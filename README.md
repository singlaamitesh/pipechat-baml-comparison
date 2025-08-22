# Pipechat + BAML vs. Vanilla Prompting Comparison

A comprehensive comparison of two approaches to LLM prompting in voice AI agents: traditional "vanilla" prompting (hardcoded strings) vs. BAML (Boundary-less Augmented Markdown Language) structured prompting.

## 🎯 Project Overview

This project demonstrates the differences between vanilla prompting and BAML by implementing two identical fact-checking voice agents using Pipechat. The goal is to compare performance, maintainability, and developer experience between these two approaches.

### What We're Comparing

- **Vanilla Prompting**: Traditional approach where prompts are hardcoded as strings directly in Python code
- **BAML Prompting**: Modern approach using structured prompt definitions in separate `.baml` files

### LLM Providers (Free-friendly)

- **Gemini (Default)**: Uses `GOOGLE_API_KEY` and free tier where available. Set `LLM_PROVIDER=gemini` (default).
- **OpenAI (Optional)**: Uses `OPENAI_API_KEY`. Set `LLM_PROVIDER=openai` to use OpenAI.

### Audio Services (Optional)

- The comparison works with pure text I/O. TTS (ElevenLabs) and STT (Deepgram) are optional.
- Omit `ELEVENLABS_API_KEY` and `DEEPGRAM_API_KEY` to run free, text-only comparisons.

## 🏗️ Architecture

```
src/
├── agents/
│   ├── vanilla_agent.py      # Vanilla prompting implementation (Gemini/OpenAI)
│   └── baml_agent.py         # BAML prompting implementation
├── baml/
│   └── fact_checker.baml     # BAML prompt definitions
├── utils/
│   └── metrics.py            # Metrics collection and analysis
├── comparison/
│   └── runner.py             # Automated comparison framework
└── config/
    └── settings.py           # Configuration management

tests/
├── test_data.py              # Test statements for fact-checking
└── test_*.py                 # Unit tests for each component

docs/                         # Documentation and analysis reports
comparison_results/           # Generated comparison results
metrics/                      # Collected performance metrics
```

## 🚀 Quick Start (Free, Text-Only)

### Prerequisites

- Python 3.9+
- A Google API Key (for Gemini) — free tier available

### Installation

1. **Install dependencies**
   ```bash
   pip install -r requirements-noaudio.txt
   ```

2. **Create .env (Gemini only)**
   ```bash
   cp env.example .env
   # Edit .env and set GOOGLE_API_KEY, leave ELEVENLABS/DEEPGRAM empty
   # Optionally set LLM_PROVIDER=gemini (default)
   ```

3. **Run the comparison**
   ```bash
   python -m src.comparison.runner
   ```

## 📊 Test Data

The project includes comprehensive test data covering:

- **Easy Facts**: Clear true/false statements (e.g., "The Earth is round")
- **Medium Facts**: Moderately complex statements (e.g., "Birds are descendants of dinosaurs")
- **Ambiguous Statements**: Subjective or uncertain statements (e.g., "The best programming language is Python")

### Test Categories

- Science & Physics
- Biology & Health
- Geography & History
- Technology & Programming
- Environment & Future Predictions

## 🔍 How It Works

### Vanilla Agent

The vanilla agent uses hardcoded prompt strings:

```python
self.prompt_template = """
You are a fact-checking AI. Analyze the following statement and determine if it is True, False, or Uncertain.
Provide a one-sentence explanation for your reasoning.

Your response must be in a JSON format with two keys: "classification" and "explanation".

Statement: "{statement}"

JSON Response:
"""
```

**Pros:**
- Simple to implement
- No additional dependencies
- Direct control over prompt format

**Cons:**
- Prompts mixed with business logic
- Manual JSON parsing and validation
- Harder to maintain and version control
- More error-prone

### BAML Agent

The BAML agent uses structured prompt definitions:

```baml
class FactCheckResult {
  classification string @enum("True" | "False" | "Uncertain")
  explanation string
}

function CheckFact(statement: string) -> FactCheckResult {
  client GPT4
  prompt #"
    You are a fact-checking AI. Analyze the following statement and determine if it is True, False, or Uncertain.
    Provide a one-sentence explanation for your reasoning.

    Statement: {{ statement }}
  "#
}
```

