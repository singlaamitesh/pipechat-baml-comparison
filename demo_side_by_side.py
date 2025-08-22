#!/usr/bin/env python3
"""
Demo script showing side-by-side comparison of vanilla vs. BAML approaches.
This script demonstrates the key differences without requiring API keys.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tests.test_data import TestData


def show_vanilla_approach():
    """Show the vanilla prompting approach."""
    print("🔴 VANILLA APPROACH (Hardcoded Prompts)")
    print("=" * 50)
    
    print("\n📝 Prompt Template (hardcoded in Python code):")
    print("""
    self.prompt_template = '''
You are a fact-checking AI. Analyze the following statement and determine if it is True, False, or Uncertain.
Provide a one-sentence explanation for your reasoning.

Your response must be in a JSON format with two keys: "classification" and "explanation".

Statement: "{statement}"

JSON Response:
'''
    """)
    
    print("\n💻 Python Implementation:")
    print("""
    async def process_statement(self, statement: str):
        # Create prompt by string formatting
        prompt = self.prompt_template.format(statement=statement)
        
        # Call API and manually parse JSON
        response = await self.openai_client.chat.completions.create(...)
        result = json.loads(response.choices[0].message.content)
        
        # Manual validation
        if not all(key in result for key in ["classification", "explanation"]):
            raise ValueError("Missing required keys")
        
        return result
    """)
    
    print("\n❌ Issues with Vanilla Approach:")
    print("  • Prompts mixed with business logic")
    print("  • Manual JSON parsing and validation")
    print("  • String formatting vulnerabilities")
    print("  • Hard to maintain and version control")
    print("  • Error-prone response handling")


def show_baml_approach():
    """Show the BAML approach."""
    print("\n🟢 BAML APPROACH (Structured Prompts)")
    print("=" * 50)
    
    print("\n📝 BAML Definition (.baml file):")
    print("""
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
      "#
    }
    """)
    
    print("\n💻 Python Implementation:")
    print("""
    async def process_statement(self, statement: str):
        # BAML handles everything automatically
        result = await self.baml_client.CheckFact(statement)
        
        # Type-safe access to results
        return {
            "classification": result.classification,
            "explanation": result.explanation
        }
    """)
    
    print("\n✅ Advantages of BAML Approach:")
    print("  • Clean separation of concerns")
    print("  • Automatic response validation")
    print("  • Type-safe access to results")
    print("  • Easy to maintain and version control")
    print("  • Built-in error handling")


def show_test_data():
    """Show the test data being used."""
    print("\n🧪 TEST DATA")
    print("=" * 50)
    
    test_data = TestData()
    statements = test_data.get_fact_checking_statements()[:5]
    
    print(f"Sample test statements ({len(statements)} of 20 total):")
    for i, item in enumerate(statements, 1):
        print(f"  {i}. {item['statement']}")
        print(f"     Expected: {item['expected_classification']}")
        print(f"     Category: {item['category']}")
        print(f"     Difficulty: {item['difficulty']}")
        print()
    
    # Show ambiguous statements
    ambiguous = test_data.get_ambiguous_statements()[:2]
    print("Sample ambiguous statements:")
    for i, item in enumerate(ambiguous, 1):
        print(f"  {i}. {item['statement']}")
        print(f"     Expected: {item['expected_classification']}")
        print(f"     Reason: {item['reason']}")
        print()


def show_metrics_collection():
    """Show how metrics are collected."""
    print("\n📊 METRICS COLLECTION")
    print("=" * 50)
    
    print("The comparison framework collects:")
    print("  • Latency: Time from input to response")
    print("  • Accuracy: Correct classification rate")
    print("  • Handoff Success: Task completion rate")
    print("  • Response Time: Processing time per statement")
    print("  • Token Usage: API consumption metrics")
    
    print("\nExample metrics table:")
    print("| Agent   | Statement Tested        | Latency | Accuracy | Handoff |")
    print("|---------|-------------------------|---------|----------|---------|")
    print("| Vanilla | \"The Earth is round\"    | 2.1s    | Yes      | Yes     |")
    print("| BAML    | \"The Earth is round\"    | 2.3s    | Yes      | Yes     |")
    print("| Vanilla | \"Humans have 12 fingers\"| 1.9s    | No       | Yes     |")
    print("| BAML    | \"Humans have 12 fingers\"| 2.2s    | Yes      | Yes     |")


def show_winner_determination():
    """Show how the winner is determined."""
    print("\n🏆 WINNER DETERMINATION")
    print("=" * 50)
    
    print("The system uses weighted scoring:")
    print("  • Accuracy Rate: 50% weight (most important)")
    print("  • Response Time: 30% weight (performance)")
    print("  • Handoff Success: 20% weight (reliability)")
    
    print("\nScoring formula:")
    print("  Score = (Accuracy × 0.5) + (Speed × 0.3) + (Reliability × 0.2)")
    
    print("\nExample calculation:")
    print("  Vanilla: (0.8 × 0.5) + (0.7 × 0.3) + (1.0 × 0.2) = 0.81")
    print("  BAML:    (0.9 × 0.5) + (0.6 × 0.3) + (1.0 × 0.2) = 0.83")
    print("  Winner: BAML (0.83 > 0.81)")


def main():
    """Run the side-by-side demo."""
    print("🚀 PIPEchat + BAML vs. VANILLA PROMPTING - SIDE-BY-SIDE DEMO")
    print("=" * 70)
    print("This demo shows the key differences between the two approaches")
    print("without requiring API keys or running actual comparisons.")
    print()
    
    show_vanilla_approach()
    show_baml_approach()
    show_test_data()
    show_metrics_collection()
    show_winner_determination()
    
    print("\n" + "=" * 70)
    print("🎯 KEY TAKEAWAYS:")
    print("  • Vanilla: Simpler setup, harder maintenance")
    print("  • BAML: Better structure, easier maintenance")
    print("  • Both: Can achieve similar performance")
    print("  • Choice depends on project requirements")
    print()
    print("📚 To run the actual comparison:")
    print("  python run_comparison.py")
    print()
    print("📖 For setup instructions:")
    print("  See docs/setup.md")


if __name__ == "__main__":
    main()
