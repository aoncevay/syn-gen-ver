import unittest
import sys
import os

# Add the parent directory to the path so we can import the perturbation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perturbation.date_format import (
    find_date_format_numeric,
    find_date_format_literal,
    convert_numeric_to_literal,
    convert_literal_to_numeric,
    perturb_date_format
)

class TestDateFormat(unittest.TestCase):
    def test_find_date_format_numeric(self):
        # Test finding mm/dd/yyyy format
        text = "The meeting is scheduled for 12/25/2023."
        result = find_date_format_numeric(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "12/25/2023")
        
        # Test finding mm-dd-yyyy format
        text = "The meeting is scheduled for 12-25-2023."
        result = find_date_format_numeric(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "12-25-2023")
        
        # Test finding mm.dd.yyyy format
        text = "The meeting is scheduled for 12.25.2023."
        result = find_date_format_numeric(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "12.25.2023")
        
        # Test finding mm/dd/yy format
        text = "The meeting is scheduled for 12/25/23."
        result = find_date_format_numeric(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "12/25/23")
        
        # Test no date in text
        text = "The meeting is scheduled for next week."
        result = find_date_format_numeric(text)
        self.assertIsNone(result)
    
    def test_find_date_format_literal(self):
        # Test finding Month Day, Year format
        text = "The meeting is scheduled for December 25, 2023."
        result = find_date_format_literal(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "December 25, 2023")
        
        # Test finding Month Day Year format (no comma)
        text = "The meeting is scheduled for December 25 2023."
        result = find_date_format_literal(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "December 25 2023")
        
        # Test with ordinal indicator
        text = "The meeting is scheduled for December 25th, 2023."
        result = find_date_format_literal(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "December 25th, 2023")
        
        # Test no date in text
        text = "The meeting is scheduled for next week."
        result = find_date_format_literal(text)
        self.assertIsNone(result)
    
    def test_convert_numeric_to_literal(self):
        # Test converting mm/dd/yyyy to Month Day, Year
        self.assertEqual(convert_numeric_to_literal("12/25/2023"), "December 25, 2023")
        
        # Test converting mm-dd-yyyy to Month Day, Year
        self.assertEqual(convert_numeric_to_literal("12-25-2023"), "December 25, 2023")
        
        # Test converting mm.dd.yyyy to Month Day, Year
        self.assertEqual(convert_numeric_to_literal("12.25.2023"), "December 25, 2023")
        
        # Test converting mm/dd/yy to Month Day, Year (assuming 20xx)
        self.assertEqual(convert_numeric_to_literal("12/25/23"), "December 25, 2023")
    
    def test_convert_literal_to_numeric(self):
        # Test converting Month Day, Year to mm/dd/yyyy
        self.assertEqual(convert_literal_to_numeric("December 25, 2023"), "12/25/2023")
        
        # Test converting Month Day Year to mm/dd/yyyy (no comma)
        self.assertEqual(convert_literal_to_numeric("December 25 2023"), "12/25/2023")
        
        # Test with ordinal indicator
        self.assertEqual(convert_literal_to_numeric("December 25th, 2023"), "12/25/2023")
    
    def test_perturb_date_format(self):
        # Test perturbing numeric date
        text = "The meeting is scheduled for 12/25/2023."
        result = perturb_date_format(text)
        self.assertIsNotNone(result)
        self.assertEqual(result["operation"]["Target"], "date_format")
        self.assertEqual(result["operation"]["From"], "12/25/2023")
        self.assertEqual(result["operation"]["To"], "December 25, 2023")
        self.assertEqual(result["perturbed_text"], "The meeting is scheduled for December 25, 2023.")
        
        # Test perturbing literal date
        text = "The meeting is scheduled for December 25, 2023."
        result = perturb_date_format(text)
        self.assertIsNotNone(result)
        self.assertEqual(result["operation"]["Target"], "date_format")
        self.assertEqual(result["operation"]["From"], "December 25, 2023")
        self.assertEqual(result["operation"]["To"], "12/25/2023")
        self.assertEqual(result["perturbed_text"], "The meeting is scheduled for 12/25/2023.")
        
        # Test no date in text
        text = "The meeting is scheduled for next week."
        result = perturb_date_format(text)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main() 