import re
from typing import Optional, Tuple, Dict, Any

# Define multipliers for different scales
MULTIPLIERS = {
    "thousand": 1_000,
    "million": 1_000_000,
    "billion": 1_000_000_000,
    "trillion": 1_000_000_000_000,
}

def find_literal_amount(text: str) -> Optional[Tuple[str, float, str, int, int]]:
    """
    Find a monetary amount expressed in words like "$14.5 million".
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (matched_text, numeric_value, scale, start_index, end_index) or None if no match
    """
    # Pattern for amounts like "$14.5 million" or "14.5 million dollars"
    pattern = r'\$?\s*(\d+(?:\.\d+)?)\s*(thousand|million|billion|trillion)(?:\s+dollars)?|\$?\s*(\d+(?:\.\d+)?)\s*(?:thousand|million|billion|trillion)\s+dollars'
    
    for match in re.finditer(pattern, text, re.IGNORECASE):
        full_match = match.group(0)
        
        # Extract numeric value and scale
        if match.group(1) and match.group(2):  # First pattern matched
            value = float(match.group(1))
            scale = match.group(2).lower()
        else:  # Second pattern matched
            value = float(match.group(3))
            scale = re.search(r'(thousand|million|billion|trillion)', full_match, re.IGNORECASE).group(1).lower()
        
        return (full_match, value, scale, match.start(), match.end())
    
    return None

def find_numeric_amount(text: str) -> Optional[Tuple[str, float, int, int]]:
    """
    Find a large numeric monetary amount like "$14,500,000".
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (matched_text, numeric_value, start_index, end_index) or None if no match
    """
    # Pattern for large numeric amounts with commas
    pattern = r'\$\s*(\d{1,3}(?:,\d{3})+(?:\.\d+)?)'
    
    for match in re.finditer(pattern, text):
        full_match = match.group(0)
        # Remove commas to convert to float
        value_str = match.group(1).replace(',', '')
        value = float(value_str)
        
        # Only consider amounts that could be expressed in thousands or more
        if value >= 1000:
            return (full_match, value, match.start(), match.end())
    
    return None

def convert_literal_to_numeric(value: float, scale: str) -> str:
    """
    Convert a literal amount like 14.5 million to numeric format like 14,500,000.
    
    Args:
        value: The numeric value
        scale: The scale (thousand, million, etc.)
    
    Returns:
        Formatted numeric string with commas
    """
    multiplier = MULTIPLIERS.get(scale.lower(), 1)
    total_value = value * multiplier
    
    # Format with commas
    if float(total_value).is_integer():
        formatted = f"${int(total_value):,}"
    else:
        formatted = f"${total_value:,.2f}"
    
    return formatted

def convert_numeric_to_literal(value: float) -> str:
    """
    Convert a numeric amount to a literal format, finding the most appropriate scale.
    
    Args:
        value: The numeric value
    
    Returns:
        Formatted string with appropriate scale
    """
    # Determine the appropriate scale
    if value >= 1_000_000_000_000:
        scale = "trillion"
        scaled_value = value / 1_000_000_000_000
    elif value >= 1_000_000_000:
        scale = "billion"
        scaled_value = value / 1_000_000_000
    elif value >= 1_000_000:
        scale = "million"
        scaled_value = value / 1_000_000
    else:
        scale = "thousand"
        scaled_value = value / 1_000
    
    # Format the scaled value
    if float(scaled_value).is_integer():
        formatted = f"${int(scaled_value)} {scale}"
    else:
        # Round to at most 2 decimal places
        scaled_value = round(scaled_value * 100) / 100
        formatted = f"${scaled_value} {scale}"
    
    return formatted

def perturb_number_rephrase(text: str) -> Optional[Dict[str, Any]]:
    """
    Find and perturb a monetary amount in the text.
    
    Args:
        text: The input text
    
    Returns:
        A dictionary with the perturbation details or None if no perturbation possible
    """
    # Try to find a literal amount first
    literal_match = find_literal_amount(text)
    if literal_match:
        original_text, value, scale, start, end = literal_match
        perturbed_text = convert_literal_to_numeric(value, scale)
        
        return {
            "perturbed_text": text[:start] + perturbed_text + text[end:],
            "operation": {
                "Target": "number_rephrase",
                "From": original_text,
                "To": perturbed_text,
                "Type": "Supported"
            }
        }
    
    # Try to find a numeric amount
    numeric_match = find_numeric_amount(text)
    if numeric_match:
        original_text, value, start, end = numeric_match
        perturbed_text = convert_numeric_to_literal(value)
        
        return {
            "perturbed_text": text[:start] + perturbed_text + text[end:],
            "operation": {
                "Target": "number_rephrase",
                "From": original_text,
                "To": perturbed_text,
                "Type": "Supported"
            }
        }
    
    return None
