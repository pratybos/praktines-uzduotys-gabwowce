import pygame
from upgrade import GuardDog, FriendlyNeighbor, HouseCleaner, Gardener, HouseRepair, Garage

contitions = ["New Construction", "Move-In Ready", "Cosmetic Fixes", "Needs Repairs", "Fixer-Upper", "Foreclosure or As-Is"]

class House:
    def __init__(self, name, price, area, rooms, year, image_path, position=(375, 300), image_size=(250, 300), mini_size = (50,70), upgrade=0):
        self.name = name
        self.price = price
        self.area = area
        self.rooms = rooms
        self.year = year
        self.position = position
        self.image_size = image_size
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, image_size)
        self.mini_image = pygame.image.load(image_path).convert_alpha()
        self.mini_image = pygame.transform.scale(self.image, mini_size)
        self.upgrade = upgrade
        self.rect = pygame.Rect(position[0], position[1], 280, 70)




class StartingHouse(House):
    def __init__(self):
        super().__init__(name="My House", price=10000, area=50,rooms=2, year=1995,
                                    image_path="../houses/house3.png", position = (340, 300), image_size=(330, 320), mini_size = (70,80))


class SecondHouse(House):
    def __init__(self):
        super().__init__(name="My House", price=15000, area=50,rooms=2, year=1995,
                                    image_path="../houses/house4.png", position = (340, 300), image_size=(330, 320), mini_size = (70,80))