**Pros:**
- Clean separation of concerns
- Automatic response validation
- Type-safe access to results
- Better maintainability
- Easier collaboration

**Cons:**
- Additional dependency (BAML)
- Learning curve for new syntax
- Slightly more complex setup

## 📈 Metrics Collection

The comparison framework collects comprehensive metrics:

### Performance Metrics
- **Latency**: Time from user input to agent response
- **Accuracy**: Correct classification rate vs. expected results
- **Handoff Success**: Successful completion of fact-checking tasks
- **Response Time**: Total processing time per statement

### Code Quality Metrics
- **Maintainability**: Ease of prompt modification and version control
- **Type Safety**: Automatic validation and error handling
- **Developer Experience**: Code clarity and separation of concerns

## 🏆 Running the Comparison

### Basic Comparison

```python
from src.comparison.runner import ComparisonRunner

async def main():
    runner = ComparisonRunner()
    results = await runner.run_comparison(
        test_count=15,
        include_ambiguous=True,
        save_results=True
    )
    print(f"Winner: {results['comparison']['winner']}")

# Run the comparison
asyncio.run(main())
```

### Custom Test Scenarios

```python
# Test with only factual statements
results = await runner.run_comparison(
    test_count=10,
    include_ambiguous=False
)

# Test with specific categories
from tests.test_data import TestData
science_statements = TestData.get_statements_by_category("science")
# ... custom testing logic
```

## 📊 Understanding Results

### Metrics Table Example

| Agent   | Statement Tested                 | Latency (s) | Accuracy | Handoff Success |
| :------ | :------------------------------- | :---------- | :------- | :-------------- |
| Vanilla | "The Earth is round"             | 2.1s        | Yes      | Yes             |
| BAML    | "The Earth is round"             | 2.3s        | Yes      | Yes             |
| Vanilla | "Humans have 12 fingers"         | 1.9s        | No       | Yes             |
| BAML    | "Humans have 12 fingers"         | 2.2s        | Yes      | Yes             |

### Analysis Factors

1. **Accuracy**: Which agent correctly classifies more statements?
2. **Latency**: Which agent responds faster?
3. **Reliability**: Which agent handles edge cases better?
4. **Maintainability**: Which approach is easier to modify and extend?

## 🔧 Configuration

### Environment Variables

```bash
# LLM selection
LLM_PROVIDER=gemini            # gemini (default) | openai
GOOGLE_API_KEY=...             # required if LLM_PROVIDER=gemini
OPENAI_API_KEY=...             # required if LLM_PROVIDER=openai

# Optional audio (omit for free, text-only mode)
ELEVENLABS_API_KEY=
DEEPGRAM_API_KEY=

# Optional
PIPECHAT_LOG_LEVEL=INFO
TEST_MODE=true
```

### Model Configuration

- Gemini default: `gemini-1.5-flash`
- OpenAI default: `gpt-4o-mini`

You can override via env:
```bash
DEFAULT_MODEL_GEMINI=gemini-1.5-pro
DEFAULT_MODEL_OPENAI=gpt-4o
```

## 🧪 Notes

- The vanilla agent is provider-agnostic. It uses Gemini by default if `GOOGLE_API_KEY` is set; otherwise OpenAI if configured.
- Audio services are not required for the comparison and can be skipped to remain free-of-cost.

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/
```

### Run with Coverage

```bash
pytest --cov=src tests/
```

### Test Individual Agents

```bash
# Test vanilla agent
python -m src.agents.vanilla_agent

# Test BAML agent
python -m src.agents.baml_agent
```

## 📁 Output Files

After running the comparison, you'll find:

- `comparison_results/`: Detailed JSON results and analysis
- `metrics/`: Performance metrics in JSON and CSV formats
- `docs/`: Generated reports and documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📚 Additional Resources

- [Pipechat Documentation](https://docs.pipecat.ai/)
- [BAML Documentation](https://docs.boundaryml.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [Deepgram API Documentation](https://developers.deepgram.com/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Pipechat team for the voice AI framework
- BAML team for the structured prompting language
- OpenAI for the LLM capabilities
- ElevenLabs and Deepgram for audio processing services

---

**Note**: This project is designed for educational and research purposes. Please ensure you have appropriate API access and follow usage guidelines for all services.
