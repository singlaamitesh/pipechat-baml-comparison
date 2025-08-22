"""
BAML agent implementation using structured prompt definitions.
This agent demonstrates the BAML approach to LLM prompting.
"""
import time
import asyncio
from typing import Dict, Any, Optional, List
from baml.client import BAMLClient   # ✅ correct
from pipecat import Pipeline
from pipecat.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.services.openai import OpenAILLMService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.agents.base import BaseAgent

from src.utils.metrics import MetricsCollector, AgentMetrics
from src.config.settings import settings
from src.tests.test_data import TestData


class BAMLFactCheckerAgent(BaseAgent):
    """
    BAML-based fact-checking agent using structured prompt definitions.
    
    This agent demonstrates the BAML approach where prompts are defined
    in separate .baml files with structured input/output definitions.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        super().__init__()
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Initialize BAML client
        try:
            self.baml_client = BAMLClient()
        except Exception as e:
            print(f"Warning: Could not initialize BAML client: {e}")
            print("Falling back to mock BAML client for demonstration")
            self.baml_client = MockBAMLClient()
    
    async def process_statement(self, statement: str) -> Dict[str, Any]:
        """
        Process a fact-checking statement using BAML prompting.
        
        Args:
            statement: The statement to fact-check
            
        Returns:
            Dictionary containing classification and explanation
        """
        start_time = self.metrics_collector.start_timer()
        
        try:
            # Use BAML to handle the prompt and response parsing
            # This is much cleaner than the vanilla approach!
            result = await self.baml_client.CheckFact(statement)
            
            response_time = self.metrics_collector.measure_latency(start_time)
            
            # BAML automatically validates the response structure
            # and provides type-safe access to the fields
            return {
                "classification": result.classification,
                "explanation": result.explanation,
                "success": True,
                "response_time": response_time,
                "tokens_used": None,  # BAML doesn't expose token usage directly
                "baml_used": True
            }
            
        except Exception as e:
            response_time = self.metrics_collector.measure_latency(start_time)
            return {
                "classification": "Uncertain",
                "explanation": f"Error processing statement: {str(e)}",
                "success": False,
                "response_time": response_time,
                "error_message": str(e),
                "baml_used": True
            }
    
    async def process_statement_detailed(self, statement: str) -> Dict[str, Any]:
        """
        Process a statement using the detailed BAML function.
        
        Args:
            statement: The statement to fact-check
            
        Returns:
            Dictionary containing classification and explanation
        """
        start_time = self.metrics_collector.start_timer()
        
        try:
            # Use the more detailed BAML function
            result = await self.baml_client.CheckFactDetailed(statement)
            
            response_time = self.metrics_collector.measure_latency(start_time)
            
            return {
                "classification": result.classification,
                "explanation": result.explanation,
                "success": True,
                "response_time": response_time,
                "tokens_used": None,
                "baml_used": True,
                "method": "detailed"
            }
            
        except Exception as e:
            response_time = self.metrics_collector.measure_latency(start_time)
            return {
                "classification": "Uncertain",
                "explanation": f"Error processing statement: {str(e)}",
                "success": False,
                "response_time": response_time,
                "error_message": str(e),
                "baml_used": True,
                "method": "detailed"
            }
    
    async def process_multiple_statements(self, statements: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple statements using BAML batch processing.
        
        Args:
            statements: List of statements to fact-check
            
        Returns:
            List of results for each statement
        """
        start_time = self.metrics_collector.start_timer()
        
        try:
            # Use BAML batch processing
            results = await self.baml_client.CheckMultipleFacts(statements)
            
            response_time = self.metrics_collector.measure_latency(start_time)
            
            # Convert BAML results to our format
            processed_results = []
            for i, result in enumerate(results):
                processed_results.append({
                    "statement": statements[i],
                    "classification": result.classification,
                    "explanation": result.explanation,
                    "success": True,
                    "response_time": response_time / len(statements),  # Approximate per statement
                    "tokens_used": None,
                    "baml_used": True,
                    "method": "batch"
                })
            
            return processed_results
            
        except Exception as e:
            response_time = self.metrics_collector.measure_latency(start_time)
            # Fall back to individual processing
            print(f"Batch processing failed, falling back to individual: {e}")
            return await self._process_statements_individually(statements)
    
    async def _process_statements_individually(self, statements: List[str]) -> List[Dict[str, Any]]:
        """Fallback method to process statements individually."""
        results = []
        for statement in statements:
            result = await self.process_statement(statement)
            results.append(result)
        return results
    
    async def run_fact_checking_session(self, test_statements: list) -> Dict[str, Any]:
        """
        Run a complete fact-checking session on multiple test statements.
        
        Args:
            test_statements: List of test statements to process
            
        Returns:
            Dictionary containing session results and metrics
        """
        session_results = []
        session_start_time = time.time()
        
        print(f"Starting BAML agent fact-checking session with {len(test_statements)} statements...")
        
        for i, test_item in enumerate(test_statements):
            statement = test_item["statement"]
            expected = test_item["expected_classification"]
            
            print(f"\nProcessing statement {i+1}/{len(test_statements)}: {statement}")
            
            # Process the statement using BAML
            result = await self.process_statement(statement)
            
            # Determine accuracy
            accuracy = False
            if result["success"]:
                accuracy = self._validate_accuracy(expected, result["classification"])
            
            # Determine handoff success (simplified - always True for this implementation)
            handoff_success = True
            
            # Create metrics entry
            metrics = AgentMetrics(
                agent_type="baml",
                statement=statement,
                latency=result["response_time"],
                accuracy=accuracy,
                handoff_success=handoff_success,
                response_time=result["response_time"],
                tokens_used=result.get("tokens_used"),
                error_message=result.get("error_message")
            )
            
            # Add to metrics collector
            self.metrics_collector.add_metrics(metrics)
            
            # Store result
            session_results.append({
                "statement": statement,
                "expected": expected,
                "actual": result.get("classification", "Unknown"),
                "explanation": result.get("explanation", ""),
                "accuracy": accuracy,
                "response_time": result["response_time"],
                "success": result["success"],
                "baml_used": result.get("baml_used", False)
            })
            
            print(f"Result: {result.get('classification', 'Unknown')} (Expected: {expected})")
            print(f"Accuracy: {'✓' if accuracy else '✗'}")
            print(f"Response time: {result['response_time']:.3f}s")
            print(f"BAML used: {'✓' if result.get('baml_used', False) else '✗'}")
            
            # Small delay between requests to avoid rate limiting
            await asyncio.sleep(0.5)
        
        session_duration = time.time() - session_start_time
        
        # Generate summary
        total_statements = len(session_results)
        successful_statements = sum(1 for r in session_results if r["success"])
        accurate_statements = sum(1 for r in session_results if r["accuracy"])
        avg_response_time = sum(r["response_time"] for r in session_results) / total_statements if total_statements > 0 else 0
        
        summary = {
            "agent_type": "baml",
            "total_statements": total_statements,
            "successful_statements": successful_statements,
            "accurate_statements": accurate_statements,
            "accuracy_rate": accurate_statements / total_statements if total_statements > 0 else 0,
            "avg_response_time": avg_response_time,
            "session_duration": session_duration,
            "results": session_results,
            "baml_advantages": [
                "Structured input/output definitions",
                "Automatic response validation",
                "Type-safe access to results",
                "Cleaner code separation",
                "Easier prompt management"
            ]
        }
        
        print(f"\n=== BAML Agent Session Summary ===")
        print(f"Total statements: {total_statements}")
        print(f"Successful: {successful_statements}")
        print(f"Accurate: {accurate_statements}")
        print(f"Accuracy rate: {summary['accuracy_rate']:.1%}")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Total session time: {session_duration:.2f}s")
        print(f"BAML advantages: {', '.join(summary['baml_advantages'][:3])}...")
        
        return summary
    
    def _validate_accuracy(self, expected: str, actual: str) -> bool:
        """
        Validate if the actual classification matches the expected one.
        
        Args:
            expected: Expected classification
            actual: Actual classification from the agent
            
        Returns:
            True if accurate, False otherwise
        """
        # Normalize both to lowercase for comparison
        expected_lower = expected.lower().strip()
        actual_lower = actual.lower().strip()
        
        # For uncertain statements, be more flexible
        if expected_lower == "uncertain":
            return actual_lower in ["uncertain", "unclear", "unknown"]
        
        return expected_lower == actual_lower
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of collected metrics."""
        return self.metrics_collector.calculate_averages("baml")
    
    def save_metrics(self, filename: Optional[str] = None) -> str:
        """Save collected metrics to file."""
        return self.metrics_collector.save_metrics(filename)
    
    def export_metrics_to_csv(self, filename: Optional[str] = None) -> str:
        """Export metrics to CSV format."""
        return self.metrics_collector.export_to_csv(filename)


class MockBAMLClient:
    """
    Mock BAML client for demonstration purposes when BAML is not available.
    This simulates the BAML behavior for testing and comparison.
    """
    
    async def CheckFact(self, statement: str):
        """Mock implementation of the CheckFact function."""
        # Simulate BAML's structured output
        class MockResult:
            def __init__(self, classification: str, explanation: str):
                self.classification = classification
                self.explanation = explanation
        
        # Simple mock logic for demonstration
        if "true" in statement.lower() or "correct" in statement.lower():
            return MockResult("True", "Statement appears to be factually correct.")
        elif "false" in statement.lower() or "incorrect" in statement.lower():
            return MockResult("False", "Statement appears to be factually incorrect.")
        else:
            return MockResult("Uncertain", "Statement requires further verification.")
    
    async def CheckFactDetailed(self, statement: str):
        """Mock implementation of the CheckFactDetailed function."""
        return await self.CheckFact(statement)
    
    async def CheckMultipleFacts(self, statements: List[str]):
        """Mock implementation of the CheckMultipleFacts function."""
        results = []
        for statement in statements:
            result = await self.CheckFact(statement)
            results.append(result)
        return results


# Example usage and testing
async def main():
    """Example usage of the BAML agent."""
    from src.tests.test_data import TestData
    
    # Initialize agent
    agent = BAMLFactCheckerAgent()
    
    # Get test data
    test_statements = TestData.get_fact_checking_statements()[:5]  # Test with first 5
    
    # Run session
    results = await agent.run_fact_checking_session(test_statements)
    
    # Save metrics
    metrics_file = agent.save_metrics()
    print(f"\nMetrics saved to: {metrics_file}")
    
    # Export to CSV
    csv_file = agent.export_metrics_to_csv()
    print(f"Metrics exported to CSV: {csv_file}")


if __name__ == "__main__":
    asyncio.run(main())
