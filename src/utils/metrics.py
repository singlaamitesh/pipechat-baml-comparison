"""
Metrics collection utilities for comparing vanilla vs. BAML agents.
"""
import time
import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import pandas as pd


@dataclass
class AgentMetrics:
    """Metrics for a single agent interaction."""
    agent_type: str  # "vanilla" or "baml"
    statement: str
    latency: float  # seconds
    accuracy: bool
    handoff_success: bool
    response_time: float
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class MetricsCollector:
    """Collects and manages metrics for agent comparison."""
    
    def __init__(self, save_path: str = "./metrics/"):
        self.save_path = save_path
        self.metrics: List[AgentMetrics] = []
        
        # Ensure metrics directory exists
        os.makedirs(save_path, exist_ok=True)
    
    def start_timer(self) -> float:
        """Start a timer and return the start time."""
        return time.time()
    
    def measure_latency(self, start_time: float) -> float:
        """Calculate latency from start time to now."""
        return time.time() - start_time
    
    def add_metrics(self, metrics: AgentMetrics) -> None:
        """Add a new metrics entry."""
        self.metrics.append(metrics)
    
    def get_agent_metrics(self, agent_type: str) -> List[AgentMetrics]:
        """Get all metrics for a specific agent type."""
        return [m for m in self.metrics if m.agent_type == agent_type]
    
    def calculate_averages(self, agent_type: str) -> Dict[str, float]:
        """Calculate average metrics for a specific agent type."""
        agent_metrics = self.get_agent_metrics(agent_type)
        
        if not agent_metrics:
            return {}
        
        return {
            "avg_latency": sum(m.latency for m in agent_metrics) / len(agent_metrics),
            "avg_response_time": sum(m.response_time for m in agent_metrics) / len(agent_metrics),
            "accuracy_rate": sum(m.accuracy for m in agent_metrics) / len(agent_metrics),
            "handoff_success_rate": sum(m.handoff_success for m in agent_metrics) / len(agent_metrics),
            "total_interactions": len(agent_metrics)
        }
    
    def compare_agents(self) -> Dict[str, Any]:
        """Compare performance between vanilla and BAML agents."""
        vanilla_metrics = self.calculate_averages("vanilla")
        baml_metrics = self.calculate_averages("baml")
        
        if not vanilla_metrics or not baml_metrics:
            return {"error": "Insufficient data for comparison"}
        
        comparison = {
            "vanilla": vanilla_metrics,
            "baml": baml_metrics,
            "differences": {
                "latency_diff": baml_metrics["avg_latency"] - vanilla_metrics["avg_latency"],
                "accuracy_diff": baml_metrics["accuracy_rate"] - vanilla_metrics["accuracy_rate"],
                "handoff_diff": baml_metrics["handoff_success_rate"] - vanilla_metrics["handoff_success_rate"]
            }
        }
        
        # Determine winner
        comparison["winner"] = self._determine_winner(vanilla_metrics, baml_metrics)
        
        return comparison
    
    def _determine_winner(self, vanilla: Dict[str, float], baml: Dict[str, float]) -> str:
        """Determine which agent performed better overall."""
        vanilla_score = (
            (1 - vanilla["avg_latency"] / 10) * 0.3 +  # Lower latency is better
            vanilla["accuracy_rate"] * 0.4 +            # Higher accuracy is better
            vanilla["handoff_success_rate"] * 0.3       # Higher handoff success is better
        )
        
        baml_score = (
            (1 - baml["avg_latency"] / 10) * 0.3 +
            baml["accuracy_rate"] * 0.4 +
            baml["handoff_success_rate"] * 0.3
        )
        
        if baml_score > vanilla_score:
            return "BAML"
        elif vanilla_score > baml_score:
            return "Vanilla"
        else:
            return "Tie"
    
    def save_metrics(self, filename: Optional[str] = None) -> str:
        """Save metrics to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.json"
        
        filepath = os.path.join(self.save_path, filename)
        
        # Convert metrics to dictionaries
        metrics_data = [asdict(m) for m in self.metrics]
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        return filepath
    
    def export_to_csv(self, filename: Optional[str] = None) -> str:
        """Export metrics to CSV file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics_{timestamp}.csv"
        
        filepath = os.path.join(self.save_path, filename)
        
        # Convert to DataFrame and save
        df = pd.DataFrame([asdict(m) for m in self.metrics])
        df.to_csv(filepath, index=False)
        
        return filepath
    
    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        comparison = self.compare_agents()
        
        if "error" in comparison:
            return f"Error: {comparison['error']}"
        
        report = f"""
# Agent Performance Comparison Report

## Summary
- **Winner**: {comparison['winner']}
- **Total Interactions**: {len(self.metrics)}
- **Vanilla Interactions**: {comparison['vanilla']['total_interactions']}
- **BAML Interactions**: {comparison['baml']['total_interactions']}

## Performance Metrics

### Vanilla Agent
- Average Latency: {comparison['vanilla']['avg_latency']:.3f}s
- Accuracy Rate: {comparison['vanilla']['accuracy_rate']:.1%}
- Handoff Success Rate: {comparison['vanilla']['handoff_success_rate']:.1%}

### BAML Agent
- Average Latency: {comparison['baml']['avg_latency']:.3f}s
- Accuracy Rate: {comparison['baml']['accuracy_rate']:.1%}
- Handoff Success Rate: {comparison['baml']['handoff_success_rate']:.1%}

## Key Differences
- **Latency Difference**: {comparison['differences']['latency_diff']:+.3f}s (BAML vs Vanilla)
- **Accuracy Difference**: {comparison['differences']['accuracy_diff']:+.1%} (BAML vs Vanilla)
- **Handoff Difference**: {comparison['differences']['handoff_diff']:+.1%} (BAML vs Vanilla)

## Analysis
{self._generate_analysis(comparison)}
"""
        return report
    
    def _generate_analysis(self, comparison: Dict[str, Any]) -> str:
        """Generate analysis text based on comparison results."""
        analysis = []
        
        if comparison['winner'] == 'BAML':
            analysis.append("**BAML agent performed better overall.**")
        elif comparison['winner'] == 'Vanilla':
            analysis.append("**Vanilla agent performed better overall.**")
        else:
            analysis.append("**Both agents performed similarly.**")
        
        # Latency analysis
        if abs(comparison['differences']['latency_diff']) > 0.1:
            if comparison['differences']['latency_diff'] > 0:
                analysis.append(f"Vanilla agent was {comparison['differences']['latency_diff']:.3f}s faster.")
            else:
                analysis.append(f"BAML agent was {abs(comparison['differences']['latency_diff']):.3f}s faster.")
        
        # Accuracy analysis
        if abs(comparison['differences']['accuracy_diff']) > 0.05:
            if comparison['differences']['accuracy_diff'] > 0:
                analysis.append(f"BAML agent was {comparison['differences']['accuracy_diff']:.1%} more accurate.")
            else:
                analysis.append(f"Vanilla agent was {abs(comparison['differences']['accuracy_diff']):.1%} more accurate.")
        
        return "\n".join(analysis)
