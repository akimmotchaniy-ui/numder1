# Завдання 1

numbers = [1, 5, 2, 8, 3, 7]

max_num = numbers[0]
min_num = numbers[0]
sum_num = 0

for num in numbers:
    if num > max_num:
        max_num = num

    if num < min_num:
        min_num = num

    sum_num += num

print("Найбільше число:", max_num)
print("Найменше число:", min_num)
print("Сума всіх чисел:", sum_num)


# Завдання 2

grades = [10, 8, 12, 7, 9]

sum_grades = 0

for grade in grades:
    sum_grades += grade

average = sum_grades / len(grades)

print("Середній бал:", average)
print("Оцінки вище середнього:")

for grade in grades:
    if grade > average:
        print(grade)