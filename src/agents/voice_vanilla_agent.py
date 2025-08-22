"""
Voice-enabled Vanilla agent implementation using Pipecat framework.
This agent demonstrates voice fact-checking using traditional hardcoded prompts.
"""
import asyncio
import time
from typing import Dict, Any, Optional, List

from pipecat.frames.frames import LLMMessagesFrame, TextFrame, TTSFrame
from pipecat.processors.base_processor import BaseProcessor
from pipecat.services.ai_services import LLMService
from pipecat.services.openai import OpenAILLMService
from pipecat.services.google import GoogleLLMService
from pipecat.services.elevenlabs import ElevenLabsTTSService
from pipecat.services.deepgram import DeepgramSTTService
from pipecat.transports.local.audio import AudioInputTransport, AudioOutputTransport
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask

from src.utils.metrics import MetricsCollector, AgentMetrics
from src.config.settings import settings


class VoiceVanillaFactCheckerProcessor(BaseProcessor):
    """
    Voice-enabled vanilla fact-checking processor using hardcoded prompts.
    
    This demonstrates the traditional approach with voice I/O through Pipecat.
    """
    
    def __init__(self, llm_service: LLMService, metrics_collector: Optional[MetricsCollector] = None):
        super().__init__()
        self.llm_service = llm_service
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.conversation_state = []
        
    async def process_frame(self, frame, direction):
        """Process incoming frames and handle fact-checking conversations."""
        
        if isinstance(frame, TextFrame):
            # This is transcribed speech from the user
            user_text = frame.text
            
            # Start timing for metrics
            start_time = self.metrics_collector.start_timer()
            
            try:
                # VANILLA APPROACH: Hardcoded prompt construction
                # This is scattered throughout the code and hard to maintain
                prompt = self._build_vanilla_prompt(user_text)
                
                # Create LLM messages frame with hardcoded system prompt
                messages = [
                    {
                        "role": "system", 
                        "content": "You are a voice-based fact-checking assistant. Respond conversationally and concisely."
                    },
                    {"role": "user", "content": prompt}
                ]
                
                # Send to LLM service
                llm_frame = LLMMessagesFrame(messages)
                await self.push_frame(llm_frame, direction)
                
                # Record metrics
                response_time = self.metrics_collector.measure_latency(start_time)
                self._record_interaction_metrics(user_text, response_time, True)
                
            except Exception as e:
                # Error handling - send error response via TTS
                error_response = f"I'm sorry, I encountered an error while fact-checking: {str(e)}"
                tts_frame = TTSFrame(error_response)
                await self.push_frame(tts_frame, direction)
                
                response_time = self.metrics_collector.measure_latency(start_time)
                self._record_interaction_metrics(user_text, response_time, False, str(e))
        
        # Pass through other frames
        await self.push_frame(frame, direction)
    
    def _build_vanilla_prompt(self, user_input: str) -> str:
        """
        Build a vanilla prompt using hardcoded string concatenation.
        
        This demonstrates the pain points of vanilla prompting:
        - Hardcoded strings scattered throughout code
        - No structure or validation
        - Difficult to maintain and update
        - Error-prone concatenation
        """
        
        # Check if this looks like a fact-checking request
        if any(word in user_input.lower() for word in ['true', 'false', 'fact', 'correct', 'wrong', 'verify', 'check']):
            # Fact-checking prompt
            prompt = f"""
            Please fact-check the following statement or question:
            
            User: "{user_input}"
            
            Analyze this and respond with:
            1. Whether the statement is True, False, or Uncertain
            2. A brief explanation in conversational tone
            3. Keep your response under 30 seconds of speech
            
            Be conversational and helpful, as this is a voice interaction.
            """
        else:
            # General conversation prompt
            prompt = f"""
            The user said: "{user_input}"
            
            If this contains a factual claim, please fact-check it.
            If it's a general question about facts, please answer helpfully.
            If it's conversational, respond appropriately and ask if they'd like to fact-check anything.
            
            Keep your response conversational and under 30 seconds of speech.
            """
        
        return prompt
    
    def _record_interaction_metrics(self, user_input: str, response_time: float, 
                                  success: bool, error_message: Optional[str] = None):
        """Record metrics for this voice interaction."""
        
        # Simplified accuracy determination - in a real system this would be more sophisticated
        accuracy = success  # For demonstration
        handoff_success = success  # Simplified - whether the interaction completed successfully
        
        metrics = AgentMetrics(
            agent_type="voice_vanilla",
            statement=user_input,
            latency=response_time,
            accuracy=accuracy,
            handoff_success=handoff_success,
            response_time=response_time,
            tokens_used=None,  # Not easily available in this setup
            error_message=error_message
        )
        
        self.metrics_collector.add_metrics(metrics)


