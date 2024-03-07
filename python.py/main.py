import pygame
from player import Player
from house import House
from house import StartingHouse
from upgrade import GuardDog, FriendlyNeighbor, HouseCleaner, Gardener, HouseRepair, Garage
from achievements import initialize_achievements
import time
import random
import sqlite3


INCOME_EVENT = pygame.USEREVENT + 1

screen_width, screen_height = 1000, 700
board_width, board_height = 280, 70
bl_center_x, bl_center_y = 50, 100
br_center_x = screen_width - board_width - 50
br_center_y = 100

FPS = 60

### Arrow ###
arr_width, arr_height = 50, 30

r_arr_x = (board_width - arr_width) / 2 + (screen_width - board_width - 50)
r_arr_up_y = br_center_y - 35
r_arr_down_y = screen_height - r_arr_up_y - 35

l_arr_x = 50 + (board_width - arr_width) / 2
l_arr_up_y = br_center_y - 35
l_arr_down_y = screen_height - l_arr_up_y - 35

class Game:
    def __init__(self):
        pygame.init()
        self.setup_screen()
        self.load_fonts()
        self.set_boards()
        self.initialize_game()
        self.active_upgrades = []
        self.upgrade_rects = []
        self.create_upgrade_rects()
        self.showing_market = False
        self.market_houses = []
        self.initial_market_houses = []
        self.load_houses_from_db()
        self.achievements = initialize_achievements()
        self.achievements_rect = []
        self.create_achievements_rects()
        self.showing_upgrades = True
        self.showing_achievements = False
        self.showing_achievement_popup = False
        self.achievement_popup_start_time = None
        self.popup_background_image = pygame.image.load('../gui/achievement.png').convert_alpha()
        self.popup_background_image = pygame.transform.scale(self.popup_background_image, (700, 150))


        pygame.time.set_timer(INCOME_EVENT, 1000)

    def load_houses_from_db(self):
        conn = sqlite3.connect('../housesDB.db')
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, price, area, rooms, year, image_path, upgrade_level, image_width, image_height, mini_width, mini_height FROM houses WHERE name != 'My House'")
        houses_data = cursor.fetchall()
        conn.close()

        for data in houses_data:
            name, price, area, rooms, year, image_path, upgrade_level, image_width, image_height, mini_image_width, mini_image_height = data
            image_size = (image_width, image_height)
            mini_size = (mini_image_width, mini_image_height)
            house = House(name, price, area, rooms, year, image_path, position=(300, 250),
                          image_size=image_size, mini_size=mini_size, upgrade=upgrade_level)
            house.rect = pygame.Rect(house.position[0], house.position[1], mini_image_width, mini_image_height)
            self.initial_market_houses.append(house)



    def buy_upgrade(self, upgrade):
        if self.money >= upgrade.base_cost:
            self.money -= upgrade.base_cost
            upgrade.purchase()
            upgrade.get_income()
            self.active_upgrades.append(upgrade)

    def buy_house(self, house):
        if house in self.player.houses:
            pass
        else:
            if self.money >= house.price and house not in self.player.houses:
                self.money -= house.price
                self.player.houses.append(house)
                if house in self.market_houses:
                    self.market_houses.remove(house)
                self.update_market_houses()



    def apply_highlight(self, image, highlight_color=(20, 20, 20), highlight_intensity=128):
        highlight_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        highlight_fill = (*highlight_color, highlight_intensity)
        highlight_surface.fill(highlight_fill)
        mask = pygame.mask.from_surface(image)
        highlighted_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)

        for x in range(image.get_width()):
            for y in range(image.get_height()):
                if mask.get_at((x, y)):
                    original_color = image.get_at((x, y))
                    new_color = pygame.Color(min(255, original_color.r + highlight_fill[0]),
                                             min(255, original_color.g + highlight_fill[1]),
                                             min(255, original_color.b + highlight_fill[2]),
                                             original_color.a)
                    highlighted_image.set_at((x, y), new_color)
                else:
                    highlighted_image.set_at((x, y), image.get_at((x, y)))
        return highlighted_image

    def load_scaled_image(self, path, width, height):
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, (width, height))

    def setup_screen(self):
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Estate Clicker")
        self.background_image = self.load_scaled_image("../gui/background.webp", screen_width, screen_height)
        self.board_image = self.load_scaled_image("../gui/title_for_board.png", board_width, board_height)
        self.screen.blit(self.background_image, (0, 0))


    def set_boards(self):
        self.board_image = self.load_scaled_image("../gui/title_for_board.png", board_width, board_height)
        self.left_board = self.board_image.get_rect(topleft=(bl_center_x, bl_center_y))
        self.right_board = self.board_image.get_rect(topleft=(br_center_x, br_center_y))

    def draw_buy_house_board(self):
        self.buy_house_board_image = self.load_scaled_image("../gui/button.png", board_width, board_height // 2)
        self.buy_house_board_rect = self.buy_house_board_image.get_rect(topleft=(br_center_x, 34))


        mouse_pos = pygame.mouse.get_pos()

        button_text = "BACK TO MY HOUSES" if self.showing_market else "BUY A HOUSE"
        name_text_surface = self.font.render(button_text, True,
                                             (171, 164, 67) if self.buy_house_board_rect.collidepoint(mouse_pos) else (
                                             252, 252, 252))
        text_rect = name_text_surface.get_rect(center=self.buy_house_board_rect.center)


        if self.buy_house_board_rect.collidepoint(mouse_pos):
            highlighted_img = self.apply_highlight(self.buy_house_board_image)
            self.screen.blit(highlighted_img, self.buy_house_board_rect.topleft)
        else:
            self.screen.blit(self.buy_house_board_image, self.buy_house_board_rect)


        self.screen.blit(name_text_surface, text_rect)

    def achievements_board(self):
        self.achievements_board_image = self.load_scaled_image("../gui/button.png", board_width, board_height // 2)
        self.achievements_board_rect = self.achievements_board_image.get_rect(topleft=(bl_center_x, 38))
        mouse_pos = pygame.mouse.get_pos()

        button_text = "UPGRADES" if self.showing_market else "ACHIEVEMENTS"
        name_text_surface = self.font.render(button_text, True,
                                             (171, 164, 67) if self.achievements_board_rect.collidepoint(
                                                 mouse_pos) else (
                                                 252, 252, 252))
        text_rect = name_text_surface.get_rect(center=self.achievements_board_rect.center)

        if self.achievements_board_rect.collidepoint(mouse_pos):
            highlighted_img = self.apply_highlight(self.achievements_board_image)
            self.screen.blit(highlighted_img, self.achievements_board_rect.topleft)
        else:
            self.screen.blit(self.achievements_board_image, self.achievements_board_rect)

        self.screen.blit(name_text_surface, text_rect)

    def load_fonts(self):
        self.font_ss = pygame.font.SysFont("Arial Black", 10)
        self.font_small = pygame.font.SysFont("Arial Black", 12)
        self.font = pygame.font.SysFont("Arial Black", 18)
        self.outline_font = pygame.font.SysFont("Arial Black", 30)

    def initialize_game(self):
        self.starting_house = StartingHouse()
        self.player = Player(self.starting_house)
        self.upgrades = [GuardDog(), FriendlyNeighbor(), HouseCleaner(), Gardener(), HouseRepair(), Garage()]


        for upgrade in self.upgrades:
            upgrade.load_images()

        # Game state variables
        self.clock = pygame.time.Clock()
        self.blink = False
        self.hover = False
        self.running = True
        self.money = 0
        self.show_money_sign = False
        self.money_sign_position = (400, 500)
        self.money_sign_start_time = None
        self.money_sign_duration = 2000
        self.money_signs = []


        #Houses scrolling setup
        self.displayed_houses_start_index = 0
        self.max_displayed_houses = 6
        # Upgrades scrolling setup
        self.displayed_upgrades_start_index = 0
        self.max_displayed_upgrades = 6

        # Setup arrow positions
        self.setup_arrows()

    def update_money(self, amount):
        # Atnaujinti pinigų kiekį
        self.money += amount


    def setup_arrows(self):
        self.arrow_down_image = self.load_scaled_image("../gui/arrow_down.png", arr_width,arr_height)
        self.arrow_up_image = self.load_scaled_image("../gui/arrow_up.png", arr_width,arr_height)
        # Calculate arrow positions based on the board dimensions
        self.right_arrow_down = self.arrow_down_image.get_rect(topleft=(r_arr_x, r_arr_down_y))
        self.right_arrow_up = self.arrow_up_image.get_rect(topleft=(r_arr_x, r_arr_up_y))
        self.left_arrow_down = self.arrow_down_image.get_rect(topleft=(l_arr_x, l_arr_down_y))
        self.left_arrow_up = self.arrow_up_image.get_rect(topleft=(l_arr_x, l_arr_up_y))

    def draw_arrows(self):

        if self.displayed_houses_start_index > 0:
            self.screen.blit(self.arrow_up_image, self.right_arrow_up)
        if self.displayed_houses_start_index + self.max_displayed_houses< len(self.player.houses):
            self.screen.blit(self.arrow_down_image, self.right_arrow_down)

        if self.displayed_upgrades_start_index > 0:
            self.screen.blit(self.arrow_up_image, self.left_arrow_up)
        if self.displayed_upgrades_start_index + self.max_displayed_upgrades< len(self.upgrades):
            self.screen.blit(self.arrow_down_image, self.left_arrow_down)

    def draw_money_signs(self):
        current_time = pygame.time.get_ticks()
        self.money_signs = [sign for sign in self.money_signs if
                            current_time - sign['start_time'] < self.money_sign_duration]
        for sign in self.money_signs:
            money_sign_text = self.font.render("+$1", True, (24, 74, 46, 255))
            self.screen.blit(money_sign_text, sign['position'])

    def draw_main_house(self, hover, blink):
        if self.hover:
            highlighted_img = self.apply_highlight(self.starting_house.image)
            self.screen.blit(highlighted_img, self.starting_house.position)
        else:
            self.screen.blit(self.starting_house.image, self.starting_house.position)

        if self.blink:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_blink_time < 200:  # Mirksėjimo trukmė 0.5 sekundės
                if (current_time - self.last_blink_time) // 100 % 2 == 0:
                    pass
                else:
                    self.screen.blit(self.starting_house.image, self.starting_house.position)
            else:
                self.blink = False

    def change_main_house_image(self, house):
        self.starting_house.image = house.image  # Pakeiskite į pasirinkto namo vaizdą
        # Atnaujinkite pagrindinio namo poziciją, jei reikia
        self.starting_house.position = (300, 250)


    def create_upgrade_rects(self):
        self.upgrade_rects = []

        for i, upgrade in enumerate(self.upgrades[
                                    self.displayed_upgrades_start_index:self.displayed_upgrades_start_index + self.max_displayed_upgrades]):
            y_pos = bl_center_y + i * 85  # Adjust based on the scroll
            rect = pygame.Rect(bl_center_x, y_pos, board_width, 85)
            # Store the upgrade and its rectangle as a dictionary
            self.upgrade_rects.append({"upgrade": upgrade, "rect": rect})


    def draw_upgrades(self):
        mouse_pos = pygame.mouse.get_pos()

        for upgrade_info in self.upgrade_rects:
            upgrade = upgrade_info['upgrade']
            rect = upgrade_info['rect']
            y_pos = rect.y
            if rect.collidepoint(mouse_pos) and self.money >= upgrade.base_cost:
                highlighted_img = self.apply_highlight(self.board_image)
                self.screen.blit(highlighted_img, rect.topleft)
            else:
                self.screen.blit(self.board_image, rect.topleft)


            if self.money >= upgrade.base_cost:
                self.screen.blit(upgrade.image, (rect.x + 10, y_pos + 5))
            else:
                dimmed_image = upgrade.image.copy()
                dimmed_image.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
                self.screen.blit(dimmed_image, (rect.x + 10, y_pos + 5))


            name_text = self.font.render(upgrade.name, True, (252, 252, 252))
            self.screen.blit(name_text, (rect.x + 80, y_pos + 7))  # Naudojame rect.x koordinatę

            cost_text = self.font.render(f"${round(upgrade.base_cost)}", True, (24, 74, 46, 255))
            self.screen.blit(cost_text, (rect.x + 80, y_pos + 27))
            next_level_potential_income = (upgrade.level + 1) * upgrade.income_increase

            potential_income_text = self.font_small.render(f"+${round(next_level_potential_income, 2)}/sec", True,(24, 74, 46, 255))
            self.screen.blit(potential_income_text, (rect.x + 80, y_pos + 50))


    def draw_houses(self):
        mouse_pos = pygame.mouse.get_pos()
        houses_to_display = self.market_houses if self.showing_market else self.player.houses
        end_index = min(self.displayed_houses_start_index + self.max_displayed_houses, len(houses_to_display))

        for i in range(self.displayed_houses_start_index, end_index):
            house = houses_to_display[i]
            y_pos = br_center_y + (i - self.displayed_houses_start_index) * 85  # Pritaikome poziciją pagal slinkimą
            house.rect = pygame.Rect(br_center_x, y_pos, board_width, board_height)
            rect = house.rect

            if rect.collidepoint(mouse_pos) and self.money >= house.price:
                highlighted_img = self.apply_highlight(self.board_image)
                self.screen.blit(highlighted_img, (br_center_x, y_pos - 5))
            else:
                self.screen.blit(self.board_image, (br_center_x, y_pos - 5))

            house_image = house.mini_image if self.money >= house.price or house in self.player.houses else house.mini_image.copy()
            house_image.fill((100, 100, 100, 128),
                             special_flags=pygame.BLEND_RGBA_MULT) if self.money < house.price and house not in self.player.houses else None

            self.screen.blit(house_image, (br_center_x, y_pos - 5))

            name_text = self.font.render(house.name, True, (252, 252, 252))


            if house not in self.player.houses:  # Jei namas nėra žaidėjo turimas, rodoma kaina
                self.screen.blit(name_text, (br_center_x + 80, y_pos + 7))

                cost_text = self.font.render(f"${round(house.price)}", True, (24, 74, 46, 255))
                self.screen.blit(cost_text, (br_center_x + 80, y_pos + 27))

                income_per_sec = (i + 1) * 10  # Pavyzdžiui, generuojama (i+1)*10 pinigų per sekundę kiekvienam namui
                income_text = self.font_small.render(f"+${income_per_sec}/sec", True, (24, 74, 46, 255))
                self.screen.blit(income_text, (br_center_x + 80, y_pos + 50))
            else:
                self.screen.blit(name_text, (br_center_x + 90, y_pos + 20))


    def update_market_houses(self):
        self.market_houses = [house for house in self.initial_market_houses if house not in self.player.houses]

    def toggle_market_view(self):
        if not self.showing_market:
            self.update_market_houses()
        self.showing_market = not self.showing_market

    def scroll_houses_up(self):
        if self.displayed_houses_start_index > 0:
            self.displayed_houses_start_index -= 1

    def scroll_houses_down(self):
        if self.displayed_houses_start_index < len(self.player.houses) - self.max_displayed_houses:
            self.displayed_houses_start_index += 1

    def scroll_upgrades_up(self):
        if self.displayed_upgrades_start_index > 0:
            self.displayed_upgrades_start_index -= 1

    def scroll_upgrades_down(self):
        if self.displayed_upgrades_start_index < len(self.upgrades) - self.max_displayed_upgrades:
            self.displayed_upgrades_start_index += 1


    def draw_money_text(self):
        money_text = f"${round(self.money)}"
        text_surface = self.outline_font.render(money_text, True, (24, 74, 46, 255))

        text_rect = text_surface.get_rect(center=(self.screen.get_rect().centerx, 50))
        self.screen.blit(text_surface, text_rect)

    def mouse_over_area(self, rect):
        mouse_pos = pygame.mouse.get_pos()
        result = rect.collidepoint(mouse_pos)
        return result

    def change_main_house_image(self, new_house_image, image_size):
        # Atnaujinti pagrindinio namo vaizdą
        self.starting_house.image = pygame.transform.scale(new_house_image, image_size)

        # Atnaujinti pagrindinio namo poziciją, kad būtų ekrano centre
        new_x = (screen_width - image_size[0]) // 2
        new_y = (screen_height - image_size[1]) // 2 + 100
        self.starting_house.position = (new_x, new_y)

    def toggle_achievements_view(self):
        self.showing_upgrades = not self.showing_upgrades
        self.showing_achievements = not self.showing_achievements

    def create_achievements_rects(self):
        self.achievements_rect = []

        for i, achievement in enumerate(self.achievements):
            y_pos = bl_center_y + i * 85
            rect = pygame.Rect(bl_center_x, y_pos, board_width, 85)
            self.achievements_rect.append({"achievement": achievement, "rect": rect})

    def draw_achievements(self):
        mouse_pos = pygame.mouse.get_pos()
        for achievement_info in self.achievements_rect:
            achievement = achievement_info["achievement"]
            rect = achievement_info["rect"]
            y_pos = rect.y

            self.screen.blit(self.board_image, rect.topleft)

            text_surface = self.font.render(f"{achievement.name}: {achievement.task}", True, (255, 255, 255))
            self.screen.blit(text_surface, (rect.x + 10, y_pos + 7))  # Naudojame rect.x koordinatę
            prize_text_surface = self.font.render(f"Prize: {achievement.income}", True, (24, 74, 46, 255))
            self.screen.blit(prize_text_surface, (rect.x + 10, y_pos + 30))

    def show_achievement_popup(self, achievement):
        self.showing_achievement_popup = True
        self.achievement_popup_start_time = pygame.time.get_ticks()
        self.current_achievement = achievement  # Saugokite esamą achievement objektą, kad galėtumėte naudoti jo duomenis vėliau

    def draw_achievement_popup(self):
        popup_rect = pygame.Rect(screen_width // 2 - 350, screen_height // 2 - 75, 700, 150)
        text_surface = self.font.render(f"Achievement {self.current_achievement.name} Unlocked, Prize: ${self.current_achievement.income}", True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=popup_rect.center)

        self.screen.blit(self.popup_background_image, popup_rect.topleft)
        self.screen.blit(text_surface, text_rect.topleft)


    def update_achievements(self):
        for achievement in self.achievements:
            if achievement.check_and_apply(self):
                self.show_achievement_popup(achievement)

    def handle_events(self):

        left_board_height = len(self.upgrades) * 85
        right_board_height = len(self.player.houses) * 85

        self.left_board = pygame.Rect(bl_center_x, bl_center_y, board_width, left_board_height)
        self.right_board = pygame.Rect(br_center_x, br_center_y, board_width, right_board_height)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == INCOME_EVENT:
                total_income_from_upgrades = sum(upgrade.get_income() for upgrade in self.active_upgrades)
                self.update_money(total_income_from_upgrades)

                total_income_from_houses = sum(house.upgrade * 10 for house in self.player.houses)
                self.update_money(total_income_from_houses)





            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.starting_house.image.get_rect(topleft=self.starting_house.position).collidepoint(event.pos):
                    self.update_money(1)
                    self.blink = True
                    self.last_blink_time = pygame.time.get_ticks()
                    mouse_x, mouse_y = event.pos
                    new_sign = {
                        'position': (mouse_x + random.randint(-100, 100),
                                     mouse_y - random.randint(-100, 100)),
                        'start_time': pygame.time.get_ticks()
                    }
                    self.money_signs.append(new_sign)

                if self.achievements_board_rect.collidepoint(event.pos):
                    self.toggle_achievements_view()

                mouse_pos = pygame.mouse.get_pos()
                if self.buy_house_board_rect.collidepoint(mouse_pos):
                    self.showing_market = not self.showing_market
                    if self.showing_market:

                        self.update_market_houses()

                for house in self.player.houses:
                    if house.rect.collidepoint(mouse_pos):
                        self.change_main_house_image(house.image, house.image_size)
                        break


                if self.mouse_over_area(self.right_arrow_up):
                    self.scroll_houses_up()
                elif self.mouse_over_area(self.right_arrow_down) :
                    self.scroll_houses_down()


                if self.mouse_over_area(self.left_arrow_up):
                    self.scroll_upgrades_up()
                elif self.mouse_over_area(self.left_arrow_down) :
                    self.scroll_upgrades_down()


                if self.mouse_over_area(self.left_board):
                    if event.button == 4:  # Scroll up
                        self.scroll_upgrades_up()
                    elif event.button == 5:  # Scroll down
                        self.scroll_upgrades_down()


                elif self.mouse_over_area(self.right_board):
                    if event.button == 4:  # Scroll up
                        self.scroll_houses_up()
                    elif event.button == 5:  # Scroll down
                        self.scroll_houses_down()

                for upgrade_info in self.upgrade_rects:
                    rect = upgrade_info["rect"]
                    if rect.collidepoint(event.pos):
                        selected_upgrade = upgrade_info["upgrade"]
                        self.buy_upgrade(selected_upgrade)

                for house in self.market_houses if self.showing_market else self.player.houses:
                    if hasattr(house, 'rect') and house.rect.collidepoint(event.pos) and self.money >= house.price:

                        self.buy_house(house)
                        self.update_market_houses()
                        break


                self.hover = self.starting_house.image.get_rect(topleft=self.starting_house.position).collidepoint(event.pos)

            elif event.type == pygame.MOUSEMOTION:
                self.hover = self.starting_house.image.get_rect(topleft=self.starting_house.position).collidepoint(
                    event.pos)

        self.clock.tick(FPS)


    def draw(self):
        self.screen.blit(self.background_image, (0, 0))
        if self.showing_upgrades:
            self.draw_upgrades()
        else:
            self.draw_achievements()

        self.draw_houses()
        self.draw_money_text()
        self.draw_main_house(self.hover, self.blink)
        self.draw_buy_house_board()
        self.achievements_board()
        self.draw_money_signs()
        self.draw_arrows()

        if self.showing_achievement_popup:
            current_time = pygame.time.get_ticks()
            if current_time - self.achievement_popup_start_time < 5000:  # Popup rodomas 3 sekundes
                self.draw_achievement_popup()
            else:
                self.showing_achievement_popup = False

        pygame.display.update()

    def update(self):
        pass

    def run(self):
        while self.running:
            self.draw()
            self.handle_events()
            self.update()
            self.update_achievements()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
