# Setup Guide: Pipechat + BAML vs. Vanilla Prompting Comparison

This guide provides step-by-step instructions for setting up and running the comparison between vanilla prompting and BAML approaches in Pipechat voice AI agents.

## 🎯 Prerequisites

Before you begin, ensure you have:

- **Python 3.9 or higher** installed on your system
- **Git** for cloning the repository
- **API keys** for the required services (see API Setup section below)
- **Basic familiarity** with Python, async/await, and command line tools

## 🚀 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <your-repo-url>
cd pipechat-baml-comparison

# Verify the structure
ls -la
```

You should see:
```
README.md
requirements.txt
pyproject.toml
src/
tests/
docs/
```

### Step 2: Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Verify activation (you should see (venv) in your prompt)
which python  # Should point to venv/bin/python
```

### Step 3: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies (no audio - recommended)
pip install -r requirements-noaudio.txt

# Verify installation
python -c "import pipecat, baml, openai; print('Dependencies installed successfully!')"
```

**Note**: If you encounter issues with `pipecat` or `baml`, you may need to install them from their respective sources:

```bash
# If you need audio support and encounter select module errors,
# try installing audio dependencies separately:
# pip install pyaudio sounddevice

# For Pipechat (if not available on PyPI)
pip install git+https://github.com/pipecat-ai/pipecat.git

# For BAML (if not available on PyPI)
pip install git+https://github.com/boundaryml/baml.git
```

### Step 4: API Setup

You'll need API keys for the following services:

#### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to "API Keys" section
4. Create a new API key
5. Copy the key (it starts with `sk-`)

#### ElevenLabs API Key (Text-to-Speech)
1. Go to [ElevenLabs](https://elevenlabs.io/)
2. Sign up for a free account
3. Navigate to your profile settings
4. Copy your API key

#### Deepgram API Key (Speech-to-Text)
1. Go to [Deepgram](https://deepgram.com/)
2. Sign up for a free account
3. Navigate to your API keys
4. Create a new API key
5. Copy the key

### Step 5: Configure Environment Variables

```bash
# Create environment file from template
cp .env.example .env

# Edit the .env file with your API keys
nano .env  # or use your preferred editor
```

**Important**: The `.env` file should contain:

```bash
# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here
DEEPGRAM_API_KEY=your-deepgram-key-here

# Optional Configuration
BAML_API_KEY=your-baml-key-here
PIPECHAT_LOG_LEVEL=INFO
TEST_MODE=true
METRICS_SAVE_PATH=./metrics/
```

### Step 6: Verify Configuration

```bash
# Test configuration loading
python -c "
from src.config.settings import settings
print('Configuration loaded successfully!')
print(f'OpenAI API Key: {settings.OPENAI_API_KEY[:10]}...')
print(f'ElevenLabs API Key: {settings.ELEVENLABS_API_KEY[:10]}...')
print(f'Deepgram API Key: {settings.DEEPGRAM_API_KEY[:10]}...')
"
```

## 🧪 Testing the Setup

### Test 1: Basic Imports

```bash
# Test that all modules can be imported
python -c "
from src.agents.vanilla_agent import VanillaFactCheckerAgent
from src.agents.baml_agent import BAMLFactCheckerAgent
from src.utils.metrics import MetricsCollector
from src.comparison.runner import ComparisonRunner
print('All modules imported successfully!')
"
```

### Test 2: Test Data

```bash
# Test test data generation
python -c "
from tests.test_data import TestData
statements = TestData.get_fact_checking_statements()[:3]
print(f'Generated {len(statements)} test statements:')
for s in statements:
    print(f'- {s[\"statement\"]} -> {s[\"expected_classification\"]}')
"
```

### Test 3: Individual Agents

```bash
# Test vanilla agent (will use mock data if APIs not configured)
python -m src.agents.vanilla_agent

# Test BAML agent (will use mock data if APIs not configured)
python -m src.agents.baml_agent
```

## 🏃‍♂️ Running the Comparison

### Option 1: Full Comparison (Recommended)

```bash
# Run the complete comparison
python -m src.comparison.runner
```

This will:
- Test both agents on identical test data
- Collect comprehensive metrics
- Generate comparison reports
- Save results to files

### Option 2: Custom Comparison

```python
# Create a custom comparison script
from src.comparison.runner import ComparisonRunner
import asyncio

