from transport import Car, Truck, Motorcycle, ServiceStation

car = Car("BMW")
truck = Truck("MAN")
motorcycle = Motorcycle("Honda")

print(car)
print(truck)
print(motorcycle)

print(car.is_working)
print(car.__dict__)

car.move(15)
truck.move(30)
motorcycle.move(10)

motorcycle.fuel = 0
motorcycle.move(5)

truck.condition = 10
truck.move(5)

service = ServiceStation()

service.repair(truck)
print(truck)

service.repair(car)
service.repair(car)
print(car)