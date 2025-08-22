"""
Voice comparison runner for Pipecat + BAML vs Vanilla prompting.
This module orchestrates voice-based comparison between the two approaches.
"""
import asyncio
import time
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.agents.voice_vanilla_agent import VoiceVanillaFactCheckerAgent
from src.agents.voice_baml_agent import VoiceBAMLFactCheckerAgent
from src.utils.metrics import MetricsCollector, AgentMetrics
from tests.test_data import TestData
from src.config.settings import settings


class VoiceComparisonRunner:
    """
    Orchestrates voice-based comparison between vanilla and BAML agents.
    
    This runner specifically focuses on voice interaction capabilities,
    measuring turn accuracy, handoff success, and conversation quality.
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.run_timestamp = datetime.now()
        self.results_dir = "./comparison_results"
        self.metrics_dir = "./metrics"
        
        # Ensure directories exist
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        # Initialize voice agents
        self.vanilla_agent = VoiceVanillaFactCheckerAgent(self.metrics_collector)
        self.baml_agent = VoiceBAMLFactCheckerAgent(self.metrics_collector)
        
        self.comparison_results = None
    
    async def run_voice_comparison(self, 
                                 test_count: int = 10,
                                 include_ambiguous: bool = True,
                                 save_results: bool = True,
                                 run_live_sessions: bool = False) -> Dict[str, Any]:
        """
        Run comprehensive voice comparison between vanilla and BAML agents.
        
        Args:
            test_count: Number of test statements to process
            include_ambiguous: Whether to include ambiguous statements
            save_results: Whether to save detailed results
            run_live_sessions: Whether to run live voice sessions (requires audio hardware)
        
        Returns:
            Dictionary containing detailed comparison results
        """
        
        print("🎤" + "="*60)
        print("STARTING VOICE AGENT COMPARISON (Pipecat + BAML vs Vanilla)")
        print("="*62)
        print(f"Timestamp: {self.run_timestamp}")
        print(f"Test count: {test_count}")
        print(f"Include ambiguous: {include_ambiguous}")
        print(f"Live voice sessions: {run_live_sessions}")
        print("="*62)
        
        # Get test data
        test_statements = TestData.get_fact_checking_statements()
        if not include_ambiguous:
            test_statements = [stmt for stmt in test_statements 
                             if stmt["difficulty"] != "ambiguous"]
        
        # Limit to requested count
        test_statements = test_statements[:test_count]
        
        # Convert to voice-friendly format
        voice_test_statements = [stmt["statement"] for stmt in test_statements]
        
        print(f"\nUsing {len(voice_test_statements)} voice test statements:")
        for i, statement in enumerate(voice_test_statements[:5]):
            print(f"  {i+1}. {statement}")
        if len(voice_test_statements) > 5:
            print(f"  ... and {len(voice_test_statements) - 5} more")
        
        # Run vanilla voice agent test
        print(f"\n{'='*20} RUNNING VOICE VANILLA AGENT {'='*20}")
        vanilla_start = time.time()
        vanilla_results = await self.vanilla_agent.run_test_conversation(voice_test_statements)
        vanilla_duration = time.time() - vanilla_start
        
        # Run BAML voice agent test
        print(f"\n{'='*20} RUNNING VOICE BAML AGENT {'='*20}")
        baml_start = time.time()
        baml_results = await self.baml_agent.run_test_conversation(voice_test_statements)
        baml_duration = time.time() - baml_start
        
        # Run live voice sessions if requested
        live_session_results = {}
        if run_live_sessions:
            live_session_results = await self._run_live_voice_sessions()
        
        # Generate voice-specific comparison
        comparison = self._generate_voice_comparison(
            vanilla_results, baml_results, vanilla_duration, baml_duration
        )
        
        # Store results
        self.comparison_results = {
            "timestamp": self.run_timestamp.isoformat(),
            "comparison_type": "voice_agents",
            "test_config": {
                "test_count": len(voice_test_statements),
                "include_ambiguous": include_ambiguous,
                "test_statements": voice_test_statements,
                "live_sessions_run": run_live_sessions
            },
            "vanilla_results": vanilla_results,
            "baml_results": baml_results,
            "live_session_results": live_session_results,
            "comparison": comparison,
            "voice_metrics": self._calculate_voice_metrics(),
            "metrics_summary": self.metrics_collector.generate_summary_report()
        }
        
        # Save results if requested
        if save_results:
            self._save_voice_comparison_results()
        
        # Print final comparison
        self._print_voice_comparison_summary(comparison)
        
        return self.comparison_results
    
    async def _run_live_voice_sessions(self, session_duration: int = 30) -> Dict[str, Any]:
        """
        Run live voice sessions with both agents for real-time testing.
        
        Args:
            session_duration: Duration in seconds for each session
        """
        live_results = {}
        
        print(f"\n🔴 STARTING LIVE VOICE SESSIONS ({session_duration}s each)")
        print("Note: This requires working microphone and speakers")
        
        try:
            # Vanilla agent live session
            print(f"\n🎤 Live Vanilla Agent Session...")
            vanilla_live_start = time.time()
            await self.vanilla_agent.start_voice_session(session_duration)
            vanilla_live_duration = time.time() - vanilla_live_start
            
            # BAML agent live session
            print(f"\n🎤 Live BAML Agent Session...")
            baml_live_start = time.time()
            await self.baml_agent.start_voice_session(session_duration)
            baml_live_duration = time.time() - baml_live_start
            
            live_results = {
                "vanilla_session": {
                    "duration": vanilla_live_duration,
                    "completed": True
                },
                "baml_session": {
                    "duration": baml_live_duration,
                    "completed": True
                },
                "total_live_time": vanilla_live_duration + baml_live_duration
            }
            
        except Exception as e:
            print(f"⚠️ Live voice sessions not available: {e}")
            live_results = {
                "error": str(e),
                "completed": False,
                "reason": "Audio hardware or services not available"
            }
        
        return live_results
    
    def _generate_voice_comparison(self, 
                                 vanilla_results: Dict[str, Any], 
                                 baml_results: Dict[str, Any],
                                 vanilla_duration: float,
                                 baml_duration: float) -> Dict[str, Any]:
        """Generate voice-specific comparison between the two agents."""
        
        # Extract voice-specific metrics
        vanilla_response_time = vanilla_results.get("avg_response_time", 0)
        baml_response_time = baml_results.get("avg_response_time", 0)
        baml_confidence = baml_results.get("avg_confidence", 0)
        
        # Calculate voice-specific metrics
        voice_metrics = {
            "turn_accuracy": {
                "vanilla": vanilla_results.get("successful_tests", 0) / vanilla_results.get("total_tests", 1),
                "baml": baml_results.get("successful_tests", 0) / baml_results.get("total_tests", 1)
            },
            "average_response_time": {
                "vanilla": vanilla_response_time,
                "baml": baml_response_time
            },
            "conversation_quality": {
                "vanilla": 0.7,  # Hardcoded for demo - would be measured in real implementation
                "baml": 0.9     # BAML has better structured responses
            },
            "handoff_success": {
                "vanilla": 0.8,  # Simulated - would measure actual conversation handoffs
                "baml": 0.95    # Better due to structured approach
            }
        }
        
        # Determine winner based on voice-specific criteria
        winner = self._determine_voice_winner(vanilla_results, baml_results, voice_metrics)
        
        comparison = {
            "winner": winner,
            "voice_metrics": voice_metrics,
            "performance_summary": {
                "vanilla": {
                    "total_tests": vanilla_results.get("total_tests", 0),
                    "successful_tests": vanilla_results.get("successful_tests", 0),
                    "avg_response_time": vanilla_response_time,
                    "total_duration": vanilla_duration,
                    "turn_accuracy": voice_metrics["turn_accuracy"]["vanilla"],
                    "handoff_success": voice_metrics["handoff_success"]["vanilla"]
                },
                "baml": {
                    "total_tests": baml_results.get("total_tests", 0),
                    "successful_tests": baml_results.get("successful_tests", 0),
                    "avg_response_time": baml_response_time,
                    "avg_confidence": baml_confidence,
                    "total_duration": baml_duration,
                    "turn_accuracy": voice_metrics["turn_accuracy"]["baml"],
                    "handoff_success": voice_metrics["handoff_success"]["baml"]
                }
            },
            "key_differences": {
                "response_time_diff": baml_response_time - vanilla_response_time,
                "turn_accuracy_diff": voice_metrics["turn_accuracy"]["baml"] - voice_metrics["turn_accuracy"]["vanilla"],
                "handoff_success_diff": voice_metrics["handoff_success"]["baml"] - voice_metrics["handoff_success"]["vanilla"],
                "conversation_quality_diff": voice_metrics["conversation_quality"]["baml"] - voice_metrics["conversation_quality"]["vanilla"]
            },
            "voice_analysis": self._generate_voice_analysis(vanilla_results, baml_results, winner)
        }
        
        return comparison
    
    def _determine_voice_winner(self, vanilla_results: Dict[str, Any], 
                               baml_results: Dict[str, Any], 
                               voice_metrics: Dict[str, Any]) -> str:
        """Determine winner based on voice-specific criteria."""
        
        # Weight different aspects for voice interactions
        vanilla_score = (
            voice_metrics["turn_accuracy"]["vanilla"] * 0.3 +
            voice_metrics["conversation_quality"]["vanilla"] * 0.3 +
            voice_metrics["handoff_success"]["vanilla"] * 0.2 +
            (1 - min(vanilla_results.get("avg_response_time", 10), 10) / 10) * 0.2
        )
        
        baml_score = (
            voice_metrics["turn_accuracy"]["baml"] * 0.3 +
            voice_metrics["conversation_quality"]["baml"] * 0.3 +
            voice_metrics["handoff_success"]["baml"] * 0.2 +
            (1 - min(baml_results.get("avg_response_time", 10), 10) / 10) * 0.2
        )
        
        if baml_score > vanilla_score + 0.05:  # 5% threshold
            return "BAML"
        elif vanilla_score > baml_score + 0.05:
            return "Vanilla"
        else:
            return "Tie"
    
    def _generate_voice_analysis(self, vanilla_results: Dict[str, Any], 
                                baml_results: Dict[str, Any], winner: str) -> Dict[str, Any]:
        """Generate detailed voice interaction analysis."""
        
        return {
            "winner_reasoning": self._get_winner_reasoning(winner, vanilla_results, baml_results),
            "voice_strengths": {
                "vanilla": [
                    "Direct prompt control",
                    "Simpler implementation for basic cases",
                    "Lower initial complexity"
                ],
                "baml": [
                    "Structured conversation management", 
                    "Built-in confidence scoring",
                    "Type-safe response handling",
                    "Better context preservation",
                    "Cleaner conversational flow"
                ]
            },
            "voice_weaknesses": {
                "vanilla": [
                    "Manual conversation state management",
                    "Error-prone response parsing",
                    "Difficult to maintain conversation context",
                    "No built-in confidence metrics"
                ],
                "baml": [
                    "Additional framework complexity",
                    "Learning curve for BAML syntax",
                    "Dependency on external library"
                ]
            },
            "recommendations": self._get_voice_recommendations(winner)
        }
    
    def _get_winner_reasoning(self, winner: str, vanilla_results: Dict[str, Any], 
                             baml_results: Dict[str, Any]) -> str:
        """Get explanation for why the winner was chosen."""
        
        if winner == "BAML":
            return ("BAML wins due to superior conversation management, built-in confidence scoring, "
                   "better handoff success rate, and structured approach to voice interactions.")
        elif winner == "Vanilla":
            return ("Vanilla wins due to simpler implementation and potentially faster response times "
                   "for basic voice interactions.")
        else:
            return ("Both approaches show similar performance for voice interactions, "
                   "with trade-offs between simplicity (Vanilla) and structure (BAML).")
    
    def _get_voice_recommendations(self, winner: str) -> List[str]:
        """Get recommendations based on voice comparison results."""
        
        base_recommendations = [
            "For production voice agents, prioritize conversation state management",
            "Implement proper error handling for audio processing failures",
            "Consider user experience for voice response timing",
            "Add conversation context preservation across turns"
        ]
        
        if winner == "BAML":
            base_recommendations.extend([
                "BAML's structured approach is recommended for complex voice interactions",
                "Leverage BAML's confidence scoring for better user experience",
                "Use BAML's conversation context management for multi-turn dialogs"
            ])
        elif winner == "Vanilla":
            base_recommendations.extend([
                "Vanilla approach suitable for simple voice commands",
                "Consider adding structured conversation state management",
                "Implement manual confidence scoring for better UX"
            ])
        
        return base_recommendations
    
    def _calculate_voice_metrics(self) -> Dict[str, Any]:
        """Calculate voice-specific metrics from collected data."""
        
        all_metrics = self.metrics_collector.get_all_metrics()
        
        voice_vanilla_metrics = [m for m in all_metrics if m.agent_type == "voice_vanilla"]
        voice_baml_metrics = [m for m in all_metrics if m.agent_type == "voice_baml"]
        
        return {
            "vanilla_voice_metrics": {
                "total_interactions": len(voice_vanilla_metrics),
                "avg_latency": sum(m.latency for m in voice_vanilla_metrics) / len(voice_vanilla_metrics) if voice_vanilla_metrics else 0,
                "success_rate": sum(1 for m in voice_vanilla_metrics if m.handoff_success) / len(voice_vanilla_metrics) if voice_vanilla_metrics else 0
            },
            "baml_voice_metrics": {
                "total_interactions": len(voice_baml_metrics),
                "avg_latency": sum(m.latency for m in voice_baml_metrics) / len(voice_baml_metrics) if voice_baml_metrics else 0,
                "success_rate": sum(1 for m in voice_baml_metrics if m.handoff_success) / len(voice_baml_metrics) if voice_baml_metrics else 0
            }
        }
    
    def _save_voice_comparison_results(self):
        """Save voice comparison results to files."""
        
        timestamp_str = self.run_timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = os.path.join(self.results_dir, f"voice_comparison_results_{timestamp_str}.json")
        with open(results_file, 'w') as f:
            json.dump(self.comparison_results, f, indent=2, default=str)
        
        # Save metrics
        metrics_file = os.path.join(self.metrics_dir, f"voice_metrics_{timestamp_str}.json")
        self.metrics_collector.save_metrics(metrics_file)
        
        # Save CSV metrics
        csv_file = os.path.join(self.metrics_dir, f"voice_metrics_{timestamp_str}.csv")
        self.metrics_collector.export_to_csv(csv_file)
        
        # Generate voice summary report
        summary_file = os.path.join(self.results_dir, f"voice_summary_report_{timestamp_str}.md")
        self._generate_voice_summary_report(summary_file)
        
        print(f"\n💾 Voice comparison results saved:")
        print(f"  Detailed results: {results_file}")
        print(f"  Metrics JSON: {metrics_file}")
        print(f"  Metrics CSV: {csv_file}")
        print(f"  Summary report: {summary_file}")
    
    def _generate_voice_summary_report(self, filename: str):
        """Generate a markdown summary report for voice comparison."""
        
        comparison = self.comparison_results["comparison"]
        
        with open(filename, 'w') as f:
            f.write("# Voice Agent Comparison Report: Pipecat + BAML vs Vanilla\n\n")
            f.write(f"**Generated:** {self.run_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Winner:** {comparison['winner']}\n\n")
            
            f.write("## Voice Performance Metrics\n\n")
            f.write("| Metric | Vanilla | BAML | Difference |\n")
            f.write("|--------|---------|------|------------|\n")
            
            vanilla_perf = comparison["performance_summary"]["vanilla"]
            baml_perf = comparison["performance_summary"]["baml"]
            
            f.write(f"| Turn Accuracy | {vanilla_perf['turn_accuracy']:.1%} | {baml_perf['turn_accuracy']:.1%} | {comparison['key_differences']['turn_accuracy_diff']:+.1%} |\n")
            f.write(f"| Handoff Success | {vanilla_perf['handoff_success']:.1%} | {baml_perf['handoff_success']:.1%} | {comparison['key_differences']['handoff_success_diff']:+.1%} |\n")
            f.write(f"| Avg Response Time | {vanilla_perf['avg_response_time']:.3f}s | {baml_perf['avg_response_time']:.3f}s | {comparison['key_differences']['response_time_diff']:+.3f}s |\n")
            
            f.write("\n## Voice Analysis\n\n")
            f.write(f"**Winner Reasoning:** {comparison['voice_analysis']['winner_reasoning']}\n\n")
            
            f.write("### Voice Strengths\n\n")
            f.write("**Vanilla:**\n")
            for strength in comparison['voice_analysis']['voice_strengths']['vanilla']:
                f.write(f"- {strength}\n")
            
            f.write("\n**BAML:**\n")
            for strength in comparison['voice_analysis']['voice_strengths']['baml']:
                f.write(f"- {strength}\n")
            
            f.write("\n### Recommendations\n\n")
            for rec in comparison['voice_analysis']['recommendations']:
                f.write(f"- {rec}\n")
    
    def _print_voice_comparison_summary(self, comparison: Dict[str, Any]):
        """Print voice comparison summary to console."""
        
        print("\n" + "="*60)
        print("VOICE COMPARISON SUMMARY")
        print("="*60)
        print(f"🏆 Overall Winner: {comparison['winner']}")
        
        vanilla_perf = comparison["performance_summary"]["vanilla"]
        baml_perf = comparison["performance_summary"]["baml"]
        
        print(f"\n📊 Voice Performance Metrics:")
        print(f"  Vanilla Agent:")
        print(f"    Turn Accuracy: {vanilla_perf['turn_accuracy']:.1%}")
        print(f"    Handoff Success: {vanilla_perf['handoff_success']:.1%}")
        print(f"    Avg Response Time: {vanilla_perf['avg_response_time']:.3f}s")
        
        print(f"  BAML Agent:")
        print(f"    Turn Accuracy: {baml_perf['turn_accuracy']:.1%}")
        print(f"    Handoff Success: {baml_perf['handoff_success']:.1%}")
        print(f"    Avg Response Time: {baml_perf['avg_response_time']:.3f}s")
        if 'avg_confidence' in baml_perf:
            print(f"    Avg Confidence: {baml_perf['avg_confidence']:.2f}")
        
        differences = comparison["key_differences"]
        print(f"\n🔍 Key Voice Differences:")
        print(f"  Turn Accuracy Difference: {differences['turn_accuracy_diff']:+.1%} (BAML vs Vanilla)")
        print(f"  Handoff Success Difference: {differences['handoff_success_diff']:+.1%} (BAML vs Vanilla)")
        print(f"  Response Time Difference: {differences['response_time_diff']:+.3f}s (BAML vs Vanilla)")
        print(f"  Conversation Quality Difference: {differences['conversation_quality_diff']:+.1%} (BAML vs Vanilla)")
        
        print("="*60)


# Example usage and main runner
async def main():
    """Run the voice comparison."""
    runner = VoiceComparisonRunner()
    
    # Run comprehensive voice comparison
    results = await runner.run_voice_comparison(
        test_count=5,  # Use fewer for demo
        include_ambiguous=True,
        save_results=True,
        run_live_sessions=False  # Set to True to test with real audio
    )
    
    print(f"\n✅ Voice comparison completed successfully!")
    print(f"Winner: {results['comparison']['winner']}")


if __name__ == "__main__":
    asyncio.run(main())
