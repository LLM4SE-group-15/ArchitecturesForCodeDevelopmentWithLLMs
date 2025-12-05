import unittest
from typing import List


class TestSumEvenNumbers(unittest.TestCase):
    """Test cases for sum_even_numbers function."""
    
    def test_mixed_numbers(self):
        """Test with mixed even and odd numbers."""
        result = sum_even_numbers([1, 2, 3, 4, 5, 6])
        self.assertEqual(result, 12)
    
    def test_all_odd(self):
        """Test with all odd numbers."""
        result = sum_even_numbers([1, 3, 5, 7])
        self.assertEqual(result, 0)
    
    def test_all_even(self):
        """Test with all even numbers."""
        result = sum_even_numbers([2, 4, 6, 8])
        self.assertEqual(result, 20)
    
    def test_empty_list(self):
        """Test with empty list."""
        result = sum_even_numbers([])
        self.assertEqual(result, 0)
    
    def test_single_even(self):
        """Test with single even number."""
        result = sum_even_numbers([4])
        self.assertEqual(result, 4)
    
    def test_negative_numbers(self):
        """Test with negative even numbers."""
        result = sum_even_numbers([-2, -4, 1, 3])
        self.assertEqual(result, -6)


if __name__ == "__main__":
    unittest.main()
