import re
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

# Dictionary mapping month names to their numerical representations
MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April", 
    5: "May", 6: "June", 7: "July", 8: "August", 
    9: "September", 10: "October", 11: "November", 12: "December"
}

MONTH_NUMBERS = {name.lower(): num for num, name in MONTH_NAMES.items()}

def find_date_format_numeric(text: str) -> Optional[Tuple[str, int, int]]:
    """
    Find a date in numeric format (mm/dd/yyyy or similar) in the text.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (matched_date, start_index, end_index) or None if no match
    """
    # Pattern for mm/dd/yyyy, mm-dd-yyyy, and similar variations
    patterns = [
        r'\b(0?[1-9]|1[0-2])[/\-\.](0?[1-9]|[12][0-9]|3[01])[/\-\.]((19|20)\d{2}|\d{2})\b',  # mm/dd/yyyy or mm/dd/yy
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return (match.group(), match.start(), match.end())
    
    return None

def find_date_format_literal(text: str) -> Optional[Tuple[str, int, int]]:
    """
    Find a date in literal format (Month Day, Year) in the text.
    
    Args:
        text: The input text
    
    Returns:
        Tuple of (matched_date, start_index, end_index) or None if no match
    """
    # Pattern for "Month Day, Year"
    pattern = r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(0?[1-9]|[12][0-9]|3[01])(?:st|nd|rd|th)?,?\s+((19|20)\d{2})\b'
    
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return (match.group(), match.start(), match.end())
    
    return None

def convert_numeric_to_literal(date_str: str) -> str:
    """
    Convert a numeric date (mm/dd/yyyy) to a literal date (Month Day, Year).
    
    Args:
        date_str: The numeric date string
    
    Returns:
        The literal date string
    """
    # Replace all separators with '/' for standardization
    date_str = re.sub(r'[.\-]', '/', date_str)
    
    try:
        # Parse the date
        if date_str.count('/') == 2:
            if len(date_str.split('/')[-1]) == 2:  # If year is in yy format
                date_str = date_str[:-2] + '20' + date_str[-2:]  # Assume 20xx for yy format
            
            date_obj = datetime.strptime(date_str, '%m/%d/%Y')
            return f"{MONTH_NAMES[date_obj.month]} {date_obj.day}, {date_obj.year}"
    except ValueError:
        # Return original if parsing fails
        return date_str
    
    return date_str

def convert_literal_to_numeric(date_str: str) -> str:
    """
    Convert a literal date (Month Day, Year) to a numeric date (mm/dd/yyyy).
    
    Args:
        date_str: The literal date string
    
    Returns:
        The numeric date string
    """
    # Remove any ordinal indicators (st, nd, rd, th) and clean up
    cleaned = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', date_str)
    
    try:
        # Parse the date
        date_obj = datetime.strptime(cleaned, '%B %d, %Y')
        return date_obj.strftime('%m/%d/%Y')
    except ValueError:
        try:
            # Try another common format
            date_obj = datetime.strptime(cleaned, '%B %d %Y')
            return date_obj.strftime('%m/%d/%Y')
        except ValueError:
            # Return original if parsing fails
            return date_str
    
    return date_str

def perturb_date_format(text: str) -> Optional[Dict[str, Any]]:
    """
    Find and perturb a date format in the text.
    
    Args:
        text: The input text
    
    Returns:
        A dictionary with the perturbation details or None if no perturbation possible
    """
    # Try to find a numeric date first
    date_match = find_date_format_numeric(text)
    if date_match:
        original_date, start, end = date_match
        perturbed_date = convert_numeric_to_literal(original_date)
        
        if perturbed_date != original_date:
            return {
                "perturbed_text": text[:start] + perturbed_date + text[end:],
                "operation": {
                    "Target": "date_format",
                    "From": original_date,
                    "To": perturbed_date,
                    "Type": "Supported"
                }
            }
    
    # Try to find a literal date
    date_match = find_date_format_literal(text)
    if date_match:
        original_date, start, end = date_match
        perturbed_date = convert_literal_to_numeric(original_date)
        
        if perturbed_date != original_date:
            return {
                "perturbed_text": text[:start] + perturbed_date + text[end:],
                "operation": {
                    "Target": "date_format",
                    "From": original_date,
                    "To": perturbed_date,
                    "Type": "Supported"
                }
            }
    
    return None
