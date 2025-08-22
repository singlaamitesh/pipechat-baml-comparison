#!/usr/bin/env python3
"""
Simple script to run the Pipechat + BAML vs. Vanilla prompting comparison.
This script demonstrates the complete comparison framework.
"""

import asyncio
import sys
import os

# Ensure the project root is in the Python path for module discovery.
# This makes 'src' and 'tests' discoverable as top-level packages.
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.comparison.runner import ComparisonRunner
from src.tests.test_data import TestData


async def main():
    """Run the comparison between vanilla and BAML agents."""
    
    print("🚀 Pipechat + BAML vs. Vanilla Prompting Comparison")
    print("=" * 60)
    
    # Show test data summary
    print("\n📊 Test Data Summary:")
    summary = TestData.get_test_summary()
    print(f"Total statements: {summary['total_statements']}")
    print(f"Categories: {', '.join(summary['categories'].keys())}")
    print(f"Difficulties: {', '.join(summary['difficulties'].keys())}")
    
    # Initialize runner
    print("\n🔧 Initializing comparison runner...")
    runner = ComparisonRunner()
    
    # Run comparison with a reasonable number of test statements
    print("\n🏃‍♂️ Starting comparison...")
    try:
        results = await runner.run_comparison(
            test_count=10,  # Use 10 statements for quick demo
            include_ambiguous=True,
            save_results=True
        )
        
        print(f"\n✅ Comparison completed successfully!")
        print(f"🏆 Overall Winner: {results['comparison']['winner']}")
        
        # Show key metrics
        vanilla_results = results['vanilla_results']
        baml_results = results['baml_results']
        
        print(f"\n📈 Key Results:")
        print(f"  Vanilla Agent:")
        print(f"    Accuracy: {vanilla_results['accuracy_rate']:.1%}")
        print(f"    Avg Response Time: {vanilla_results['avg_response_time']:.3f}s")
        
        print(f"  BAML Agent:")
        print(f"    Accuracy: {baml_results['accuracy_rate']:.1%}")
        print(f"    Avg Response Time: {baml_results['avg_response_time']:.3f}s")
        
        # Show differences
        differences = results['comparison']['differences']
        print(f"\n🔍 Key Differences:")
        print(f"  Accuracy Difference: {differences['accuracy_diff']:+.1%} (BAML vs Vanilla)")
        print(f"  Response Time Difference: {differences['response_time_diff']:+.3f}s (BAML vs Vanilla)")
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error running comparison: {e}")
        print("This might be due to missing API keys or dependencies.")
        print("Check the setup guide for configuration instructions.")
        return None


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        if results:
            print(f"\n🎉 Comparison completed! Check the output files for detailed results.")
            print(f"📁 Results saved to: comparison_results/ and metrics/ directories")
        else:
            print(f"\n⚠️  Comparison failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n⏹️  Comparison interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
