// BAML (Boundary-less Augmented Markdown Language) definition for fact-checking
// This file demonstrates the structured approach to prompt management

// Define the structured output we want from the LLM
class FactCheckResult {
  classification string @enum("True" | "False" | "Uncertain")
  explanation string
}

// Define the function the LLM will implement
function CheckFact(statement: string) -> FactCheckResult {
  client GPT4
  prompt #"
    You are a fact-checking AI. Analyze the following statement and determine if it is True, False, or Uncertain.
    Provide a one-sentence explanation for your reasoning.

    Statement: {{ statement }}

    Respond with a JSON object containing:
    - classification: One of "True", "False", or "Uncertain"
    - explanation: A clear, concise explanation for your classification
  "#
}

// Alternative function with more detailed instructions
function CheckFactDetailed(statement: string) -> FactCheckResult {
  client GPT4
  prompt #"
    You are an expert fact-checking AI with deep knowledge across multiple domains.
    
    Your task is to analyze the given statement and classify it as:
    - "True" if the statement is factually correct based on current scientific/established knowledge
    - "False" if the statement is factually incorrect
    - "Uncertain" if the statement cannot be definitively classified due to ambiguity, subjectivity, or insufficient evidence
    
    Guidelines:
    1. For scientific facts, rely on established research and consensus
    2. For historical facts, use verified historical records
    3. For subjective opinions or future predictions, classify as "Uncertain"
    4. Provide clear, educational explanations that help users understand your reasoning
    
    Statement to analyze: {{ statement }}
    
    Respond with a JSON object containing:
    - classification: The classification (True/False/Uncertain)
    - explanation: A clear explanation of your reasoning
  "#
}

// Function for batch fact-checking
function CheckMultipleFacts(statements: string[]) -> FactCheckResult[] {
  client GPT4
  prompt #"
    You are a fact-checking AI that can process multiple statements at once.
    
    For each statement, determine if it is True, False, or Uncertain.
    Provide a clear explanation for each classification.
    
    Statements to analyze:
    {{ statements | map: "{{ it }}" | join: "\n" }}
    
    Respond with an array of JSON objects, each containing:
    - classification: One of "True", "False", or "Uncertain"
    - explanation: A clear explanation for the classification
  "#
}

// Function for fact-checking with confidence levels
class FactCheckResultWithConfidence {
  classification string @enum("True" | "False" | "Uncertain")
  explanation string
  confidence float @min(0.0) @max(1.0)
  reasoning string
}

function CheckFactWithConfidence(statement: string) -> FactCheckResultWithConfidence {
  client GPT4
  prompt #"
    You are a fact-checking AI that provides confidence levels with your assessments.
    
    Analyze the given statement and classify it as True, False, or Uncertain.
    Also provide a confidence level (0.0 to 1.0) and detailed reasoning.
    
    Statement: {{ statement }}
    
    Respond with a JSON object containing:
    - classification: True, False, or Uncertain
    - explanation: A clear explanation of your classification
    - confidence: A confidence score from 0.0 (completely uncertain) to 1.0 (completely certain)
    - reasoning: Detailed reasoning for your confidence level
  "#
}
