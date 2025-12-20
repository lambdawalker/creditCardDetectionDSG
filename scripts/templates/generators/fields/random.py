import random
import string


def choice(items):
    """
    Selects and returns a random item from either a list or string.

    Args:
        items: Either a list/array or string to choose from

    Returns:
        A random element from the input

    Raises:
        ValueError: If items is empty
        TypeError: If items is not a list or string
    """
    if not isinstance(items, (list, str)):
        raise TypeError("Input must be a list or string")

    if len(items) == 0:
        raise ValueError("Input cannot be empty")

    return random.choice(items)


def generate_hex_string(length, upper_case=True):
    """
    Generates a random hexadecimal string of specified length.

    Args:
        length: The desired length of the hex string (integer)

    Returns:
        A random hexadecimal string of the specified length

    Raises:
        ValueError: If length is negative or zero
        TypeError: If length is not an integer
    """
    if not isinstance(length, int):
        raise TypeError("Length must be an integer")

    if length <= 0:
        raise ValueError("Length must be greater than zero")

    hex_chars = string.hexdigits[16:32] if upper_case else string.hexdigits[:16]
    return ''.join(random.choice(hex_chars) for _ in range(length))


def generate_int(min=None, max=None):
    min = min if min is not None else 0
    max = max if max is not None else 1000000

    if min > max:
        t = min
        min = max
        max = t

    return random.randint(min, max)


def generate_left_just_number(min=None, max=None, total_length=None):
    """
    Generates a random number within a range and pads it with trailing zeros.

    Args:
        min_value: The minimum value (inclusive) for the random number
        max_value: The maximum value (inclusive) for the random number
        total_length: The desired total length including trailing zeros

    Returns:
        A string representing the number with trailing zeros

    Raises:
        ValueError: If min_value > max_value, or if total_length is too small
        TypeError: If arguments are not integers
    """
    number = generate_int(min, max)
    number_str = str(number)
    total_length = total_length if total_length is not None else len(str(max))

    if total_length <= 0 or total_length is None or len(number_str) > total_length:
        return number_str

    return number_str.ljust(total_length, '0')


def generate_boolean():
    return random.choice([True, False])
