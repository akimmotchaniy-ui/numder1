from abc import ABC, abstractmethod


class Transport(ABC):
    def __init__(self, fuel, condition):
        self.fuel = fuel
        self.condition = condition

    @property
    def is_working(self):
        return self.condition > 30

    @abstractmethod
    def __str__(self):
        pass

    def move(self, distance):
        if not self.is_working:
            print("Транспорт зламаний")
            return

        if self.fuel < distance:
            print("Немає пального")
            return

        self.fuel -= distance
        self.condition -= 5

        if self.condition < 0:
            self.condition = 0

        print("Проїхав", distance, "км")


class Car(Transport):
    def __init__(self, model):
        super().__init__(50, 100)
        self.model = model

    def __str__(self):
        return f"Car {self.model}, fuel={self.fuel}, condition={self.condition}"


class Truck(Transport):
    def __init__(self, name):
        super().__init__(120, 100)
        self.name = name

    def __str__(self):
        return f"Truck {self.name}, fuel={self.fuel}, condition={self.condition}"


class Motorcycle(Transport):
    def __init__(self, brand):
        super().__init__(20, 100)
        self.brand = brand

    def __str__(self):
        return f"Motorcycle {self.brand}, fuel={self.fuel}, condition={self.condition}"


class ServiceStation:
    def repair(self, transport_unit):
        transport_unit.condition += 20
        if transport_unit.condition > 100:
            transport_unit.condition = 100