class VoiceVanillaFactCheckerAgent:
    """
    Complete voice-enabled vanilla fact-checking agent using Pipecat.
    
    This demonstrates how to build a voice agent with the traditional 
    vanilla prompting approach.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.pipeline = None
        self.task = None
        
        # Initialize services based on configuration
        self._setup_services()
    
    def _setup_services(self):
        """Setup LLM, TTS, and STT services based on configuration."""
        
        # Setup LLM service
        if settings.LLM_PROVIDER.lower() == "openai" and settings.OPENAI_API_KEY:
            self.llm_service = OpenAILLMService(
                api_key=settings.OPENAI_API_KEY,
                model=settings.DEFAULT_MODEL_OPENAI
            )
        elif settings.LLM_PROVIDER.lower() == "gemini" and settings.GOOGLE_API_KEY:
            self.llm_service = GoogleLLMService(
                api_key=settings.GOOGLE_API_KEY,
                model=settings.DEFAULT_MODEL_GEMINI
            )
        else:
            print("Warning: No valid LLM configuration found, using mock service")
            self.llm_service = None
        
        # Setup TTS service (optional)
        if settings.ELEVENLABS_API_KEY:
            self.tts_service = ElevenLabsTTSService(api_key=settings.ELEVENLABS_API_KEY)
        else:
            print("Info: No ElevenLabs API key, TTS will be limited")
            self.tts_service = None
        
        # Setup STT service (optional)
        if settings.DEEPGRAM_API_KEY:
            self.stt_service = DeepgramSTTService(api_key=settings.DEEPGRAM_API_KEY)
        else:
            print("Info: No Deepgram API key, STT will be limited")
            self.stt_service = None
    
    async def create_voice_pipeline(self):
        """Create the voice processing pipeline."""
        
        if not self.llm_service:
            raise RuntimeError("No LLM service available for voice pipeline")
        
        # Create the fact-checking processor
        fact_checker = VoiceVanillaFactCheckerProcessor(
            llm_service=self.llm_service,
            metrics_collector=self.metrics_collector
        )
        
        # Create audio transports
        audio_input = AudioInputTransport()
        audio_output = AudioOutputTransport()
        
        # Build pipeline components
        pipeline_components = [audio_input]
        
        # Add STT if available
        if self.stt_service:
            pipeline_components.append(self.stt_service)
        
        # Add our fact-checking processor
        pipeline_components.append(fact_checker)
        
        # Add LLM service
        pipeline_components.append(self.llm_service)
        
        # Add TTS if available
        if self.tts_service:
            pipeline_components.append(self.tts_service)
        
        # Add audio output
        pipeline_components.append(audio_output)
        
        # Create pipeline
        self.pipeline = Pipeline(pipeline_components)
        
        return self.pipeline
    
    async def start_voice_session(self, duration_seconds: int = 60):
        """
        Start a voice fact-checking session.
        
        Args:
            duration_seconds: How long to run the session
        """
        if not self.pipeline:
            await self.create_voice_pipeline()
        
        print(f"🎤 Starting voice vanilla fact-checking session for {duration_seconds} seconds...")
        print("Say something to fact-check, or ask a factual question!")
        
        # Create and run the pipeline task
        self.task = PipelineTask(self.pipeline)
        
        # Run for specified duration
        try:
            runner = PipelineRunner()
            await runner.run(self.task, duration=duration_seconds)
        except KeyboardInterrupt:
            print("\n⏹️ Voice session stopped by user")
        except Exception as e:
            print(f"\n❌ Voice session error: {e}")
        finally:
            if self.task:
                await self.task.stop()
    
    async def run_test_conversation(self, test_statements: List[str]) -> Dict[str, Any]:
        """
        Run a test conversation with predefined statements.
        
        This simulates voice input for testing purposes.
        """
        results = []
        session_start = time.time()
        
        print(f"🧪 Running voice vanilla agent test with {len(test_statements)} statements...")
        
        for i, statement in enumerate(test_statements):
            print(f"\n📢 Test statement {i+1}: {statement}")
            
            # Simulate processing the statement
            start_time = self.metrics_collector.start_timer()
            
            try:
                # Process using vanilla approach
                processor = VoiceVanillaFactCheckerProcessor(
                    llm_service=self.llm_service,
                    metrics_collector=self.metrics_collector
                )
                
                # Simulate the fact-checking process
                prompt = processor._build_vanilla_prompt(statement)
                
                # Mock processing time
                await asyncio.sleep(0.1)
                response_time = self.metrics_collector.measure_latency(start_time)
                
                # Record result
                results.append({
                    "statement": statement,
                    "approach": "voice_vanilla",
                    "prompt_length": len(prompt),
                    "response_time": response_time,
                    "success": True
                })
                
                print(f"✅ Processed in {response_time:.3f}s")
                
            except Exception as e:
                response_time = self.metrics_collector.measure_latency(start_time)
                results.append({
                    "statement": statement,
                    "approach": "voice_vanilla",
                    "response_time": response_time,
                    "success": False,
                    "error": str(e)
                })
                print(f"❌ Error: {e}")
        
        session_duration = time.time() - session_start
        
        # Generate summary
        successful_tests = sum(1 for r in results if r["success"])
        avg_response_time = sum(r["response_time"] for r in results) / len(results)
        
        summary = {
            "agent_type": "voice_vanilla",
            "total_tests": len(results),
            "successful_tests": successful_tests,
            "avg_response_time": avg_response_time,
            "session_duration": session_duration,
            "results": results,
            "voice_features": [
                "Real-time audio input/output",
                "Speech-to-text processing",
                "Text-to-speech responses",
                "Conversational interaction flow"
            ],
            "vanilla_challenges": [
                "Hardcoded prompts scattered in code",
                "Manual string concatenation",
                "No structured validation",
                "Difficult prompt maintenance"
            ]
        }
        
        print(f"\n=== Voice Vanilla Agent Test Summary ===")
        print(f"Tests completed: {successful_tests}/{len(results)}")
        print(f"Average response time: {avg_response_time:.3f}s")
        print(f"Session duration: {session_duration:.2f}s")
        
        return summary
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of collected metrics."""
        return self.metrics_collector.get_summary()


# Example usage and testing
if __name__ == "__main__":
    async def test_voice_vanilla_agent():
        """Test the voice vanilla agent."""
        agent = VoiceVanillaFactCheckerAgent()
        
        # Test statements
        test_statements = [
            "Is the Earth round?",
            "Tell me if humans have 12 fingers",
            "I heard that water boils at 100 degrees Celsius",
            "Is it true that the sky is blue because of ocean reflection?",
            "Can you verify that chocolate is toxic to dogs?"
        ]
        
        # Run test conversation
        results = await agent.run_test_conversation(test_statements)
        
        # Show results
        print(f"\n📊 Voice vanilla agent completed {results['successful_tests']}/{results['total_tests']} tests")
        print(f"Average response time: {results['avg_response_time']:.3f}s")
        
        return results
    
    # Run the test
    asyncio.run(test_voice_vanilla_agent())
