class Car:
    def __init__(self, model, age, owner=None, fuel=0):
        self.model = model
        self.age = age
        self.owner = owner
        self.fuel = fuel

    def __str__(self):
        return (f"Модель: {self.model}\n"
                f"Вік: {self.age}\n"
                f"Власник: {self.owner}\n"
                f"Бензин: {self.fuel} л")

    @property
    def condition(self):
        if self.age <= 3:
            return "Нове авто"
        elif self.age <= 10:
            return "Середній стан"
        else:
            return "Старе авто"

    @property
    def fuel_status(self):
        if self.fuel >= 30:
            return "Можна їхати далеко"
        else:
            return "Потрібно заправитись"