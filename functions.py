def calculate(a: int | float, b: int | float, operation: str = "sum") -> int | float:

    if operation == "sub":

        return a - b

    return a + b

def change_text(text: str, upper: bool = True) -> str:

    if upper:

        return text.upper()

    return text.lower()

def sum_numbers(numbers: str, separator: str = ",") -> int:

    nums = numbers.split(separator)

    total = 0

    for num in nums:

        total += int(num)

    return total