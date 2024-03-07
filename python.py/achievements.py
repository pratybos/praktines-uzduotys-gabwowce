import pygame


class Achievement:
    def __init__(self, name, income, task, check_function):
        self.name = name
        self.income = income
        self.task = task
        self.check_function = check_function
        self.completed = False

    def check_and_apply(self, game):
        if not self.completed and self.check_function(game):
            game.money += self.income
            self.completed = True
            return True
            print(f"Achievement completed: {self.name}")

def check_earn_100(game):
    return game.money >= 100


def check_buy_first_house(game):
    return len(game.player.houses) > 1

def check_earn_1000(game):
    return game.money >= 1000

def check_buy_5_house(game):
    return len(game.player.houses) > 3

def check_earn_10000(game):
    return game.money >= 10000

def initialize_achievements():
    achievements = [
        Achievement("Level1", 100, "Earn $100", check_earn_100),
        Achievement("Level2", 1000, "Buy first house", check_buy_first_house),
        Achievement("Level3", 10000, "Earn $1000", check_earn_10000),
        Achievement("Level4", 5000, "Buy 3 houses", check_buy_5_house),
        Achievement("Level5", 10000, "Earn $10000", check_earn_10000),
    ]
    return achievements



