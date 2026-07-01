from car import Car

car1 = Car("BMW X5", 2, "Іван", 40)
car2 = Car("Audi A6", 12, "Петро", 10)

# dict
print(car1.__dict__)
print(car2.__dict__)

print()

# Вивід об'єктів
print(car1)
print()
print(car2)

print()

# Зміна кількості бензину
car1.fuel = 20
car2.fuel = 50

print("Після зміни бензину:")
print(car1)
print()
print(car2)

print()

# Property
print("Стан авто 1:", car1.condition)
print("Стан авто 2:", car2.condition)

print("Бензин авто 1:", car1.fuel_status)
print("Бензин авто 2:", car2.fuel_status)

print()

# Порівняння бензину
if car1.fuel > car2.fuel:
    print(f"У {car1.model} більше бензину.")
elif car1.fuel < car2.fuel:
    print(f"У {car2.model} більше бензину.")
else:
    print("Бензину однакова кількість.")