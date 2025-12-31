import pytest
from calculator import add, subtract, multiply, divide, power, factorial


class TestAdd:
    """Test cases for the add function."""
    
    def test_add_positive_numbers(self):
        """Test adding two positive numbers returns correct sum."""
        result = add(3, 5)
        assert result == 8
    
    def test_add_negative_numbers(self):
        """Test adding two negative numbers returns correct sum."""
        result = add(-3, -5)
        assert result == -8
    
    def test_add_mixed_sign_numbers(self):
        """Test adding numbers with different signs."""
        result = add(10, -3)
        assert result == 7
    
    def test_add_with_zero(self):
        """Test adding zero returns the other number."""
        result = add(5, 0)
        assert result == 5
    
    def test_add_floating_point_numbers(self):
        """Test adding floating point numbers handles precision correctly."""
        result = add(1.5, 2.7)
        assert result == 4.2


class TestSubtract:
    """Test cases for the subtract function."""
    
    def test_subtract_positive_result(self):
        """Test subtracting smaller number from larger returns positive."""
        result = subtract(10, 3)
        assert result == 7
    
    def test_subtract_negative_result(self):
        """Test subtracting larger number from smaller returns negative."""
        result = subtract(3, 10)
        assert result == -7
    
    def test_subtract_to_zero(self):
        """Test subtracting equal numbers returns zero."""
        result = subtract(5, 5)
        assert result == 0
    
    def test_subtract_with_negative_numbers(self):
        """Test subtracting negative numbers."""
        result = subtract(-5, -3)
        assert result == -2
    
    def test_subtract_floating_point_numbers(self):
        """Test subtracting floating point numbers."""
        result = subtract(5.5, 2.2)
        assert result == 3.3


class TestMultiply:
    """Test cases for the multiply function."""
    
    def test_multiply_positive_numbers(self):
        """Test multiplying two positive numbers."""
        result = multiply(3, 4)
        assert result == 12
    
    def test_multiply_negative_numbers(self):
        """Test multiplying two negative numbers returns positive."""
        result = multiply(-3, -4)
        assert result == 12
    
    def test_multiply_mixed_sign_numbers(self):
        """Test multiplying numbers with different signs returns negative."""
        result = multiply(-3, 4)
        assert result == -12
    
    def test_multiply_by_zero(self):
        """Test multiplying by zero returns zero."""
        result = multiply(5, 0)
        assert result == 0
    
    def test_multiply_floating_point_numbers(self):
        """Test multiplying floating point numbers."""
        result = multiply(2.5, 4)
        assert result == 10.0


class TestDivide:
    """Test cases for the divide function."""
    
    def test_divide_positive_numbers(self):
        """Test dividing two positive numbers."""
        result = divide(10, 2)
        assert result == 5
    
    def test_divide_negative_numbers(self):
        """Test dividing two negative numbers."""
        result = divide(-10, -2)
        assert result == 5
    
    def test_divide_mixed_sign_numbers(self):
        """Test dividing numbers with different signs returns negative."""
        result = divide(-10, 2)
        assert result == -5
    
    def test_divide_floating_point_result(self):
        """Test division that results in floating point."""
        result = divide(7, 2)
        assert result == 3.5
    
    def test_divide_by_zero_raises_error(self):
        """Test dividing by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)


class TestPower:
    """Test cases for the power function."""
    
    def test_power_positive_exponent(self):
        """Test raising to positive exponent."""
        result = power(2, 3)
        assert result == 8
    
    def test_power_zero_exponent(self):
        """Test raising to zero exponent returns 1."""
        result = power(5, 0)
        assert result == 1
    
    def test_power_negative_exponent(self):
        """Test raising to negative exponent returns reciprocal."""
        result = power(2, -2)
        assert result == 0.25
    
    def test_power_base_zero(self):
        """Test raising zero to positive exponent."""
        result = power(0, 3)
        assert result == 0
    
    def test_power_floating_point_base(self):
        """Test raising floating point base to integer exponent."""
        result = power(2.5, 2)
        assert result == 6.25
    
    def test_power_exponent_one(self):
        """Test raising to exponent one returns base."""
        result = power(7, 1)
        assert result == 7


class TestFactorial:
    """Test cases for the factorial function."""
    
    def test_factorial_positive_number(self):
        """Test factorial of positive number."""
        result = factorial(5)
        assert result == 120
    
    def test_factorial_zero(self):
        """Test factorial of zero returns 1."""
        result = factorial(0)
        assert result == 1
    
    def test_factorial_one(self):
        """Test factorial of one returns 1."""
        result = factorial(1)
        assert result == 1
    
    def test_factorial_large_number(self):
        """Test factorial of larger number."""
        result = factorial(6)
        assert result == 720
    
    def test_factorial_negative_number_raises_error(self):
        """Test factorial of negative number raises ValueError."""
        with pytest.raises(ValueError, match="Factorial not defined for negative numbers"):
            factorial(-3)
