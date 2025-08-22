"""
Vanilla agent implementation using hardcoded prompt strings.
This agent demonstrates the traditional approach to LLM prompting.
"""
import json
import time
import asyncio
from typing import Dict, Any, Optional

from src.utils.metrics import MetricsCollector, AgentMetrics
from src.config.settings import settings

# Provider SDKs (import lazily where possible)
try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore

try:
    import google.generativeai as genai  # type: ignore
except Exception:  # pragma: no cover
    genai = None  # type: ignore


class VanillaFactCheckerAgent:
    """
    Vanilla fact-checking agent using hardcoded prompt strings.
    Supports OpenAI and Gemini providers based on environment config.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector or MetricsCollector()
        
        # Hardcoded prompt template - this is the "vanilla" approach
        self.prompt_template = """
You are a fact-checking AI. Analyze the following statement and determine if it is True, False, or Uncertain.
Provide a one-sentence explanation for your reasoning.

Your response must be in a JSON format with two keys: "classification" and "explanation".

Statement: "{statement}"

JSON Response:
"""
        
        # Expected response format for validation
        self.expected_keys = ["classification", "explanation"]
        
        # Initialize provider client lazily
        self._provider = settings.LLM_PROVIDER
        self._model = settings.get_default_model()
        self._openai_client = None
        self._gemini_model = None
        
        if self._provider == "openai" and AsyncOpenAI and settings.OPENAI_API_KEY:
            self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        elif self._provider == "gemini" and genai and settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            self._gemini_model = genai.GenerativeModel(self._model)
        else:
            raise RuntimeError(
                f"LLM provider '{self._provider}' not properly configured. "
                "Set LLM_PROVIDER to 'gemini' with GOOGLE_API_KEY, or 'openai' with OPENAI_API_KEY."
            )
    
    async def process_statement(self, statement: str) -> Dict[str, Any]:
        """
        Process a fact-checking statement using vanilla prompting.
        """
        start_time = self.metrics_collector.start_timer()
        
        try:
            prompt = self.prompt_template.format(statement=statement)
            
            if self._provider == "openai":
                assert self._openai_client is not None
                response = await self._openai_client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": "You are a fact-checking AI that responds in JSON format."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=settings.MAX_TOKENS,
                    temperature=settings.TEMPERATURE,
                    response_format={"type": "json_object"}
                )
                response_content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if getattr(response, "usage", None) else None
            else:
                # Gemini
                assert self._gemini_model is not None
                # System instruction + prompt merged for simplicity
                gemini_prompt = (
                    "You are a fact-checking AI that responds ONLY with valid JSON.\n" + prompt
                )
                # Use generate_content; ask for JSON in prompt
                result = await self._gemini_model.generate_content_async(gemini_prompt)
                # Some SDK versions use .text, others use candidates[0].content.parts
                response_content = getattr(result, "text", None) or (
                    result.candidates[0].content.parts[0].text if getattr(result, "candidates", None) else ""
                )
                tokens_used = None
            
            response_time = self.metrics_collector.measure_latency(start_time)
            
            # Parse JSON response
            try:
                result_obj = json.loads(response_content)
                
                if not all(key in result_obj for key in self.expected_keys):
                    raise ValueError(f"Missing required keys: {self.expected_keys}")
                
                classification = str(result_obj.get("classification", "")).strip()
                explanation = str(result_obj.get("explanation", "")).strip()
                
                valid_classifications = ["True", "False", "Uncertain", "true", "false", "uncertain"]
                if classification not in valid_classifications:
                    raise ValueError(f"Invalid classification: {classification}")
                
                return {
                    "classification": classification,
                    "explanation": explanation,
                    "success": True,
                    "response_time": response_time,
                    "tokens_used": tokens_used,
                }
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse JSON response: {e}")
        
        except Exception as e:
            response_time = self.metrics_collector.measure_latency(start_time)
            return {
                "classification": "Uncertain",
                "explanation": f"Error processing statement: {str(e)}",
                "success": False,
                "response_time": response_time,
                "error_message": str(e)
            }
    
    async def run_fact_checking_session(self, test_statements: list) -> Dict[str, Any]:
        session_results = []
        session_start_time = time.time()
        
        print(f"Starting vanilla agent ({self._provider}) with {len(test_statements)} statements...")
        
        for i, test_item in enumerate(test_statements):
            statement = test_item["statement"]
            expected = test_item["expected_classification"]
            
            print(f"\nProcessing statement {i+1}/{len(test_statements)}: {statement}")
            result = await self.process_statement(statement)
            
            accuracy = False
            if result["success"]:
                accuracy = self._validate_accuracy(expected, result["classification"])
            
            metrics = AgentMetrics(
                agent_type="vanilla",
                statement=statement,
                latency=result["response_time"],
                accuracy=accuracy,
                handoff_success=True,
                response_time=result["response_time"],
                tokens_used=result.get("tokens_used"),
                error_message=result.get("error_message")
            )
            self.metrics_collector.add_metrics(metrics)
            
            session_results.append({
                "statement": statement,
                "expected": expected,
                "actual": result.get("classification", "Unknown"),
                "explanation": result.get("explanation", ""),
                "accuracy": accuracy,
                "response_time": result["response_time"],
                "success": result["success"]
            })
            
            print(f"Result: {result.get('classification', 'Unknown')} (Expected: {expected})")
            print(f"Accuracy: {'✓' if accuracy else '✗'} | Response time: {result['response_time']:.3f}s")
            await asyncio.sleep(0.3)
        
        session_duration = time.time() - session_start_time
        total_statements = len(session_results)
        successful_statements = sum(1 for r in session_results if r["success"])
        accurate_statements = sum(1 for r in session_results if r["accuracy"])
        avg_response_time = sum(r["response_time"] for r in session_results) / total_statements if total_statements > 0 else 0
        
        summary = {
            "agent_type": "vanilla",
            "provider": self._provider,
            "total_statements": total_statements,
            "successful_statements": successful_statements,
            "accurate_statements": accurate_statements,
            "accuracy_rate": accurate_statements / total_statements if total_statements > 0 else 0,
            "avg_response_time": avg_response_time,
            "session_duration": session_duration,
            "results": session_results
        }
        
        print(f"\n=== Vanilla Agent Session Summary ({self._provider}) ===")
        print(f"Accuracy rate: {summary['accuracy_rate']:.1%} | Average response time: {avg_response_time:.3f}s | Total time: {session_duration:.2f}s")
        return summary
    
    def _validate_accuracy(self, expected: str, actual: str) -> bool:
        expected_lower = expected.lower().strip()
        actual_lower = actual.lower().strip()
        if expected_lower == "uncertain":
            return actual_lower in ["uncertain", "unclear", "unknown"]
        return expected_lower == actual_lower
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        return self.metrics_collector.calculate_averages("vanilla")
    
    def save_metrics(self, filename: Optional[str] = None) -> str:
        return self.metrics_collector.save_metrics(filename)
    
    def export_metrics_to_csv(self, filename: Optional[str] = None) -> str:
        return self.metrics_collector.export_to_csv(filename)


# Example usage and testing
async def main():
    from src.tests.test_data import TestData
    agent = VanillaFactCheckerAgent()
    test_statements = TestData.get_fact_checking_statements()[:5]
    results = await agent.run_fact_checking_session(test_statements)
    metrics_file = agent.save_metrics()
    print(f"\nMetrics saved to: {metrics_file}")
    csv_file = agent.export_metrics_to_csv()
    print(f"Metrics exported to CSV: {csv_file}")


if __name__ == "__main__":
    asyncio.run(main())
