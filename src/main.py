import json
import argparse
import random
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

from perturbation import create_perturbation_manager
from perturbation.config import get_config

def load_data(input_file: str) -> List[Dict[str, Any]]:
    """
    Load data from JSON file.
    
    Args:
        input_file: Path to input JSON file
    
    Returns:
        List of dictionaries containing statements
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Input file '{input_file}' is not valid JSON.")
        sys.exit(1)

def save_data(output_file: str, data: List[Dict[str, Any]]):
    """
    Save data to JSON file.
    
    Args:
        output_file: Path to output JSON file
        data: List of dictionaries to save
    """
    # Create directory if it doesn't exist
    output_path = Path(output_file)
    output_dir = output_path.parent
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error: Could not write to output file '{output_file}': {e}")
        sys.exit(1)

def process_statements(input_data: List[Dict[str, Any]], max_perturbations: int = None) -> List[Dict[str, Any]]:
    """
    Process statements and generate perturbations.
    
    Args:
        input_data: List of dictionaries containing statements
        max_perturbations: Maximum number of perturbations to generate (None for all)
    
    Returns:
        List of dictionaries with original and perturbed statements
    """
    # Get configuration
    config = get_config()
    perturbation_config = config.get("perturbation", {})
    enabled_types = perturbation_config.get("enabled_types", None)
    
    # Create perturbation manager
    perturbation_manager = create_perturbation_manager(enabled_types)
    
    # List to store results
    results = []
    count = 0
    total_attempts = 0
    
    # Shuffle input data to get a diverse sample
    shuffled_data = input_data.copy()
    #random.shuffle(shuffled_data)
    
    print(f"\nProcessing {len(shuffled_data)} statements...")
    print(f"Enabled perturbation types: {enabled_types or 'all'}")
    print(f"Maximum perturbations to generate: {max_perturbations or 'unlimited'}\n")
    
    for i, item in enumerate(shuffled_data, 1):
        if "statement" in item:
            statement = item["statement"]
            print(f"\nProcessing statement {i}/{len(shuffled_data)}: {statement[:100]}...")
            
            # Apply perturbation at sentence level
            result = perturbation_manager.apply_sentence_level_perturbation(statement)
            total_attempts += 1
            
            if result:
                print(f"✓ Successfully applied {result['operations'][0]['Target']} perturbation")
                results.append(result)
                count += 1
                
                # Print current stats every 5 successful perturbations
                if count % 5 == 0:
                    perturbation_manager.print_stats()
                
                # Stop if we've reached the maximum
                if max_perturbations and count >= max_perturbations:
                    print(f"\nReached maximum number of perturbations ({max_perturbations})")
                    break
            else:
                print("✗ No valid perturbation found for this statement")
            
            # Print progress every 10 statements
            if i % 10 == 0:
                print(f"\nProgress: {i}/{len(shuffled_data)} statements processed")
                print(f"Successful perturbations: {count}")
                perturbation_manager.print_stats()
    
    # Print final statistics
    print("\nFinal Statistics:")
    print(f"Total statements processed: {i}")
    print(f"Total successful perturbations: {count}")
    print(f"Overall success rate: {(count/total_attempts)*100:.1f}%")
    perturbation_manager.print_stats()
    
    return results

def main():
    """
    Main function to run the perturbation generation process.
    """
    parser = argparse.ArgumentParser(description="Generate perturbations for statements")
    parser.add_argument("--input", "-i", type=str, required=True, help="Input JSON file path")
    parser.add_argument("--output", "-o", type=str, required=True, help="Output JSON file path")
    parser.add_argument("--max", "-m", type=int, help="Maximum number of perturbations to generate")
    parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--config", "-c", type=str, help="Path to custom config.json file")
    
    args = parser.parse_args()
    
    # If a custom config file is specified, make sure it exists
    if args.config:
        if not os.path.exists(args.config):
            print(f"Error: Specified config file '{args.config}' not found.")
            sys.exit(1)
        
        # Load configuration from the specified file
        try:
            with open(args.config, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                
            # Create a temporary config file in the expected location
            temp_config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=4)
                
            print(f"Using configuration from {args.config}")
        except Exception as e:
            print(f"Error loading config file: {e}")
            sys.exit(1)
    
    # Set random seed
    random.seed(args.seed)
    
    # Load data
    print(f"Loading data from {args.input}")
    data = load_data(args.input)
    print(f"Loaded {len(data)} items")
    
    # Process statements
    print(f"Processing statements...")
    results = process_statements(data, args.max)
    print(f"Generated {len(results)} perturbations")
    
    # Save results
    print(f"Saving results to {args.output}")
    save_data(args.output, results)
    print("Done!")

if __name__ == "__main__":
    main()
