import unittest
import sys
import os

# Add the parent directory to the path so we can import the perturbation modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perturbation.number_rephrase import (
    find_literal_amount,
    find_numeric_amount,
    convert_literal_to_numeric,
    convert_numeric_to_literal,
    perturb_number_rephrase
)

class TestNumberRephrase(unittest.TestCase):
    def test_find_literal_amount(self):
        # Test finding $X million format
        text = "The company reported revenue of $14.5 million for the quarter."
        result = find_literal_amount(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "$14.5 million")
        self.assertEqual(result[1], 14.5)
        self.assertEqual(result[2], "million")
        
        # Test finding X million dollars format
        text = "The company reported revenue of 14.5 million dollars for the quarter."
        result = find_literal_amount(text)
        self.assertIsNotNone(result)
        self.assertIn("14.5 million", result[0])
        self.assertEqual(result[1], 14.5)
        self.assertEqual(result[2], "million")
        
        # Test finding other scales
        text = "The company reported revenue of $3.2 billion for the year."
        result = find_literal_amount(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "$3.2 billion")
        self.assertEqual(result[1], 3.2)
        self.assertEqual(result[2], "billion")
        
        # Test no amount in text
        text = "The company reported strong growth for the quarter."
        result = find_literal_amount(text)
        self.assertIsNone(result)
    
    def test_find_numeric_amount(self):
        # Test finding $X,XXX,XXX format
        text = "The company reported revenue of $14,500,000 for the quarter."
        result = find_numeric_amount(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "$14,500,000")
        self.assertEqual(result[1], 14500000.0)
        
        # Test finding $X,XXX,XXX.XX format
        text = "The company reported revenue of $14,500,000.50 for the quarter."
        result = find_numeric_amount(text)
        self.assertIsNotNone(result)
        self.assertEqual(result[0], "$14,500,000.50")
        self.assertEqual(result[1], 14500000.50)
        
        # Test small amounts (shouldn't match)
        text = "The item costs $500."
        result = find_numeric_amount(text)
        self.assertIsNone(result)
        
        # Test no amount in text
        text = "The company reported strong growth for the quarter."
        result = find_numeric_amount(text)
        self.assertIsNone(result)
    
    def test_convert_literal_to_numeric(self):
        # Test converting X million to $X,000,000
        self.assertEqual(convert_literal_to_numeric(14.5, "million"), "$14,500,000")
        
        # Test converting X billion to $X,000,000,000
        self.assertEqual(convert_literal_to_numeric(3.2, "billion"), "$3,200,000,000")
        
        # Test converting X thousand to $X,000
        self.assertEqual(convert_literal_to_numeric(5.1, "thousand"), "$5,100")
        
        # Test integer values
        self.assertEqual(convert_literal_to_numeric(5, "million"), "$5,000,000")
    
    def test_convert_numeric_to_literal(self):
        # Test converting large numbers to appropriate scale
        self.assertEqual(convert_numeric_to_literal(14500000), "$14.5 million")
        self.assertEqual(convert_numeric_to_literal(3200000000), "$3.2 billion")
        self.assertEqual(convert_numeric_to_literal(5100), "$5.1 thousand")
        
        # Test integer values
        self.assertEqual(convert_numeric_to_literal(5000000), "$5 million")
        
        # Test rounding
        self.assertEqual(convert_numeric_to_literal(14520000), "$14.52 million")
    
    def test_perturb_number_rephrase(self):
        # Test perturbing literal amount
        text = "The company reported revenue of $14.5 million for the quarter."
        result = perturb_number_rephrase(text)
        self.assertIsNotNone(result)
        self.assertEqual(result["operation"]["Target"], "number_rephrase")
        self.assertEqual(result["operation"]["From"], "$14.5 million")
        self.assertEqual(result["operation"]["To"], "$14,500,000")
        self.assertEqual(result["perturbed_text"], "The company reported revenue of $14,500,000 for the quarter.")
        
        # Test perturbing numeric amount
        text = "The company reported revenue of $14,500,000 for the quarter."
        result = perturb_number_rephrase(text)
        self.assertIsNotNone(result)
        self.assertEqual(result["operation"]["Target"], "number_rephrase")
        self.assertEqual(result["operation"]["From"], "$14,500,000")
        self.assertEqual(result["operation"]["To"], "$14.5 million")
        self.assertEqual(result["perturbed_text"], "The company reported revenue of $14.5 million for the quarter.")
        
        # Test no amount in text
        text = "The company reported strong growth for the quarter."
        result = perturb_number_rephrase(text)
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main() 