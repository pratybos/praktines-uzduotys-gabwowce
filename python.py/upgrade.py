import pygame


class Upgrade:
    def __init__(self, name, base_cost, income_increase, image_path, image_size=(63, 60)):
        self.name = name
        self.base_cost = base_cost
        self.income_increase = income_increase
        self.level = 0
        self.image_path = image_path
        self.image = None
        self.image_size = image_size

    def load_images(self):
        self.image = pygame.image.load(self.image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.image_size)

    def purchase(self):
        self.level += 1
        # Atnaujinti kainą pagal lygį, pvz., kiekvienas lygis padidina kainą 10%
        self.base_cost *= 1.5

    def get_income(self):
        return self.level * self.income_increase


class GuardDog(Upgrade):
    def __init__(self):
        super().__init__("Guard Dog", 20, 0.2, "../upgrades/dog.png", image_size = (60, 60))

class FriendlyNeighbor(Upgrade):
    def __init__(self):
        super().__init__("Friendly Neighbor", 50, 0.3, "../upgrades/friendly.png")

class HouseCleaner(Upgrade):
    def __init__(self):
        super().__init__("House Cleaner", 100, 0.7, "../upgrades/cleaner.png")

class Gardener(Upgrade):
    def __init__(self):
        super().__init__("Gardener", 200, 1, "../upgrades/gardener.png")

class HouseRepair(Upgrade):
    def __init__(self):
        super().__init__("House repair", 300, 2, "../upgrades/tools.png")

class Garage(Upgrade):
    def __init__(self):
        super().__init__("Garage", 500, 5, "../upgrades/garage.png")



