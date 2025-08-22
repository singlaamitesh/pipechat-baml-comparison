// BAML (Boundary-less Augmented Markdown Language) definition for fact-checking
// Enhanced for Gemini model capabilities and voice interactions

// Define the structured output we want from the LLM
class FactCheckResult {
  classification string @enum("True" | "False" | "Uncertain")
  explanation string
}

// Enhanced result with Gemini-specific features
class GeminiFactCheckResult {
  classification string @enum("True" | "False" | "Uncertain")
  explanation string
  confidence float @min(0.0) @max(1.0)
  reasoning string
  sources string[] @optional
  follow_up_questions string[] @optional
  conversation_tone string @enum("confident" | "helpful" | "inquisitive" | "corrective")
}

// Voice-optimized result for conversational interactions
class VoiceFactCheckResult {
  classification string @enum("True" | "False" | "Uncertain")
  explanation string
  confidence float @min(0.0) @max(1.0)
  conversational_response string
  tone string @enum("confident_affirmative" | "helpful_corrective" | "uncertain_inquisitive")
  follow_up_suggestions string[]
  context_preserved boolean
}

// Basic fact-checking function optimized for Gemini
function CheckFact(statement: string) -> FactCheckResult {
  client Gemini
  prompt #"
    You are a fact-checking AI powered by Google's Gemini model. 
    
    Gemini Strengths to Leverage:
    - Real-time knowledge access
    - Multi-step reasoning capabilities
    - Contextual understanding
    - Factual accuracy with source awareness
    
    Analyze the following statement using Gemini's capabilities:
    Statement: {{ statement }}
    
    Use Gemini's reasoning to:
    1. Access current knowledge and facts
    2. Apply multi-step logical reasoning
    3. Consider context and nuance
    4. Provide clear, educational explanations
    
    Respond with a JSON object containing:
    - classification: "True", "False", or "Uncertain"
    - explanation: A clear, educational explanation leveraging Gemini's knowledge
  "#
}

