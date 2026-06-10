from functions import calculate, change_text, sum_numbers

# Завдання 1

# позиційні аргументи

print(calculate(10, 5))

# іменовані аргументи

print(calculate(a=10, b=5, operation="sub"))

# розпакування через **dict

data1 = {"a": 7, "b": 3, "operation": "sum"}

print(calculate(**data1))

# Завдання 2

# позиційні аргументи

print(change_text("Python"))

# іменовані аргументи

print(change_text(text="Python", upper=False))

# розпакування через **dict

data2 = {"text": "Hello World", "upper": True}

print(change_text(**data2))

# Завдання 3

# позиційні аргументи

print(sum_numbers("1,2,3"))

# іменовані аргументи

print(sum_numbers(numbers="4;5;6", separator=";"))

# розпакування через **dict

data3 = {"numbers": "7,8,9", "separator": ","}

print(sum_numbers(**data3))