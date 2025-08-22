"""
Test data for fact-checking comparison between vanilla and BAML agents.
"""
from typing import List, Dict, Any


class TestData:
    """Test data for fact-checking agent comparison."""
    
    @staticmethod
    def get_fact_checking_statements() -> List[Dict[str, Any]]:
        """Get a comprehensive list of test statements with expected classifications."""
        return [
            {
                "statement": "The Earth is round.",
                "expected_classification": "True",
                "difficulty": "easy",
                "category": "science"
            },
            {
                "statement": "Humans have 12 fingers.",
                "expected_classification": "False",
                "difficulty": "easy",
                "category": "biology"
            },
            {
                "statement": "The sky is blue because of the ocean's reflection.",
                "expected_classification": "False",
                "difficulty": "medium",
                "category": "science"
            },
            {
                "statement": "Water boils at 100 degrees Celsius at sea level.",
                "expected_classification": "True",
                "difficulty": "easy",
                "category": "science"
            },
            {
                "statement": "The Great Wall of China is visible from space with the naked eye.",
                "expected_classification": "False",
                "difficulty": "medium",
                "category": "geography"
            },
            {
                "statement": "Birds are descendants of dinosaurs.",
                "expected_classification": "True",
                "difficulty": "medium",
                "category": "biology"
            },
            {
                "statement": "The human brain uses only 10% of its capacity.",
                "expected_classification": "False",
                "difficulty": "medium",
                "category": "biology"
            },
            {
                "statement": "Lightning never strikes the same place twice.",
                "expected_classification": "False",
                "difficulty": "easy",
                "category": "science"
            },
            {
                "statement": "The speed of light is approximately 300,000 kilometers per second.",
                "expected_classification": "True",
                "difficulty": "medium",
                "category": "physics"
            },
            {
                "statement": "Chocolate is toxic to dogs.",
                "expected_classification": "True",
                "difficulty": "easy",
                "category": "biology"
            },
            {
                "statement": "The moon is made of cheese.",
                "expected_classification": "False",
                "difficulty": "easy",
                "category": "science"
            },
            {
                "statement": "Caffeine is addictive.",
                "expected_classification": "True",
                "difficulty": "medium",
                "category": "health"
            },
            {
                "statement": "The average human body temperature is 98.6 degrees Fahrenheit.",
                "expected_classification": "True",
                "difficulty": "easy",
                "category": "health"
            },
            {
                "statement": "All snakes are venomous.",
                "expected_classification": "False",
                "difficulty": "medium",
                "category": "biology"
            },
            {
                "statement": "The sun is a star.",
                "expected_classification": "True",
                "difficulty": "easy",
                "category": "astronomy"
            }
        ]
    
    @staticmethod
    def get_ambiguous_statements() -> List[Dict[str, Any]]:
        """Get statements that are intentionally ambiguous or uncertain."""
        return [
            {
                "statement": "The best programming language is Python.",
                "expected_classification": "Uncertain",
                "difficulty": "hard",
                "category": "technology",
                "reason": "Subjective opinion with no objective truth"
            },
            {
                "statement": "Climate change will cause catastrophic damage by 2050.",
                "expected_classification": "Uncertain",
                "difficulty": "hard",
                "category": "environment",
                "reason": "Future prediction with complex variables"
            },
            {
                "statement": "Artificial intelligence will replace most human jobs.",
                "expected_classification": "Uncertain",
                "difficulty": "hard",
                "category": "technology",
                "reason": "Future prediction with many unknown factors"
            },
            {
                "statement": "The optimal diet for humans is vegetarian.",
                "expected_classification": "Uncertain",
                "difficulty": "hard",
                "category": "health",
                "reason": "Complex topic with conflicting research"
            },
            {
                "statement": "The universe is infinite in size.",
                "expected_classification": "Uncertain",
                "difficulty": "hard",
                "category": "astronomy",
                "reason": "Current science cannot definitively answer"
            }
        ]
    
    @staticmethod
    def get_all_test_statements() -> List[Dict[str, Any]]:
        """Get all test statements combined."""
        return (
            TestData.get_fact_checking_statements() + 
            TestData.get_ambiguous_statements()
        )
    
    @staticmethod
    def get_statements_by_category(category: str) -> List[Dict[str, Any]]:
        """Get test statements filtered by category."""
        all_statements = TestData.get_all_test_statements()
        return [s for s in all_statements if s.get("category") == category]
    
    @staticmethod
    def get_statements_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
        """Get test statements filtered by difficulty."""
        all_statements = TestData.get_all_test_statements()
        return [s for s in all_statements if s.get("difficulty") == difficulty]
    
    @staticmethod
    def get_random_subset(count: int = 10) -> List[Dict[str, Any]]:
        """Get a random subset of test statements."""
        import random
        all_statements = TestData.get_all_test_statements()
        return random.sample(all_statements, min(count, len(all_statements)))
    
    @staticmethod
    def validate_classification(statement: str, expected: str, actual: str) -> bool:
        """Validate if the actual classification matches the expected one."""
        # For uncertain statements, be more flexible
        if expected == "Uncertain":
            return actual in ["Uncertain", "uncertain", "UNCERTAIN"]
        
        return actual.lower() == expected.lower()
    
    @staticmethod
    def get_test_summary() -> Dict[str, Any]:
        """Get a summary of the test data."""
        all_statements = TestData.get_all_test_statements()
        
        categories = {}
        difficulties = {}
        classifications = {}
        
        for statement in all_statements:
            # Count categories
            cat = statement.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
            # Count difficulties
            diff = statement.get("difficulty", "unknown")
            difficulties[diff] = difficulties.get(diff, 0) + 1
            
            # Count expected classifications
            classif = statement.get("expected_classification", "unknown")
            classifications[classif] = classifications.get(classif, 0) + 1
        
        return {
            "total_statements": len(all_statements),
            "categories": categories,
            "difficulties": difficulties,
            "expected_classifications": classifications
        }


if __name__ == "__main__":
    # Print test data summary
    summary = TestData.get_test_summary()
    print("Test Data Summary:")
    print(f"Total statements: {summary['total_statements']}")
    print(f"Categories: {summary['categories']}")
    print(f"Difficulties: {summary['difficulties']}")
    print(f"Expected classifications: {summary['expected_classifications']}")
    
    # Print a few example statements
    print("\nExample statements:")
    for i, statement in enumerate(TestData.get_fact_checking_statements()[:5]):
        print(f"{i+1}. {statement['statement']} -> {statement['expected_classification']}")