// Enhanced fact-checking with Gemini's advanced capabilities
function CheckFactWithGemini(statement: string) -> GeminiFactCheckResult {
  client Gemini
  prompt #"
    You are an expert fact-checking AI powered by Google's Gemini model.
    
    Gemini Model Capabilities to Leverage:
    - Real-time knowledge retrieval and synthesis
    - Multi-step reasoning and logical analysis
    - Contextual understanding and nuance detection
    - Source-aware factual verification
    - Educational explanation generation
    
    Your task is to analyze the given statement using Gemini's advanced capabilities:
    Statement: {{ statement }}
    
    Analysis Process (using Gemini's strengths):
    1. **Knowledge Retrieval**: Access current, up-to-date information
    2. **Multi-step Reasoning**: Break down complex claims into logical steps
    3. **Context Analysis**: Consider context, nuance, and edge cases
    4. **Source Awareness**: Be aware of information sources and reliability
    5. **Educational Output**: Provide explanations that help users learn
    
    Classification Guidelines:
    - "True": Factually correct based on current, reliable knowledge
    - "False": Factually incorrect or contradicted by reliable sources
    - "Uncertain": Ambiguous, subjective, or insufficient evidence available
    
    Respond with a JSON object containing:
    - classification: True, False, or Uncertain
    - explanation: Clear, educational explanation using Gemini's knowledge
    - confidence: Confidence score (0.0 to 1.0) based on evidence strength
    - reasoning: Detailed reasoning process showing Gemini's analytical steps
    - sources: Array of relevant information sources (if applicable)
    - follow_up_questions: Suggested questions to deepen understanding
    - conversation_tone: Appropriate tone for voice interaction
  "#
}

// Voice-optimized fact-checking for conversational AI
function CheckFactVoice(statement: string, conversation_context: string[] @optional) -> VoiceFactCheckResult {
  client Gemini
  prompt #"
    You are a voice-based fact-checking AI powered by Google's Gemini model.
    
    Gemini Voice Interaction Strengths:
    - Natural language understanding for conversational flow
    - Context preservation across conversation turns
    - Real-time knowledge synthesis for immediate responses
    - Educational content generation for voice delivery
    - Tone and style adaptation for different contexts
    
    Current conversation context: {{ conversation_context | default: "New conversation" }}
    User statement: {{ statement }}
    
    Voice Interaction Guidelines:
    1. **Conversational Flow**: Maintain natural conversation rhythm
    2. **Context Awareness**: Use conversation history for better responses
    3. **Voice Optimization**: Keep responses concise but informative
    4. **Tone Adaptation**: Match tone to content and user needs
    5. **Educational Value**: Provide learning opportunities through conversation
    
    Use Gemini's capabilities to:
    - Access real-time knowledge for accurate fact-checking
    - Generate conversational responses suitable for voice
    - Preserve context for multi-turn conversations
    - Adapt tone based on content and user interaction
    
    Respond with a JSON object containing:
    - classification: True, False, or Uncertain
    - explanation: Factual explanation using Gemini's knowledge
    - confidence: Confidence level (0.0 to 1.0)
    - conversational_response: Voice-optimized response for speech
    - tone: Appropriate conversational tone
    - follow_up_suggestions: Questions to continue the conversation
    - context_preserved: Whether context was maintained
  "#
}

// Multi-modal fact-checking (for future image/text combinations)
class MultiModalFactCheckResult {
  classification string @enum("True" | "False" | "Uncertain")
  explanation string
  confidence float @min(0.0) @max(1.0)
  visual_analysis string @optional
  text_analysis string
  combined_reasoning string
}

function CheckFactMultiModal(text_statement: string, image_description: string @optional) -> MultiModalFactCheckResult {
  client Gemini
  prompt #"
    You are a multi-modal fact-checking AI powered by Google's Gemini model.
    
    Gemini Multi-Modal Capabilities:
    - Text and image understanding
    - Cross-modal reasoning
    - Visual fact verification
    - Contextual analysis across modalities
    
    Text Statement: {{ text_statement }}
    Image Description: {{ image_description | default: "No image provided" }}
    
    Analysis Process:
    1. **Text Analysis**: Verify factual claims in the text
    2. **Visual Analysis**: If image provided, analyze visual content
    3. **Cross-Modal Reasoning**: Combine text and visual information
    4. **Factual Synthesis**: Provide comprehensive fact-checking
    
    Respond with a JSON object containing:
    - classification: True, False, or Uncertain
    - explanation: Overall factual assessment
    - confidence: Confidence level (0.0 to 1.0)
    - visual_analysis: Analysis of visual content (if applicable)
    - text_analysis: Analysis of text content
    - combined_reasoning: Cross-modal reasoning process
  "#
}

// Batch processing optimized for Gemini's efficiency
function CheckMultipleFactsGemini(statements: string[]) -> GeminiFactCheckResult[] {
  client Gemini
  prompt #"
    You are a batch fact-checking AI powered by Google's Gemini model.
    
    Gemini Batch Processing Strengths:
    - Efficient parallel processing of multiple queries
    - Consistent reasoning across multiple statements
    - Context-aware batch analysis
    - Optimized response generation
    
    Statements to analyze:
    {{ statements | map: "{{ it }}" | join: "\n" }}
    
    Batch Analysis Guidelines:
    1. **Consistency**: Apply consistent reasoning across all statements
    2. **Efficiency**: Leverage Gemini's parallel processing capabilities
    3. **Context Awareness**: Consider relationships between statements
    4. **Quality Maintenance**: Maintain high quality despite batch processing
    
    Respond with an array of JSON objects, each containing:
    - classification: True, False, or Uncertain
    - explanation: Clear explanation using Gemini's knowledge
    - confidence: Confidence score (0.0 to 1.0)
    - reasoning: Detailed reasoning process
    - sources: Relevant information sources
    - follow_up_questions: Suggested follow-up questions
    - conversation_tone: Appropriate tone for interaction
  "#
}

// Educational fact-checking with learning objectives
class EducationalFactCheckResult {
  classification string @enum("True" | "False" | "Uncertain")
  explanation string
  confidence float @min(0.0) @max(1.0)
  learning_points string[]
  related_concepts string[]
  difficulty_level string @enum("beginner" | "intermediate" | "advanced")
}

function CheckFactEducational(statement: string, user_level: string @optional) -> EducationalFactCheckResult {
  client Gemini
  prompt #"
    You are an educational fact-checking AI powered by Google's Gemini model.
    
    Gemini Educational Capabilities:
    - Adaptive learning content generation
    - Multi-level explanation capabilities
    - Concept relationship mapping
    - Progressive knowledge building
    
    Statement: {{ statement }}
    User Level: {{ user_level | default: "intermediate" }}
    
    Educational Approach:
    1. **Level Adaptation**: Adjust explanation complexity to user level
    2. **Learning Points**: Extract key educational concepts
    3. **Concept Mapping**: Connect to related knowledge areas
    4. **Progressive Learning**: Build understanding step by step
    
    Respond with a JSON object containing:
    - classification: True, False, or Uncertain
    - explanation: Level-appropriate explanation
    - confidence: Confidence level (0.0 to 1.0)
    - learning_points: Key concepts to learn from this fact-check
    - related_concepts: Related topics for further exploration
    - difficulty_level: Appropriate complexity level
  "#
}
