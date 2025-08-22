"""
Comparison runner for Pipechat + BAML vs Vanilla prompting.
This module orchestrates the comparison between the two approaches.
"""
import asyncio
import time
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.agents.vanilla_agent import VanillaFactCheckerAgent
from src.agents.baml_agent import BAMLFactCheckerAgent
from src.utils.metrics import MetricsCollector, AgentMetrics
from tests.test_data import TestData
from src.config.settings import settings


class ComparisonRunner:
    """
    Automated comparison runner for vanilla vs. BAML agents.
    
    This class orchestrates the comparison process by:
    1. Running both agents on identical test data
    2. Collecting comprehensive metrics
    3. Generating detailed comparison reports
    4. Saving results for analysis
    """
    
    def __init__(self, output_dir: str = "./comparison_results/"):
        self.output_dir = output_dir
        self.metrics_collector = MetricsCollector()
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize agents with shared metrics collector
        self.vanilla_agent = VanillaFactCheckerAgent(self.metrics_collector)
        self.baml_agent = BAMLFactCheckerAgent(self.metrics_collector)
        
        # Comparison results
        self.comparison_results = {}
        self.run_timestamp = None
    
    async def run_comparison(self, 
                           test_count: int = 10, 
                           include_ambiguous: bool = True,
                           save_results: bool = True) -> Dict[str, Any]:
        """
        Run the complete comparison between vanilla and BAML agents.
        
        Args:
            test_count: Number of test statements to use
            include_ambiguous: Whether to include ambiguous statements
            save_results: Whether to save results to files
            
        Returns:
            Dictionary containing complete comparison results
        """
        self.run_timestamp = datetime.now()
        
        print("=" * 60)
        print("STARTING VANILLA vs BAML AGENT COMPARISON")
        print("=" * 60)
        print(f"Timestamp: {self.run_timestamp}")
        print(f"Test count: {test_count}")
        print(f"Include ambiguous: {include_ambiguous}")
        print("=" * 60)
        
        # Get test data
        if include_ambiguous:
            test_statements = TestData.get_all_test_statements()
        else:
            test_statements = TestData.get_fact_checking_statements()
        
        # Limit to requested count
        test_statements = test_statements[:test_count]
        
        print(f"\nUsing {len(test_statements)} test statements:")
        for i, item in enumerate(test_statements[:5]):
            print(f"  {i+1}. {item['statement']} -> {item['expected_classification']}")
        if len(test_statements) > 5:
            print(f"  ... and {len(test_statements) - 5} more")
        
        # Run vanilla agent
        print(f"\n{'='*20} RUNNING VANILLA AGENT {'='*20}")
        vanilla_start = time.time()
        vanilla_results = await self.vanilla_agent.run_fact_checking_session(test_statements)
        vanilla_duration = time.time() - vanilla_start
        
        # Run BAML agent
        print(f"\n{'='*20} RUNNING BAML AGENT {'='*20}")
        baml_start = time.time()
        baml_results = await self.baml_agent.run_fact_checking_session(test_statements)
        baml_duration = time.time() - baml_start
        
        # Generate comparison
        comparison = self._generate_comparison(vanilla_results, baml_results, vanilla_duration, baml_duration)
        
        # Store results
        self.comparison_results = {
            "timestamp": self.run_timestamp.isoformat(),
            "test_config": {
                "test_count": len(test_statements),
                "include_ambiguous": include_ambiguous,
                "test_statements": test_statements
            },
            "vanilla_results": vanilla_results,
            "baml_results": baml_results,
            "comparison": comparison,
            "metrics_summary": self.metrics_collector.generate_summary_report()
        }
        
        # Save results if requested
        if save_results:
            self._save_comparison_results()
        
        # Print final comparison
        self._print_comparison_summary(comparison)
        
        return self.comparison_results
    
    def _generate_comparison(self, 
                           vanilla_results: Dict[str, Any], 
                           baml_results: Dict[str, Any],
                           vanilla_duration: float,
                           baml_duration: float) -> Dict[str, Any]:
        """Generate detailed comparison between the two agents."""
        
        # Calculate key metrics
        vanilla_accuracy = vanilla_results.get("accuracy_rate", 0)
        baml_accuracy = baml_results.get("accuracy_rate", 0)
        vanilla_response_time = vanilla_results.get("avg_response_time", 0)
        baml_response_time = baml_results.get("avg_response_time", 0)
        
        # Determine winner
        winner = self._determine_winner(vanilla_results, baml_results)
        
        comparison = {
            "winner": winner,
            "performance_metrics": {
                "vanilla": {
                    "accuracy_rate": vanilla_accuracy,
                    "avg_response_time": vanilla_response_time,
                    "total_duration": vanilla_duration,
                    "successful_statements": vanilla_results.get("successful_statements", 0),
                    "total_statements": vanilla_results.get("total_statements", 0)
                },
                "baml": {
                    "accuracy_rate": baml_accuracy,
                    "avg_response_time": baml_response_time,
                    "total_duration": baml_duration,
                    "successful_statements": baml_results.get("successful_statements", 0),
                    "total_statements": baml_results.get("total_statements", 0)
                }
            },
            "differences": {
                "accuracy_diff": baml_accuracy - vanilla_accuracy,
                "response_time_diff": baml_response_time - vanilla_response_time,
                "duration_diff": baml_duration - vanilla_duration
            },
            "analysis": self._generate_analysis(vanilla_results, baml_results, winner)
        }
        
        return comparison
    
    def _determine_winner(self, vanilla_results: Dict[str, Any], baml_results: Dict[str, Any]) -> str:
        """Determine which agent performed better overall."""
        
        # Calculate weighted scores
        vanilla_score = (
            vanilla_results.get("accuracy_rate", 0) * 0.5 +           # Accuracy is most important
            (1 - vanilla_results.get("avg_response_time", 10) / 10) * 0.3 +  # Lower response time is better
            (vanilla_results.get("successful_statements", 0) / vanilla_results.get("total_statements", 1)) * 0.2  # Success rate
        )
        
        baml_score = (
            baml_results.get("accuracy_rate", 0) * 0.5 +
            (1 - baml_results.get("avg_response_time", 10) / 10) * 0.3 +
            (baml_results.get("successful_statements", 0) / baml_results.get("total_statements", 1)) * 0.2
        )
        
        if baml_score > vanilla_score:
            return "BAML"
        elif vanilla_score > baml_score:
            return "Vanilla"
        else:
            return "Tie"
    
    def _generate_analysis(self, vanilla_results: Dict[str, Any], baml_results: Dict[str, Any], winner: str) -> str:
        """Generate detailed analysis of the comparison results."""
        
        analysis = []
        
        # Overall winner
        analysis.append(f"**Overall Winner: {winner}**")
        analysis.append("")
        
        # Accuracy analysis
        vanilla_acc = vanilla_results.get("accuracy_rate", 0)
        baml_acc = baml_results.get("accuracy_rate", 0)
        acc_diff = baml_acc - vanilla_acc
        
        analysis.append("## Accuracy Analysis")
        if abs(acc_diff) > 0.05:
            if acc_diff > 0:
                analysis.append(f"- BAML agent was {acc_diff:.1%} more accurate")
                analysis.append(f"- Vanilla accuracy: {vanilla_acc:.1%}")
                analysis.append(f"- BAML accuracy: {baml_acc:.1%}")
            else:
                analysis.append(f"- Vanilla agent was {abs(acc_diff):.1%} more accurate")
                analysis.append(f"- Vanilla accuracy: {vanilla_acc:.1%}")
                analysis.append(f"- BAML accuracy: {baml_acc:.1%}")
        else:
            analysis.append("- Both agents achieved similar accuracy levels")
            analysis.append(f"- Vanilla accuracy: {vanilla_acc:.1%}")
            analysis.append(f"- BAML accuracy: {baml_acc:.1%}")
        
        # Response time analysis
        vanilla_rt = vanilla_results.get("avg_response_time", 0)
        baml_rt = baml_results.get("avg_response_time", 0)
        rt_diff = baml_rt - vanilla_rt
        
        analysis.append("\n## Response Time Analysis")
        if abs(rt_diff) > 0.1:
            if rt_diff > 0:
                analysis.append(f"- Vanilla agent was {rt_diff:.3f}s faster")
                analysis.append(f"- Vanilla avg response time: {vanilla_rt:.3f}s")
                analysis.append(f"- BAML avg response time: {baml_rt:.3f}s")
            else:
                analysis.append(f"- BAML agent was {abs(rt_diff):.3f}s faster")
                analysis.append(f"- Vanilla avg response time: {vanilla_rt:.3f}s")
                analysis.append(f"- BAML avg response time: {baml_rt:.3f}s")
        else:
            analysis.append("- Both agents had similar response times")
            analysis.append(f"- Vanilla avg response time: {vanilla_rt:.3f}s")
            analysis.append(f"- BAML avg response time: {baml_rt:.3f}s")
        
        # Code quality analysis
        analysis.append("\n## Code Quality Analysis")
        analysis.append("### Vanilla Agent")
        analysis.append("- Prompts defined as hardcoded strings in code")
        analysis.append("- Manual JSON parsing and validation")
        analysis.append("- Less maintainable prompt management")
        analysis.append("- More error-prone response handling")
        
        analysis.append("\n### BAML Agent")
        analysis.append("- Prompts defined in structured .baml files")
        analysis.append("- Automatic response validation and parsing")
        analysis.append("- Better separation of concerns")
        analysis.append("- Type-safe access to results")
        
        # Recommendations
        analysis.append("\n## Recommendations")
        if winner == "BAML":
            analysis.append("- **Use BAML for production systems** requiring reliable, structured responses")
            analysis.append("- BAML provides better maintainability and developer experience")
            analysis.append("- Consider BAML for team collaboration on prompt engineering")
        elif winner == "Vanilla":
            analysis.append("- **Vanilla approach may be sufficient for simple, one-off projects**")
            analysis.append("- Consider BAML for projects requiring structured outputs")
            analysis.append("- BAML provides better long-term maintainability")
        else:
            analysis.append("- **Both approaches perform similarly for this task**")
            analysis.append("- Choose based on project requirements and team preferences")
            analysis.append("- BAML provides better structure for complex projects")
        
        return "\n".join(analysis)
    
    def _print_comparison_summary(self, comparison: Dict[str, Any]):
        """Print a summary of the comparison results."""
        
        print("\n" + "=" * 60)
        print("COMPARISON SUMMARY")
        print("=" * 60)
        
        winner = comparison["winner"]
        print(f"🏆 Overall Winner: {winner}")
        
        # Performance metrics
        vanilla_metrics = comparison["performance_metrics"]["vanilla"]
        baml_metrics = comparison["performance_metrics"]["baml"]
        
        print(f"\n📊 Performance Metrics:")
        print(f"  Vanilla Agent:")
        print(f"    Accuracy: {vanilla_metrics['accuracy_rate']:.1%}")
        print(f"    Avg Response Time: {vanilla_metrics['avg_response_time']:.3f}s")
        print(f"    Total Duration: {vanilla_metrics['total_duration']:.2f}s")
        
        print(f"  BAML Agent:")
        print(f"    Accuracy: {baml_metrics['accuracy_rate']:.1%}")
        print(f"    Avg Response Time: {baml_metrics['avg_response_time']:.3f}s")
        print(f"    Total Duration: {baml_metrics['total_duration']:.2f}s")
        
        # Key differences
        differences = comparison["differences"]
        print(f"\n🔍 Key Differences:")
        print(f"  Accuracy Difference: {differences['accuracy_diff']:+.1%} (BAML vs Vanilla)")
        print(f"  Response Time Difference: {differences['response_time_diff']:+.3f}s (BAML vs Vanilla)")
        print(f"  Duration Difference: {differences['duration_diff']:+.2f}s (BAML vs Vanilla)")
        
        print("\n" + "=" * 60)
    
    def _save_comparison_results(self):
        """Save comparison results to files."""
        
        timestamp = self.run_timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = os.path.join(self.output_dir, f"comparison_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(self.comparison_results, f, indent=2)
        
        # Save metrics
        metrics_file = self.metrics_collector.save_metrics(f"metrics_{timestamp}.json")
        csv_file = self.metrics_collector.export_to_csv(f"metrics_{timestamp}.csv")
        
        # Save summary report
        summary_file = os.path.join(self.output_dir, f"summary_report_{timestamp}.md")
        with open(summary_file, 'w') as f:
            f.write(self.metrics_collector.generate_summary_report())
        
        print(f"\n💾 Results saved:")
        print(f"  Detailed results: {results_file}")
        print(f"  Metrics JSON: {metrics_file}")
        print(f"  Metrics CSV: {csv_file}")
        print(f"  Summary report: {summary_file}")
    
    def get_comparison_results(self) -> Dict[str, Any]:
        """Get the comparison results."""
        return self.comparison_results
    
    def get_metrics_collector(self) -> MetricsCollector:
        """Get the metrics collector."""
        return self.metrics_collector


# Example usage
async def main():
    """Example usage of the comparison runner."""
    
    # Initialize runner
    runner = ComparisonRunner()
    
    # Run comparison with 15 test statements
    results = await runner.run_comparison(
        test_count=15,
        include_ambiguous=True,
        save_results=True
    )
    
    print(f"\n✅ Comparison completed successfully!")
    print(f"Winner: {results['comparison']['winner']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