async def custom_comparison():
    runner = ComparisonRunner()
    
    # Run with specific parameters
    results = await runner.run_comparison(
        test_count=20,           # Use 20 test statements
        include_ambiguous=True,   # Include ambiguous statements
        save_results=True         # Save results to files
    )
    
    print(f"Comparison completed!")
    print(f"Winner: {results['comparison']['winner']}")
    print(f"Vanilla Accuracy: {results['vanilla_results']['accuracy_rate']:.1%}")
    print(f"BAML Accuracy: {results['baml_results']['accuracy_rate']:.1%}")

# Run the custom comparison
asyncio.run(custom_comparison())
```

### Option 3: Interactive Testing

```python
# Test individual statements interactively
from src.agents.vanilla_agent import VanillaFactCheckerAgent
from src.agents.baml_agent import BAMLFactCheckerAgent

async def interactive_test():
    vanilla_agent = VanillaFactCheckerAgent()
    baml_agent = BAMLFactCheckerAgent()
    
    # Test a specific statement
    statement = "The Earth is flat"
    
    print(f"Testing statement: {statement}")
    print("-" * 50)
    
    # Test with vanilla agent
    vanilla_result = await vanilla_agent.process_statement(statement)
    print(f"Vanilla Result: {vanilla_result['classification']}")
    print(f"Explanation: {vanilla_result['explanation']}")
    
    # Test with BAML agent
    baml_result = await baml_agent.process_statement(statement)
    print(f"BAML Result: {baml_result['classification']}")
    print(f"Explanation: {baml_result['explanation']}")

# Run interactive test
asyncio.run(interactive_test())
```

## 📊 Understanding the Results

### Output Files

After running the comparison, you'll find:

```
comparison_results/
├── comparison_results_YYYYMMDD_HHMMSS.json  # Detailed results
├── summary_report_YYYYMMDD_HHMMSS.md        # Human-readable summary
└── ...

metrics/
├── metrics_YYYYMMDD_HHMMSS.json             # Metrics in JSON format
└── metrics_YYYYMMDD_HHMMSS.csv              # Metrics in CSV format
```

### Key Metrics to Look For

1. **Accuracy Rate**: Percentage of correct classifications
2. **Response Time**: Average time to process each statement
3. **Latency**: Time from input to response
4. **Handoff Success**: Whether tasks complete successfully

### Interpreting Results

- **Higher accuracy** indicates better fact-checking performance
- **Lower response time** indicates faster processing
- **Consistent handoff success** indicates reliable operation
- **Overall winner** is determined by weighted scoring of all metrics

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors

```bash
# If you get import errors, check your Python path
python -c "import sys; print('\n'.join(sys.path))"

# Make sure you're in the project directory
pwd  # Should show /path/to/pipechat-baml-comparison
```

#### 2. API Key Issues

```bash
# Test API connectivity
python -c "
import openai
client = openai.AsyncOpenAI(api_key='your-key-here')
print('OpenAI client created successfully')
"
```

#### 3. BAML Not Available

If BAML is not available, the system will automatically fall back to a mock implementation:

```bash
# You'll see this message:
# Warning: Could not initialize BAML client: ...
# Falling back to mock BAML client for demonstration
```

This allows you to test the comparison framework even without BAML access.

#### 4. Memory Issues

If you encounter memory issues with large test sets:

```python
# Reduce test count
results = await runner.run_comparison(test_count=5)
```

### Getting Help

1. **Check the logs**: Look for error messages in the console output
2. **Verify API keys**: Ensure all API keys are correctly set
3. **Check dependencies**: Verify all packages are installed correctly
4. **Review configuration**: Check that environment variables are loaded

## 🚀 Next Steps

Once you have the basic comparison running:

1. **Experiment with different test data**: Modify `tests/test_data.py`
2. **Customize metrics collection**: Extend `src/utils/metrics.py`
3. **Add new prompt strategies**: Create additional agent implementations
4. **Integrate with real voice input**: Connect actual audio devices
5. **Scale up testing**: Run larger test sets for more statistical significance

## 📚 Additional Resources

- [Pipechat Documentation](https://docs.pipecat.ai/)
- [BAML Documentation](https://docs.boundaryml.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [ElevenLabs API Docs](https://elevenlabs.io/docs/api-reference)
- [Deepgram API Docs](https://developers.deepgram.com/docs)

---

**Need help?** Check the project issues or create a new one with detailed error information.
