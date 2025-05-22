# Statement Perturbation Generator

This project generates slight perturbations to statements without modifying their meaning, entailment, or positioning. The goal is to create a hard test for models to detect perturbations.

## Types of Perturbations

The system currently supports four types of perturbations:

1. **Date Format** (`date_format.py`): Transforms dates from "mm/dd/yyyy" to "MonthName Date, Year" or vice versa.
2. **Entity Reorder** (`entity_reorder.py`): Shuffles named entities (people or organizations) in the text.
3. **Number Rephrase** (`number_rephrase.py`): Changes number formats, e.g., "$14.5 million" to "$14,500,000" or vice versa.
4. **Synonym** (`synonym.py`): Replaces words with their synonyms.

Each statement is perturbed with only one single perturbation.

## Directory Structure

The recommended directory structure for this project is:

```
syn-gen-ver/              # Project root
├── data/                 # Input and output data
│   └── sample.json       # Sample input data
├── models/               # Language models directory
│   └── en_core_web_trf-3.8.0/  # Extracted spaCy model files
├── src/                  # Source code
│   ├── config.json       # Configuration file
│   ├── main.py           # Main script
│   ├── perturbation/     # Perturbation modules
│   └── tests/            # Unit tests
├── setup_model.sh        # Script to install models
└── requirements.txt      # Dependencies
```

## Setup

### Standard Setup

1. Clone the repository:

```bash
git clone <<YOUR_REPOSITORY>>
cd syn-gen-ver
```

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Download the required NLTK data:

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger')"
```

4. Download the spaCy model:

```bash
python -m spacy download en_core_web_sm
```

### Setup for Restricted Environments

If you're working in an environment with restricted internet access or package installation limitations:

1. Manually download the spaCy model from [the spaCy models page](https://spacy.io/models)
   - The downloaded file will typically have a name like `en_core_web_trf-3.8.0-py3-none-any.whl`

2. Place the downloaded wheel file in the models directory:
   ```
   models/en_core_web_trf-3.8.0-py3-none-any.whl
   ```

3. Use the setup script to install and configure the model:

   ```bash
   # For local installation (extracts to models/ directory)
   chmod +x setup_model.sh
   ./setup_model.sh models/en_core_web_trf-3.8.0-py3-none-any.whl local
   
   # OR for global installation (using pip)
   ./setup_model.sh models/en_core_web_trf-3.8.0-py3-none-any.whl global
   ```

   The script will:
   - Extract/install the model
   - Update the config.json file automatically
   - Create a backup of the original config

4. Manually download NLTK data (if needed):
   - Visit the [NLTK data page](https://www.nltk.org/nltk_data/)
   - Download the required packages (punkt, wordnet, averaged_perceptron_tagger)
   - Place them in a directory and update the `nltk.data_path` in config.json

## Usage

### Running the Script

All commands should be run from the project root directory to ensure that file paths resolve correctly.

### Basic Usage

Process statements from an input JSON file and save the perturbed statements to an output file:

```bash
# Run from the project root directory
python src/main.py --input data/sample.json --output data/perturbed.json
```

### Additional Options

- Limit the number of perturbations:

```bash
python src/main.py --input data/sample.json --output data/perturbed.json --max 100
```

- Set a random seed for reproducibility:

```bash
python src/main.py --input data/sample.json --output data/perturbed.json --seed 42
```

- Specify a custom configuration file:

```bash
python src/main.py --input data/sample.json --output data/perturbed.json --config my_custom_config.json
```

### Running Tests

Run the tests from the project root directory to ensure all paths resolve correctly:

```bash
# Run all tests
python -m unittest discover src/tests
```

You can also run specific test files, classes, or methods:

```bash
# Run a specific test file
python -m unittest src/tests/test_date_format.py

# Run a specific test class
python -m unittest src.tests.test_date_format.TestDateFormat

# Run a specific test method
python -m unittest src.tests.test_date_format.TestDateFormat.test_find_date_format_numeric
```

## Configuration

The system can be configured using a `config.json` file in the project root or `src/` directory. Available configuration options:

```json
{
    "spacy_model": {
        "name": "en_core_web_trf",          // Name of the spaCy model to use
        "local_path": "models/en_core_web_trf-3.8.0",  // Path to extracted model (if use_local_model is true)
        "use_local_model": true             // Whether to use a local model or installed model
    },
    "nltk": {
        "data_path": null,                 // Custom path to NLTK data
        "download_enabled": true           // Whether to allow downloading NLTK resources
    },
    "perturbation": {
        "enabled_types": ["date_format", "entity_reorder", "number_rephrase", "synonym"]
    }
}
```

## Input Format

The input file should be a JSON file containing a list of dictionaries, where each dictionary has a "statement" key:

```json
[
    {"statement": "As of December 31, 2023, the Company measured total assets at fair value of $32,253 thousand."},
    {"statement": "In 2023, Mills Music Trust received $1,237,548 from EMI."}
]
```

## Output Format

The output file will be a JSON file containing a list of dictionaries with the following structure:

```json
[
    {
        "statement": "As of December 31, 2023, the Company measured total assets at fair value of $32,253 thousand.",
        "updated_statement": "As of 12/31/2023, the Company measured total assets at fair value of $32,253 thousand.",
        "operations": [
            {
                "Target": "date_format",
                "From": "December 31, 2023",
                "To": "12/31/2023"
            }
        ]
    }
]
```

## Extending the Project

To add new perturbation types:

1. Create a new file in the `src/perturbation` directory (e.g., `new_perturbation.py`).
2. Implement a main function called `perturb_new_perturbation` that takes a text string and returns a dictionary with perturbation details or None if no perturbation is possible.
3. Register the new perturbation in `src/perturbation/__init__.py`.
4. Add unit tests in the `src/tests` directory.

## Troubleshooting

- **Path Issues**: If you encounter path-related errors, make sure you're running the commands from the project root directory.
- **Model Not Found**: Verify that the path in your config.json correctly points to where you placed the extracted model.
- **Import Errors**: Ensure your Python environment has all required dependencies installed.
- **Model Installation Issues**: 
  - For issues with the wheel file, run the setup script with the appropriate parameters
  - Check the model name matches what's in your config.json
  - For manual installations, ensure the spaCy model version is compatible with your Python version

## Fallback Mechanisms

The system includes fallback mechanisms when NLP resources aren't available:

- **Entity Recognition**: Falls back to regex-based pattern matching for entities
- **Synonym Replacement**: Uses a built-in dictionary of common words and their synonyms
- **Sentence Tokenization**: Falls back to simple rule-based sentence splitting
