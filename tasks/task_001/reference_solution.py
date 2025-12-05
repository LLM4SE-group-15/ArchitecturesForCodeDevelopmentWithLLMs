from typing import List


def sum_even_numbers(numbers: List[int]) -> int:
    """
    Calculate the sum of all even numbers in a list.
    
    Args:
        numbers: List of integers
        
    Returns:
        Sum of even numbers
        
    Examples:
        >>> sum_even_numbers([1, 2, 3, 4, 5, 6])
        12
        >>> sum_even_numbers([1, 3, 5])
        0
    """
    return sum(num for num in numbers if num % 2 == 0)
