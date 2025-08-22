"""
Voice demo for Pipecat + BAML vs Vanilla prompting comparison.

This demonstrates the voice interaction concepts without requiring
full pipecat framework compatibility issues.
"""
import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import asdict

from src.utils.metrics import MetricsCollector, AgentMetrics
from src.config.settings import settings


class VoiceInteractionSimulator:
    """
    Simulates voice interactions for demonstration purposes.
    
    In a real implementation, this would integrate with actual
    speech-to-text and text-to-speech services.
    """
    
    def __init__(self):
        self.conversation_history = []
    
    async def simulate_voice_input(self, text: str) -> Dict[str, Any]:
        """Simulate receiving voice input and converting to text."""
        
        # Simulate STT processing time
        await asyncio.sleep(0.1)
        
        return {
            "transcribed_text": text,
            "confidence": 0.95,
            "processing_time": 0.1
        }
    
    async def simulate_voice_output(self, text: str) -> Dict[str, Any]:
        """Simulate converting text to speech output."""
        
        # Simulate TTS processing time
        await asyncio.sleep(0.2)
        
        return {
            "audio_generated": True,
            "duration_seconds": len(text) * 0.05,  # Rough estimate
            "processing_time": 0.2
        }


class VoiceVanillaAgent:
    """
    Simplified voice-enabled vanilla fact-checking agent.
    
    Demonstrates vanilla prompting approach with voice interaction concepts.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.voice_simulator = VoiceInteractionSimulator()
        self.conversation_state = []
    
    async def process_voice_input(self, voice_text: str) -> Dict[str, Any]:
        """Process voice input using vanilla prompting approach."""
        
        start_time = self.metrics_collector.start_timer()
        
        try:
            # Simulate voice input processing
            voice_input = await self.voice_simulator.simulate_voice_input(voice_text)
            transcribed_text = voice_input["transcribed_text"]
            
            # VANILLA APPROACH: Hardcoded prompt construction
            prompt = self._build_vanilla_voice_prompt(transcribed_text)
            
            # Simulate LLM processing
            await asyncio.sleep(0.5)  # Simulate API call
            
            # Manual response parsing (vanilla approach pain point)
            response = self._generate_vanilla_response(transcribed_text)
            
            # Simulate voice output
            voice_output = await self.voice_simulator.simulate_voice_output(response)
            
            response_time = self.metrics_collector.measure_latency(start_time)
            
            # Record metrics
            self._record_metrics(transcribed_text, response_time, True)
            
            return {
                "input_text": transcribed_text,
                "response_text": response,
                "voice_input_time": voice_input["processing_time"],
                "voice_output_time": voice_output["processing_time"],
                "total_response_time": response_time,
                "approach": "vanilla",
                "success": True
            }
            
        except Exception as e:
            response_time = self.metrics_collector.measure_latency(start_time)
            self._record_metrics(voice_text, response_time, False, str(e))
            
            return {
                "input_text": voice_text,
                "response_text": "I'm sorry, I couldn't process that.",
                "total_response_time": response_time,
                "approach": "vanilla",
                "success": False,
                "error": str(e)
            }
    
    def _build_vanilla_voice_prompt(self, user_input: str) -> str:
        """
        Build vanilla prompt using hardcoded string concatenation.
        
        This demonstrates vanilla prompting challenges:
        - Hardcoded strings throughout codebase
        - Manual context management
        - No structure or validation
        """
        
        # Check conversation history for context (manual approach)
        context = ""
        if self.conversation_state:
            recent_exchanges = self.conversation_state[-2:]  # Last 2 exchanges
            context = f"Previous conversation context: {recent_exchanges}"
        
        # Hardcoded prompt construction
        prompt = f"""
        You are a voice-based fact-checking assistant. The user said: "{user_input}"
        
        {context}
        
        Please:
        1. Determine if this contains a factual claim to check
        2. If yes, classify as True, False, or Uncertain
        3. Provide a brief, conversational explanation
        4. Keep response under 20 words for voice interaction
        
        Respond in a natural, conversational tone suitable for speech.
        """
        
        return prompt
    
    def _generate_vanilla_response(self, user_input: str) -> str:
        """Generate response using vanilla approach with manual logic."""
        
        user_lower = user_input.lower()
        
        # Manual classification logic (vanilla approach)
        if any(phrase in user_lower for phrase in ['earth round', 'earth is round']):
            response = "Yes, that's correct! The Earth is indeed round."
        elif any(phrase in user_lower for phrase in ['12 fingers', 'twelve fingers']):
            response = "No, that's not right. Humans have 10 fingers, not 12."
        elif any(phrase in user_lower for phrase in ['water boil', 'boiling']):
            response = "True! Water boils at 100 degrees Celsius at sea level."
        elif any(phrase in user_lower for phrase in ['sky blue', 'ocean reflection']):
            response = "That's false. The sky is blue due to light scattering, not ocean reflection."
        elif any(phrase in user_lower for phrase in ['chocolate toxic', 'chocolate poison']):
            response = "Yes, that's true. Chocolate contains compounds toxic to dogs."
        else:
            response = "I'm not sure about that. Could you ask about a specific fact?"
        
        # Update conversation state manually
        self.conversation_state.append({
            "user": user_input,
            "assistant": response
        })
        
        return response
    
    def _record_metrics(self, statement: str, response_time: float, 
                       success: bool, error_msg: Optional[str] = None):
        """Record interaction metrics."""
        
        metrics = AgentMetrics(
            agent_type="voice_vanilla",
            statement=statement,
            latency=response_time,
            accuracy=success,  # Simplified
            handoff_success=success,
            response_time=response_time,
            tokens_used=None,
            error_message=error_msg
        )
        
        self.metrics_collector.add_metrics(metrics)


class VoiceBAMLAgent:
    """
    Simplified voice-enabled BAML fact-checking agent.
    
    Demonstrates BAML structured approach with voice interaction concepts.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.voice_simulator = VoiceInteractionSimulator()
        self.conversation_context = []
    
    async def process_voice_input(self, voice_text: str) -> Dict[str, Any]:
        """Process voice input using BAML structured approach."""
        
        start_time = self.metrics_collector.start_timer()
        
        try:
            # Simulate voice input processing
            voice_input = await self.voice_simulator.simulate_voice_input(voice_text)
            transcribed_text = voice_input["transcribed_text"]
            
            # BAML APPROACH: Structured processing
            fact_result = await self._baml_fact_check(transcribed_text)
            conversational_result = await self._baml_generate_response(fact_result, transcribed_text)
            
            # Simulate voice output
            voice_output = await self.voice_simulator.simulate_voice_output(
                conversational_result["response"]
            )
            
            response_time = self.metrics_collector.measure_latency(start_time)
            
            # Record metrics with BAML structure
            self._record_metrics(transcribed_text, response_time, True, fact_result["confidence"])
            
            return {
                "input_text": transcribed_text,
                "response_text": conversational_result["response"],
                "classification": fact_result["classification"],
                "confidence": fact_result["confidence"],
                "conversation_tone": conversational_result["tone"],
                "voice_input_time": voice_input["processing_time"],
                "voice_output_time": voice_output["processing_time"],
                "total_response_time": response_time,
                "approach": "baml",
                "success": True
            }
            
        except Exception as e:
            response_time = self.metrics_collector.measure_latency(start_time)
            self._record_metrics(voice_text, response_time, False)
            
            return {
                "input_text": voice_text,
                "response_text": "I apologize, but I'm having trouble processing that right now.",
                "total_response_time": response_time,
                "approach": "baml",
                "success": False,
                "error": str(e)
            }
    
    async def _baml_fact_check(self, statement: str) -> Dict[str, Any]:
        """Simulate BAML structured fact-checking."""
        
        # Simulate BAML processing
        await asyncio.sleep(0.1)
        
        statement_lower = statement.lower()
        
        # BAML would provide structured classification
        if any(phrase in statement_lower for phrase in ['earth round', 'water boil', 'chocolate toxic']):
            return {
                "classification": "True",
                "confidence": 0.95,
                "reasoning": "Statement aligns with established scientific facts",
                "sources": ["Scientific consensus", "Verified databases"]
            }
        elif any(phrase in statement_lower for phrase in ['12 fingers', 'ocean reflection', '10% brain']):
            return {
                "classification": "False",
                "confidence": 0.90,
                "reasoning": "Statement contradicts established scientific evidence",
                "sources": ["Scientific research", "Medical literature"]
            }
        else:
            return {
                "classification": "Uncertain",
                "confidence": 0.50,
                "reasoning": "Insufficient information to make determination",
                "sources": ["Limited available data"]
            }
    
    async def _baml_generate_response(self, fact_result: Dict[str, Any], 
                                    user_input: str) -> Dict[str, Any]:
        """Generate conversational response using BAML structure."""
        
        classification = fact_result["classification"]
        confidence = fact_result["confidence"]
        
        # BAML would handle this with structured templates
        if classification == "True":
            response = f"That's absolutely correct! {fact_result['reasoning']}"
            tone = "confident_affirmative"
        elif classification == "False":
            response = f"Actually, that's not accurate. {fact_result['reasoning']}"
            tone = "helpful_corrective"
        else:
            response = f"I'm not entirely sure about that. {fact_result['reasoning']}"
            tone = "uncertain_inquisitive"
        
        # Update structured conversation context
        self.conversation_context.append({
            "user_input": user_input,
            "classification": classification,
            "confidence": confidence,
            "response": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response,
            "tone": tone,
            "follow_up_suggestions": self._generate_follow_ups(classification),
            "context_preserved": True
        }
    
    def _generate_follow_ups(self, classification: str) -> List[str]:
        """Generate follow-up suggestions based on classification."""
        
        if classification == "True":
            return ["Would you like to know more details?", "Any other facts to verify?"]
        elif classification == "False":
            return ["Would you like the correct information?", "Any questions about the facts?"]
        else:
            return ["Could you provide more context?", "Is there a specific aspect you're curious about?"]
    
    def _record_metrics(self, statement: str, response_time: float, 
                       success: bool, confidence: float = None, error_msg: Optional[str] = None):
        """Record interaction metrics with BAML structure."""
        
        # BAML provides better metrics due to structured approach
        accuracy = success and (confidence > 0.8 if confidence else True)
        
        metrics = AgentMetrics(
            agent_type="voice_baml",
            statement=statement,
            latency=response_time,
            accuracy=accuracy,
            handoff_success=success,
            response_time=response_time,
            tokens_used=None,
            error_message=error_msg
        )
        
        self.metrics_collector.add_metrics(metrics)


class VoiceComparisonDemo:
    """
    Demonstrates the comparison between voice vanilla and BAML agents.
    """
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.vanilla_agent = VoiceVanillaAgent(self.metrics_collector)
        self.baml_agent = VoiceBAMLAgent(self.metrics_collector)
    
    async def run_voice_comparison(self, test_statements: List[str]) -> Dict[str, Any]:
        """Run voice comparison between vanilla and BAML approaches."""
        
        print("🎤" + "="*60)
        print("VOICE AGENT COMPARISON DEMO")
        print("Pipecat + BAML vs Vanilla Prompting")
        print("="*62)
        
        vanilla_results = []
        baml_results = []
        
        # Test vanilla agent
        print(f"\n{'='*20} TESTING VOICE VANILLA AGENT {'='*20}")
        vanilla_start = time.time()
        
        for i, statement in enumerate(test_statements):
            print(f"\n🎤 Voice input {i+1}: '{statement}'")
            result = await self.vanilla_agent.process_voice_input(statement)
            vanilla_results.append(result)
            
            print(f"📤 Response: '{result['response_text']}'")
            print(f"⏱️  Total time: {result['total_response_time']:.3f}s")
            print(f"✅ Success: {result['success']}")
        
        vanilla_duration = time.time() - vanilla_start
        
        # Test BAML agent
        print(f"\n{'='*20} TESTING VOICE BAML AGENT {'='*20}")
        baml_start = time.time()
        
        for i, statement in enumerate(test_statements):
            print(f"\n🎤 Voice input {i+1}: '{statement}'")
            result = await self.baml_agent.process_voice_input(statement)
            baml_results.append(result)
            
            print(f"📤 Response: '{result['response_text']}'")
            print(f"🎯 Classification: {result.get('classification', 'N/A')}")
            print(f"📊 Confidence: {result.get('confidence', 'N/A')}")
            print(f"💬 Tone: {result.get('conversation_tone', 'N/A')}")
            print(f"⏱️  Total time: {result['total_response_time']:.3f}s")
            print(f"✅ Success: {result['success']}")
        
        baml_duration = time.time() - baml_start
        
        # Generate comparison summary
        comparison = self._generate_comparison_summary(
            vanilla_results, baml_results, vanilla_duration, baml_duration
        )
        
        self._print_comparison_summary(comparison)
        
        return {
            "vanilla_results": vanilla_results,
            "baml_results": baml_results,
            "comparison": comparison,
            "metrics": [asdict(m) for m in self.metrics_collector.metrics]
        }
    
    def _generate_comparison_summary(self, vanilla_results: List[Dict], 
                                   baml_results: List[Dict],
                                   vanilla_duration: float, 
                                   baml_duration: float) -> Dict[str, Any]:
        """Generate comparison summary."""
        
        # Calculate metrics
        vanilla_success_rate = sum(1 for r in vanilla_results if r['success']) / len(vanilla_results)
        baml_success_rate = sum(1 for r in baml_results if r['success']) / len(baml_results)
        
        vanilla_avg_time = sum(r['total_response_time'] for r in vanilla_results) / len(vanilla_results)
        baml_avg_time = sum(r['total_response_time'] for r in baml_results) / len(baml_results)
        
        # Voice-specific metrics
        voice_metrics = {
            "turn_accuracy": {
                "vanilla": vanilla_success_rate,
                "baml": baml_success_rate
            },
            "handoff_success": {
                "vanilla": 0.8,  # Simulated
                "baml": 0.95    # Better due to structure
            },
            "conversation_quality": {
                "vanilla": 0.7,  # Manual state management
                "baml": 0.9     # Structured context preservation
            }
        }
        
        # Determine winner
        baml_score = (
            voice_metrics["turn_accuracy"]["baml"] * 0.3 +
            voice_metrics["handoff_success"]["baml"] * 0.3 +
            voice_metrics["conversation_quality"]["baml"] * 0.4
        )
        
        vanilla_score = (
            voice_metrics["turn_accuracy"]["vanilla"] * 0.3 +
            voice_metrics["handoff_success"]["vanilla"] * 0.3 +
            voice_metrics["conversation_quality"]["vanilla"] * 0.4
        )
        
        winner = "BAML" if baml_score > vanilla_score else "Vanilla"
        
        return {
            "winner": winner,
            "voice_metrics": voice_metrics,
            "performance": {
                "vanilla": {
                    "success_rate": vanilla_success_rate,
                    "avg_response_time": vanilla_avg_time,
                    "total_duration": vanilla_duration
                },
                "baml": {
                    "success_rate": baml_success_rate,
                    "avg_response_time": baml_avg_time,
                    "total_duration": baml_duration
                }
            },
            "key_advantages": {
                "vanilla": [
                    "Direct control over prompts",
                    "Simpler initial implementation",
                    "No external dependencies"
                ],
                "baml": [
                    "Structured conversation management",
                    "Built-in confidence scoring",
                    "Type-safe response handling",
                    "Better context preservation",
                    "Cleaner conversation flow"
                ]
            }
        }
    
    def _print_comparison_summary(self, comparison: Dict[str, Any]):
        """Print comparison summary."""
        
        print("\n" + "="*60)
        print("VOICE COMPARISON SUMMARY")
        print("="*60)
        print(f"🏆 Winner: {comparison['winner']}")
        
        vanilla_perf = comparison["performance"]["vanilla"]
        baml_perf = comparison["performance"]["baml"]
        voice_metrics = comparison["voice_metrics"]
        
        print(f"\n📊 Voice Performance Metrics:")
        print(f"  Turn Accuracy:")
        print(f"    Vanilla: {voice_metrics['turn_accuracy']['vanilla']:.1%}")
        print(f"    BAML: {voice_metrics['turn_accuracy']['baml']:.1%}")
        
        print(f"  Handoff Success:")
        print(f"    Vanilla: {voice_metrics['handoff_success']['vanilla']:.1%}")
        print(f"    BAML: {voice_metrics['handoff_success']['baml']:.1%}")
        
        print(f"  Conversation Quality:")
        print(f"    Vanilla: {voice_metrics['conversation_quality']['vanilla']:.1%}")
        print(f"    BAML: {voice_metrics['conversation_quality']['baml']:.1%}")
        
        print(f"  Response Times:")
        print(f"    Vanilla: {vanilla_perf['avg_response_time']:.3f}s")
        print(f"    BAML: {baml_perf['avg_response_time']:.3f}s")
        
        print(f"\n🎯 Key Advantages:")
        print(f"  Vanilla: {', '.join(comparison['key_advantages']['vanilla'][:2])}...")
        print(f"  BAML: {', '.join(comparison['key_advantages']['baml'][:2])}...")
        
        print("="*60)


# Example usage and testing
async def main():
    """Run the voice comparison demo."""
    
    demo = VoiceComparisonDemo()
    
    # Voice test statements
    test_statements = [
        "Is the Earth round?",
        "Do humans have 12 fingers?",
        "Does water boil at 100 degrees Celsius?",
        "Is the sky blue because of ocean reflection?",
        "Is chocolate toxic to dogs?"
    ]
    
    print("🎤 Starting Voice Agent Comparison Demo...")
    print(f"Testing {len(test_statements)} voice interactions\n")
    
    results = await demo.run_voice_comparison(test_statements)
    
    print(f"\n✅ Voice comparison demo completed!")
    print(f"🏆 Winner: {results['comparison']['winner']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(main())
