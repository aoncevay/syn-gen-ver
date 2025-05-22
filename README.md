# Statement Perturbation Generator

This project generates slight perturbations to statements without modifying their meaning, entailment, or positioning. The goal is to create a hard test for models to detect perturbations.

## Types of Perturbations

The system currently supports four types of perturbations:

1. **Date Format** (`date_format.py`): Transforms dates from "mm/dd/yyyy" to "MonthName Date, Year" or vice versa.
2. **Entity Reorder** (`entity_reorder.py`): Shuffles named entities (people or organizations) in the text.
3. **Number Rephrase** (`number_rephrase.py`): Changes number formats, e.g., "$14.5 million" to "$14,500,000" or vice versa.
4. **Synonym** (`synonym.py`): Replaces words with their synonyms.

Each statement is perturbed with only one single perturbation.

## Setup

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

## Usage

### Basic Usage

Process statements from an input JSON file and save the perturbed statements to an output file:

```bash
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

## Running Tests

Run the unit tests for each perturbation module:

```bash
python -m unittest discover src/tests
```

## Extending the Project

To add new perturbation types:

1. Create a new file in the `src/perturbation` directory (e.g., `new_perturbation.py`).
2. Implement a main function called `perturb_new_perturbation` that takes a text string and returns a dictionary with perturbation details or None if no perturbation is possible.
3. Register the new perturbation in `src/perturbation/__init__.py`.
4. Add unit tests in the `src/tests` directory.
