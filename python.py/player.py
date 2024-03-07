import pygame
from house import StartingHouse, SecondHouse

class Player:
    def __init__(self, starting_house, starting_money=1000):
        self.money = starting_money
        self.houses = [StartingHouse()]  # Pradėkite su tuščiu sąrašu namų
        self.upgrades = {}  # Pradėkite su tuščiu sąrašu patobulinimų

    def buy_house(self, house):
        if self.money >= house.price:
            self.houses.append(house)
            self.money -= house.price
            print(f"Bought {house.name} for {house.price}. Remaining money: {self.money}")
        else:
            print("Not enough money to buy this house.")

    def sell_house(self, house):
        if house in self.houses:
            self.houses.remove(house)
            self.money += house.price  # Paprastumo dėlei, grąžiname visą namo kainą
            print(f"Sold {house.name}. Money after selling: {self.money}")
        else:
            print("You don't own this house.")

    def add_money(self, amount):
        self.money += amount
        print(f"Added {amount} money. Total money: {self.money}")

    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            print(f"Spent {amount} money. Remaining money: {self.money}")
        else:
            print("Not enough money to spend.")
