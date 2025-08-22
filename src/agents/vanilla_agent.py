"""
Vanilla agent implementation using hardcoded string prompts.
This agent demonstrates the traditional approach to LLM prompting.
"""
import time
import asyncio
from typing import Dict, Any, Optional, List

# Simplified base agent for demonstration
class BaseAgent:
    """Simplified base agent for demonstration purposes."""
    
    def __init__(self):
        self.name = self.__class__.__name__

from src.utils.metrics import MetricsCollector, AgentMetrics
from src.config.settings import settings
from tests.test_data import TestData


class VanillaFactCheckerAgent(BaseAgent):
    """
    Vanilla fact-checking agent using hardcoded string prompts.
    
    This agent demonstrates the traditional approach where prompts are
    hardcoded as strings directly in the application code.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        super().__init__()
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Initialize LLM client based on provider
        self.llm_provider = settings.LLM_PROVIDER.lower()
        
        if self.llm_provider == "openai":
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                self.model = settings.DEFAULT_MODEL_OPENAI
                print(f"Using OpenAI model: {self.model}")
            except ImportError:
                print("OpenAI package not available, using mock client")
                self.client = MockOpenAIClient()
                self.model = "gpt-4o-mini"
        elif self.llm_provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.client = genai.GenerativeModel(settings.DEFAULT_MODEL_GEMINI)
                self.model = settings.DEFAULT_MODEL_GEMINI
                print(f"Using Google Gemini model: {self.model}")
            except ImportError:
                print("Google Generative AI package not available, using mock client")
                self.client = MockGeminiClient()
                self.model = "gemini-1.5-flash"
        else:
            print(f"Unknown LLM provider: {self.llm_provider}, using mock client")
            self.client = MockOpenAIClient()
            self.model = "mock-model"
    
    async def process_statement(self, statement: str) -> Dict[str, Any]:
        """
        Process a fact-checking statement using vanilla prompting.
        
        Args:
            statement: The statement to fact-check
            
        Returns:
            Dictionary containing classification and explanation
        """
        start_time = self.metrics_collector.start_timer()
        
        try:
            # This is the vanilla approach - hardcoded prompt strings
            # scattered throughout the code, making it harder to maintain
            prompt = f"""
            Please fact-check the following statement and provide a classification.
            
            Statement: "{statement}"
            
            Please respond with:
            1. Classification: True, False, or Uncertain
            2. Explanation: A brief explanation for your classification
            
            Format your response as:
            Classification: [True/False/Uncertain]
            Explanation: [Your explanation here]
            """
            
            # Make API call to LLM
            if self.llm_provider == "openai":
                response = await self._call_openai(prompt)
            elif self.llm_provider == "gemini":
                response = await self._call_gemini(prompt)
            else:
                response = await self._call_mock(prompt)
            
            response_time = self.metrics_collector.measure_latency(start_time)
            
            # Parse the response manually (this is error-prone!)
            classification, explanation = self._parse_vanilla_response(response)
            
            return {
                "classification": classification,
                "explanation": explanation,
                "success": True,
                "response_time": response_time,
                "tokens_used": None,  # Not available in this implementation
                "baml_used": False,
                "raw_response": response
            }
            
        except Exception as e:
            response_time = self.metrics_collector.measure_latency(start_time)
            return {
                "classification": "Uncertain",
                "explanation": f"Error processing statement: {str(e)}",
                "success": False,
                "response_time": response_time,
                "error_message": str(e),
                "baml_used": False
            }
    
    async def _call_openai(self, prompt: str) -> str:
        """Make API call to OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return f"Error: {str(e)}"
    
    async def _call_gemini(self, prompt: str) -> str:
        """Make API call to Google Gemini."""
        try:
            response = await self.client.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini API error: {e}")
            return f"Error: {str(e)}"
    
    async def _call_mock(self, prompt: str) -> str:
        """Mock API call for testing."""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Simple mock logic
        if "true" in prompt.lower() or "correct" in prompt.lower():
            return "Classification: True\nExplanation: This statement appears to be factually correct."
        elif "false" in prompt.lower() or "incorrect" in prompt.lower():
            return "Classification: False\nExplanation: This statement appears to be factually incorrect."
        else:
            return "Classification: Uncertain\nExplanation: Unable to determine factual accuracy."
    
    def _parse_vanilla_response(self, response: str) -> tuple:
        """
        Parse the vanilla LLM response manually.
        
        This is one of the main pain points of vanilla prompting:
        - No structured output validation
        - Manual parsing required
        - Error-prone and brittle
        - Hard to maintain
        """
        try:
            lines = response.split('\n')
            classification = "Uncertain"
            explanation = "No explanation provided"
            
            for line in lines:
                line = line.strip()
                if line.startswith("Classification:"):
                    classification = line.replace("Classification:", "").strip()
                elif line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
            
            # Validate classification
            if classification.lower() not in ["true", "false", "uncertain"]:
                classification = "Uncertain"
                explanation = f"Invalid classification format: {classification}. {explanation}"
            
            return classification, explanation
            
        except Exception as e:
            return "Uncertain", f"Error parsing response: {str(e)}. Raw response: {response[:100]}..."
    
    async def process_multiple_statements(self, statements: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple statements using vanilla prompting.
        
        Args:
            statements: List of statements to fact-check
            
        Returns:
            List of results for each statement
        """
        results = []
        for statement in statements:
            result = await self.process_statement(statement)
            results.append(result)
        return results

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's performance metrics."""
        return self.metrics_collector.get_summary()

    def export_metrics(self, filename: str = None) -> str:
        """Export metrics to CSV file."""
        if filename is None:
            filename = f"vanilla_agent_metrics_{int(time.time())}.csv"
        return self.metrics_collector.export_to_csv(filename)

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
        
        print(f"Starting vanilla agent fact-checking session with {len(test_statements)} statements...")
        
        for i, test_item in enumerate(test_statements):
            statement = test_item["statement"]
            expected = test_item["expected_classification"]
            
            print(f"\nProcessing statement {i+1}/{len(test_statements)}: {statement}")
            
            # Process the statement using vanilla prompting
            result = await self.process_statement(statement)
            
            # Determine accuracy
            accuracy = False
            if result["success"]:
                accuracy = self._validate_accuracy(expected, result["classification"])
            
            # Determine handoff success (simplified - always True for this implementation)
            handoff_success = True
            
            # Create metrics entry
            metrics = AgentMetrics(
                agent_type="vanilla",
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
            "agent_type": "vanilla",
            "total_statements": total_statements,
            "successful_statements": successful_statements,
            "accurate_statements": accurate_statements,
            "accuracy_rate": accurate_statements / total_statements if total_statements > 0 else 0,
            "avg_response_time": avg_response_time,
            "session_duration": session_duration,
            "results": session_results,
            "vanilla_disadvantages": [
                "Hardcoded prompt strings throughout code",
                "Manual response parsing required",
                "No structured output validation",
                "Difficult to maintain and update prompts",
                "Error-prone response handling"
            ]
        }
        
        print(f"\n=== Vanilla Agent Session Summary ===")
        print(f"Total statements: {total_statements}")
        print(f"Successful: {successful_statements}")
        print(f"Accurate: {accurate_statements}")
        print(f"Accuracy rate: {summary['accuracy_rate']:.1%}")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Total session time: {session_duration:.2f}s")
        print(f"Vanilla disadvantages: {', '.join(summary['vanilla_disadvantages'][:3])}...")
        
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


# Mock clients for testing without API keys
class MockOpenAIClient:
    """Mock OpenAI client for testing."""
    
    class Chat:
        class Completions:
            async def create(self, **kwargs):
                class MockResponse:
                    class MockChoice:
                        class MockMessage:
                            content = "Classification: True\nExplanation: Mock response for testing."
                        message = MockMessage()
                    choices = [MockChoice()]
                return MockResponse()
        completions = Completions()

class MockGeminiClient:
    """Mock Gemini client for testing."""
    
    async def generate_content(self, prompt: str):
        class MockResponse:
            text = "Classification: True\nExplanation: Mock response for testing."
        return MockResponse()


# Example usage and testing
if __name__ == "__main__":
    async def test_agent():
        """Test the vanilla agent with sample statements."""
        agent = VanillaFactCheckerAgent()
        
        test_statements = [
            "The Earth is round.",
            "The sky is green.",
            "Water boils at 100 degrees Celsius."
        ]
        
        print("Testing Vanilla Agent...")
        for statement in test_statements:
            result = await agent.process_statement(statement)
            print(f"\nStatement: {statement}")
            print(f"Classification: {result['classification']}")
            print(f"Explanation: {result['explanation']}")
            print(f"Response Time: {result['response_time']:.3f}s")
    
    # Run the test
    asyncio.run(test_agent())
