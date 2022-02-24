import os
import sys
import time

import pygame

from bd_file import Help_db

pygame.init()
hits = None
FPS = 10
WIDTH = 800
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
# helper = None
helper = Help_db()

winner = ''
all_sprites = pygame.sprite.Group()
green_tank = pygame.sprite.Group()
blue_tank = pygame.sprite.Group()
bullets = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
wall_group = pygame.sprite.Group()


def terminate():  # Экстреный выход из програмы
    pygame.quit()
    sys.exit()


def load_level(filename):
    fullname = os.path.join(filename)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с картой '{fullname}' не найден")
        terminate()
    # читаем уровень, убирая символы перевода строки
    with open(fullname, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def load_image(name, color_key=None):
    fullname = os.path.join(name)
    try:
        image = pygame.image.load(fullname).convert()
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
    # вернем игрока, а также размер поля в клетках
    return x, y


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        if tile_type == 'wall':
            super().__init__(wall_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)


class AnimatedSprite(pygame.sprite.Sprite):  # Основной класс, в котором прописана: анимация, движения танков.
    def __init__(self, x, y, lastMove, color="green"):
        if color == "green":
            super().__init__(all_sprites, green_tank)
            self.group = green_tank
        else:
            super().__init__(all_sprites, blue_tank)
            self.group = blue_tank
        super().__init__(tiles_group, all_sprites)
        self.tiles_group = tiles_group
        self.speed = 5
        self.lastMove = lastMove
        self.set_images(color)
        self.set_image()
        self.update_image()
        self.rect = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.rect = self.rect.move(x, y)
        self.rect.centerx = self.rect.x
        self.rect.bottom = self.rect.y
        self.next_wall = None

    def set_images(self, color):  # Анимация танков
        if color == "green":
            self.images_up = [
                load_image("image/tank1.png", -1), load_image("image/tank2.png", -1), load_image("image/tank3.png", -1),
                load_image("image/tank4.png", -1), load_image("image/tank5.png", -1), load_image("image/tank6.png", -1),
                load_image("image/tank7.png", -1), load_image("image/tank8.png", -1),
            ]
            self.images_right = [
                load_image('image/tank_right1.png', -1), load_image('image/tank_right2.png', -1),
                load_image('image/tank_right3.png', -1),
                load_image('image/tank_right4.png', -1), load_image('image/tank_right5.png', -1),
                load_image('image/tank_right6.png', -1), load_image('image/tank_right7.png', -1),
                load_image('image/tank_right8.png', -1)]

            self.images_left = [load_image('image/tank_laft1.png', -1), load_image('image/tank_laft2.png', -1),
                                load_image('image/tank_laft3.png', -1),
                                load_image('image/tank_laft4.png', -1), load_image('image/tank_laft5.png', -1),
                                load_image('image/tank_laft6.png', -1),
                                load_image('image/tank_laft7.png', -1), load_image('image/tank_laft8.png', -1)]

            self.images_down = [load_image('image/tank_back1.png', -1), load_image('image/tank_back2.png', -1),
                                load_image('image/tank_back3.png', -1),
                                load_image('image/tank_back4.png', -1), load_image('image/tank_back5.png', -1),
                                load_image('image/tank_back6.png', -1),
                                load_image('image/tank_back7.png', -1), load_image('image/tank_back8.png', -1)]
        else:
            self.images_down = [load_image('image/tank_blue1.png', -1), load_image('image/tank_blue2.png', -1),
                                load_image('image/tank_blue3.png', -1),
                                load_image('image/tank_blue4.png', -1), load_image('image/tank_blue5.png', -1),
                                load_image('image/tank_blue6.png', -1),
                                load_image('image/tank_blue7.png', -1), load_image('image/tank_blue8.png', -1)]
            self.images_up = [load_image('image/tank_blue_back1.png', -1), load_image('image/tank_blue_back2.png', -1),
                              load_image('image/tank_blue_back3.png', -1),
                              load_image('image/tank_blue_back4.png', -1), load_image('image/tank_blue_back5.png', -1),
                              load_image('image/tank_blue_back6.png', -1),
                              load_image('image/tank_blue_back7.png', -1), load_image('image/tank_blue_back8.png', -1)]

            self.images_left = [load_image('image/tank_blue_laft1.png', -1),
                                load_image('image/tank_blue_laft2.png', -1),
                                load_image('image/tank_blue_laft3.png', -1),
                                load_image('image/tank_blue_laft4.png', -1),
                                load_image('image/tank_blue_laft5.png', -1),
                                load_image('image/tank_blue_laft6.png', -1),
                                load_image('image/tank_blue_laft7.png', -1),
                                load_image('image/tank_blue_laft8.png', -1)]

            self.images_right = [load_image('image/tank_blue_right1.png', -1),
                                 load_image('image/tank_blue_right2.png', -1),
                                 load_image('image/tank_blue_right3.png', -1),
                                 load_image('image/tank_blue_right4.png', -1),
                                 load_image('image/tank_blue_right5.png', -1),
                                 load_image('image/tank_blue_right6.png', -1),
                                 load_image('image/tank_blue_right7.png', -1),
                                 load_image('image/tank_blue_right8.png', -1)]

    def set_image(self):
        self.count = 0
        self.image = self.images_up[self.count % len(self.images_up)]
        self.direction = "up"

    def update_image(self):  # Отрисовывает танки в зависимости от направления движени
        if self.direction == "up":
            self.image = self.images_up[self.count % len(self.images_up)]
        elif self.direction == "down":
            self.image = self.images_down[self.count % len(self.images_down)]
        elif self.direction == "left":
            self.image = self.images_left[self.count % len(self.images_left)]
        elif self.direction == "right":
            self.image = self.images_right[self.count % len(self.images_right)]
        elif self.direction == "stop":  # При остановки танк смотрит в направление последнего движения
            if self.lastMove == 'up':
                self.image = self.images_up[0]

            elif self.lastMove == 'left':
                self.image = self.images_left[0]

            elif self.lastMove == 'right':
                self.image = self.images_right[0]

            elif self.lastMove == 'down':
                self.image = self.images_down[0]
        self.count += 1

    def update(self):
        self.update_image()

    def move(self, direction, lastMove):  # Движения танков
        self.direction = direction
        self.lastMove = lastMove
        if not self.next_wall:
            if self.direction == "up":
                self.rect.y -= self.speed
            elif self.direction == "down":
                self.rect.y += self.speed
            elif self.direction == "left":
                self.rect.x -= self.speed
            elif self.direction == "right":
                self.rect.x += self.speed
            elif self.direction == "stop":
                self.rect.x += 0
                self.rect.y += 0
            self.colision()

    def shot(self, color='green'):  # Выстрел танков
        if self.lastMove == 'up':
            bullet = Bullet(self.rect.centerx, self.rect.top, self.lastMove, color)
            all_sprites.add(bullet)
            bullets.add(bullet)
        elif self.lastMove == 'down':
            bullet = Bullet(self.rect.centerx, self.rect.bottom + 10, self.lastMove, color)
            all_sprites.add(bullet)
            bullets.add(bullet)
        elif self.lastMove == 'left':
            bullet = Bullet(self.rect.topleft[0] - 5, self.rect.topleft[1] + 29, self.lastMove, color)
            all_sprites.add(bullet)
            bullets.add(bullet)
        elif self.lastMove == 'right':
            bullet = Bullet(self.rect.topright[0] + 10, self.rect.topright[1] + 29, self.lastMove, color)
            all_sprites.add(bullet)
            bullets.add(bullet)

    def colision(self):
        another_tank = pygame.sprite.spritecollideany(self,
                                                      blue_tank if self.group == green_tank else green_tank)
        wall = pygame.sprite.spritecollideany(self, wall_group)
        if another_tank or wall:
            if self.direction == "up":
                self.rect.y += self.speed
            elif self.direction == "down":
                self.rect.y -= self.speed
            elif self.direction == "left":
                self.rect.x += self.speed
            elif self.direction == "right":
                self.rect.x -= self.speed


class Bullet(pygame.sprite.Sprite):  # Класс реализует полет пуль
    def __init__(self, x, y, lastMove, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 10))
        self.image.fill('YELLOW')
        self.color = color
        self.rect = self.image.get_rect()
        self.lastMove = lastMove
        self.rect.bottom = y
        self.rect.centerx = x
        if lastMove == 'up':
            self.speedx = 0
            self.speedy = -10
        elif lastMove == 'down':
            self.speedx = 0
            self.speedy = 10
        elif lastMove == 'left':
            self.speedx = -10
            self.speedy = 0
        elif lastMove == 'right':
            self.speedx = 10
            self.speedy = 0

    def update(self):  # Обновление пули иудаление их при встречи с стенками
        global blue_bulletss
        global green_bulletss
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.color == 'green':
            if pygame.sprite.spritecollideany(self, wall_group):
                self.kill()
                green_bulletss += 1
        elif self.color == 'blue':
            if pygame.sprite.spritecollideany(self, wall_group):
                self.kill()
                blue_bulletss += 1


tile_images = {
    'wall': load_image('image/wall.png'),
    'empty': load_image('image/floor.png')
}

tile_width = tile_height = 50

# группы спрайтов

blue_bulletss = 4
green_bulletss = 4
pygame.init()
choose_map = None
sprite = pygame.sprite.Sprite()


# начальное меню
class Otobraz:
    def __init__(self):
        # создание окна
        size = width, height = 800, 800
        pygame.display.set_caption("Танчики")
        self.choose_map = choose_map
        self.map_1_size = None
        self.map_2_size = None
        self.back_work_bd = None
        self.back_work_map = None
        self.choose_rezhim = 'Обычный'
        # отрисование меню
        self.draw_menu(width, height)
        # запуск цикла
        self.game(screen, width, height)

    # Основная функция
    def game(self, screen, width, height):
        game_start = False
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # проверка что мы не меню "Данные боя"
                    if self.back_work_bd:
                        if (self.list_fight[0] < event.pos[0] < self.list_fight[2] + self.list_fight[0] and
                                self.list_fight[1] < event.pos[1] < self.list_fight[3] + self.list_fight[1]):
                            self.draw_menu(width, height)
                            draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                            self.back_work_bd = None
                        if (self.cleat[0] < event.pos[0] < self.cleat[2] + self.cleat[0] and
                                self.cleat[1] < event.pos[1] < self.cleat[3] + self.cleat[1]):
                            helper.delete_db()
                            self.draw_list(width, height)
                    elif self.back_work_map:
                        if (self.list_bak[0] < event.pos[0] < self.list_bak[2] + self.list_bak[0] and
                                self.list_bak[1] < event.pos[1] < self.list_bak[3] + self.list_bak[1]):
                            self.draw_menu(width, height)
                            # draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                            self.back_work_map = None
                        if self.map_1_size:
                            x_map_1 = self.map_1_size[0]
                            y_map_1 = self.map_1_size[1]
                            x1_map_1 = x_map_1 + self.map_1_size[2]
                            y1_map_1 = y_map_1 + self.map_1_size[3]
                            # проверка, что выбрана карта один
                            if x_map_1 < event.pos[0] < x1_map_1 and y_map_1 < event.pos[1] < y1_map_1:
                                self.choose_map = 'map_1'
                                # choose_map = self.choose_map
                                draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                        if self.map_2_size:
                            x_map_2 = self.map_2_size[0]
                            y_map_2 = self.map_2_size[1]
                            x2_map_2 = x_map_2 + self.map_2_size[2]
                            y2_map_2 = y_map_2 + self.map_2_size[3]
                            # проверка, что выбрана карта два
                            if x_map_2 < event.pos[0] < x2_map_2 and y_map_2 < event.pos[1] < y2_map_2:
                                self.choose_map = 'map_2'
                                # choose_map = self.choose_map
                                draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                        if self.map_3_size:
                            x_map_3 = self.map_3_size[0]
                            y_map_3 = self.map_3_size[1]
                            x1_map_3 = x_map_3 + self.map_3_size[2]
                            y1_map_3 = y_map_3 + self.map_3_size[3]
                            # проверка, что выбрана карта один
                            if x_map_3 < event.pos[0] < x1_map_3 and y_map_3 < event.pos[1] < y1_map_3:
                                self.choose_map = 'map_1'
                                # choose_map = self.choose_map
                                draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                        if self.map_4_size:
                            x_map_4 = self.map_4_size[0]
                            y_map_4 = self.map_4_size[1]
                            x2_map_4 = x_map_4 + self.map_4_size[2]
                            y2_map_4 = y_map_4 + self.map_4_size[3]
                            # проверка, что выбрана карта два
                            if x_map_4 < event.pos[0] < x2_map_4 and y_map_4 < event.pos[1] < y2_map_4:
                                self.choose_map = 'map_2'
                                # choose_map = self.choose_map
                                draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)

                    else:
                        x = self.start_game_btn_coords[0]
                        y = self.start_game_btn_coords[1]
                        x1 = x + self.start_game_btn_coords[2]
                        y1 = y + self.start_game_btn_coords[3]
                        if self.map_1_size:
                            x_map_1 = self.map_1_size[0]
                            y_map_1 = self.map_1_size[1]
                            x1_map_1 = x_map_1 + self.map_1_size[2]
                            y1_map_1 = y_map_1 + self.map_1_size[3]
                            # проверка, что выбрана карта один
                            if x_map_1 < event.pos[0] < x1_map_1 and y_map_1 < event.pos[1] < y1_map_1:
                                self.choose_map = 'map_1'
                                # choose_map = self.choose_map
                                draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                        if self.map_2_size:
                            x_map_2 = self.map_2_size[0]
                            y_map_2 = self.map_2_size[1]
                            x2_map_2 = x_map_2 + self.map_2_size[2]
                            y2_map_2 = y_map_2 + self.map_2_size[3]
                            # проверка, что выбрана карта два
                            if x_map_2 < event.pos[0] < x2_map_2 and y_map_2 < event.pos[1] < y2_map_2:
                                self.choose_map = 'map_2'
                                # choose_map = self.choose_map
                                draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                        # проверка, что нажата кнопка "Данные боя"
                        if (self.list_fight[0] < event.pos[0] < self.list_fight[2] + self.list_fight[0] and
                                self.list_fight[1] < event.pos[1] < self.list_fight[3] + self.list_fight[1]):
                            self.draw_list(width, height)
                        if (self.map_coords[0] < event.pos[0] < self.map_coords[2] +
                                self.map_coords[0] and
                                self.map_coords[1] < event.pos[1] < self.map_coords[3] +
                                self.map_coords[1]):
                            self.chose_map_func()
                        if (self.chance_btn_coords[0] < event.pos[0] < self.chance_btn_coords[2] +
                                self.chance_btn_coords[0] and
                                self.chance_btn_coords[1] < event.pos[1] < self.chance_btn_coords[3] +
                                self.chance_btn_coords[1]):
                            if self.choose_rezhim == 'Обычный':
                                self.choose_rezhim = 'Захват флага'
                                self.draw_menu(width, height)
                                draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                            elif self.choose_rezhim == 'Захват флага':
                                self.choose_rezhim = 'Обычный'
                                self.draw_menu(width, height)
                                draw_lvl(screen, self.choose_map, self.map_1_size, self.map_2_size)
                        # проверка, что нажата кнопка "Играть"
                        if x < event.pos[0] < x1 and y < event.pos[1] < y1:
                            # вызываем ошибку, если не выбрана карта
                            if not self.choose_map:
                                self.error(screen, width, height)
                            else:
                                # в противном случае запускаем игру
                                main(screen, self.choose_map, self.choose_rezhim)
                                game_start = True
                                break
            pygame.display.flip()
            if game_start:
                break

    def chose_map_func(self):
        screen.blit(background, (0, 0))
        font_txt = pygame.font.Font(None, 35)
        txt_back = font_txt.render('Назад', True, (255, 255, 100))
        screen.blit(txt_back, (25, 45))
        self.list_bak = (txt_back.get_width() - 60, txt_back.get_height() + 10,
                           txt_back.get_width() + 20, txt_back.get_height() + 20)
        pygame.draw.rect(screen, (255, 255, 0), self.list_bak, 1)
        self.back_work_map = True
        self.map_1_size = (800 - 670, 800 - 650, 208, 206)
        pygame.draw.rect(screen, (0, 0, 0), self.map_1_size, 0)
        screen.blit(map_1_ig, (800 - 666, 800 - 646))
        self.map_2_size = (800 - 341, 800 - 650, 208, 206)
        pygame.draw.rect(screen, (0, 0, 0), self.map_2_size, 0)
        screen.blit(map_2_ig, (800 - 337, 800 - 646))
        self.map_3_size = (800 - 670, 800 - 400, 208, 206)
        pygame.draw.rect(screen, (0, 0, 0), self.map_3_size, 0)
        screen.blit(map_3_ig, (800 - 666, 800 - 396))
        self.map_4_size = (800 - 341, 800 - 400, 208, 206)
        pygame.draw.rect(screen, (0, 0, 0), self.map_4_size, 0)
        screen.blit(map_4_ig, (800 - 337, 800 - 396))
        font = pygame.font.Font(None, 50)
        text = font.render("Выбор карты", True, (255, 255, 100))
        text_x = 800 // 2 - text.get_width() // 2
        screen.blit(text, (text_x, 50))

    # функция отрисовки "Данные боя"
    def draw_list(self, width, height):
        screen.blit(background, (0, 0))
        font_txt = pygame.font.Font(None, 35)
        txt_back = font_txt.render('Назад', True, (255, 255, 100))
        screen.blit(txt_back, (25, 45))
        self.list_fight = (txt_back.get_width() - 60, txt_back.get_height() + 10,
                           txt_back.get_width() + 20, txt_back.get_height() + 20)
        pygame.draw.rect(screen, (255, 255, 0), self.list_fight, 1)
        x = txt_back.get_width() * 2 - 40
        # создание таблицы
        pygame.draw.rect(screen, (255, 255, 0), (x, 80, width - x * 2, height - 160), 1)
        pygame.draw.line(screen, (255, 255, 0), (x, 160), (width - x, 160), 1)
        pygame.draw.line(screen, (255, 255, 0), (x, 240), (width - x, 240), 1)
        pygame.draw.line(screen, (255, 255, 0), (x, 320), (width - x, 320), 1)
        pygame.draw.line(screen, (255, 255, 0), (x, 400), (width - x, 400), 1)
        pygame.draw.line(screen, (255, 255, 0), (x, 480), (width - x, 480), 1)
        pygame.draw.line(screen, (255, 255, 0), (x, 560), (width - x, 560), 1)
        pygame.draw.line(screen, (255, 255, 0), (x, 640), (width - x, 640), 1)
        pygame.draw.line(screen, (255, 255, 0), (x, 720), (width - x, 720), 1)
        pygame.draw.line(screen, (255, 255, 0), (x + 280, 80), (x + 280, 720), 1)
        pygame.draw.line(screen, (255, 255, 0), (x + 280, 80), (x + 280, 720), 1)
        pygame.draw.line(screen, (255, 255, 0), (x + 430, 80), (x + 430, 720), 1)
        txt_1 = font_txt.render('Победитель', True, (255, 255, 100))
        screen.blit(txt_1, (255 - txt_1.get_width() / 2, 110))
        txt_2 = font_txt.render('Время игры', True, (255, 255, 100))
        screen.blit(txt_2, (395, 110))
        txt_3 = font_txt.render('Кол-во', True, (255, 255, 100))
        screen.blit(txt_3, (570, 97))
        txt_4 = font_txt.render('выстрелов', True, (255, 255, 100))
        screen.blit(txt_4, (550, 123))
        self.back_work_bd = True
        data = helper.vivod()
        count = 0
        # заполнение данных
        for i in data[::-1]:
            if count == 7:
                break
            txt = font_txt.render(str(i[3]), True, (255, 255, 100))
            screen.blit(txt, (323 - txt.get_width(), count * 80 + 190))
            txt = font_txt.render(str(i[1]), True, (255, 255, 100))
            screen.blit(txt, (490 - txt.get_width(), count * 80 + 190))
            txt = font_txt.render(str(i[2]), True, (255, 255, 100))
            screen.blit(txt, (620 - txt.get_width(), count * 80 + 190))
            count += 1
        txt_clear = font_txt.render('Очистить историю', True, (255, 255, 100))
        screen.blit(txt_clear, (width - 250, height - 45))
        self.cleat = (800 - txt_clear.get_width() - 35, 800 - txt_clear.get_height() - 30,
                      txt_clear.get_width() + 20, txt_clear.get_height() + 20)
        pygame.draw.rect(screen, (255, 255, 0), self.cleat, 1)
        # First level screen
        # обновляешь экран, формируешь новую картинку, новый игровой цикл,

    # функция ошибки
    def error(self, screen, width, height):
        font = pygame.font.Font(None, 50)
        text = font.render("Вы не выбрали карту", True, (255, 0, 0))
        text_x = width // 2 - text.get_width() // 2
        screen.blit(text, (text_x, height - 230))

    # фунция меню
    def draw_menu(self, width, height):
        screen.blit(background, (0, 0))
        screen.blit(background, (0, 0))
        font = pygame.font.Font(None, 50)
        font_txt = pygame.font.Font(None, 35)
        text = font.render("Танчики", True, (255, 255, 100))
        rezhim = font.render("Режим: " + self.choose_rezhim, True, (255, 255, 100))
        text_rezhim = width // 2 - rezhim.get_width() // 2
        text_start = font.render("Играть", True, (255, 255, 100))
        chance = font_txt.render('Сменить режим', True, (255, 255, 100))
        text_chance = width // 2 - text.get_width() // 2 - 22
        text_x = width // 2 - text.get_width() // 2
        text_x_start = width // 2 - text_start.get_width() // 2
        text_y = height - 155 - text_start.get_height() // 2
        text_w = text_start.get_width()
        text_h = text_start.get_height()
        screen.blit(rezhim, (text_rezhim, 160))
        screen.blit(text, (text_x, 50))
        txt_map = font_txt.render('Выбрать карту', True, (255, 255, 100))
        screen.blit(txt_map, (width // 2 - txt_map.get_width() // 2, height - 400))
        self.map_coords = (txt_map.get_width() + 125, 390,
                                  txt_map.get_width() + 20, txt_map.get_height() + 20)
        pygame.draw.rect(screen, (255, 255, 0), self.map_coords, 1)
        screen.blit(chance, (text_chance, screen.get_height() - 300))
        self.chance_btn_coords = (text_chance - 10, screen.get_height() - 300 - chance.get_height() // 2,
                                  chance.get_width() + 20, chance.get_height() + 20)
        pygame.draw.rect(screen, (255, 255, 0), self.chance_btn_coords, 1)
        screen.blit(text_start, (text_x_start, screen.get_height() - 220))
        self.start_game_btn_coords = (text_x_start - 10, text_y - 60,
                                      text_w + 20, text_h + 20)
        pygame.draw.rect(screen, (255, 255, 0), self.start_game_btn_coords, 1)
        txt_fight = font_txt.render('Данные боя', True, (255, 255, 100))
        screen.blit(txt_fight, (width // 2 - txt_fight.get_width() // 2, height - 150))
        self.list_fight = (width // 2 - txt_fight.get_width() // 2 - 10, height - 160,
                           txt_fight.get_width() + 20, txt_fight.get_height() + 20)
        pygame.draw.rect(screen, (255, 255, 0), self.list_fight, 1)


# финальная заставка
class Final_menu:
    def __init__(self, times, bullet, winner='12'):
        size = width, height = 800, 800
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Тесты")
        times = times[:4]
        self.game(screen, width, height, winner, times, bullet)

    # основная функция
    def game(self, screen, width, height, winner, time, bullet):
        self.draw_menu(screen, width, height, winner, time, bullet)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (self.list_fight[0] < event.pos[0] < self.list_fight[2] + self.list_fight[0] and
                            self.list_fight[1] < event.pos[1] < self.list_fight[3] + self.list_fight[1]):
                        Otobraz()
            pygame.display.flip()

    # отрисовка меню
    def draw_menu(self, screen, width, height, winner, time, bullet):
        helper.add_db(time, bullet, winner)
        screen.blit(background, (0, 0))
        font_end = pygame.font.Font(None, 75)
        font = pygame.font.Font(None, 50)
        font_text = pygame.font.Font(None, 35)
        text = font_end.render("Игра окончена", True, (0, 0, 0))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 2 - 350
        if winner == 'Зеленый танк':
            text_winner = font.render(winner + ' выиграл ', True, (0, 255, 0))
        else:
            text_winner = font.render(winner + ' выиграл ', True, (0, 0, 255))
        x_win = width // 2 - text_winner.get_width() // 2
        y_win = height // 2 - 210
        text_time = font_text.render('Время боя: ' + time, True, (255, 255, 0))
        x_time = width // 2 - text_time.get_width() // 2
        y_time = height // 2 - 100
        text_bullet = font_text.render('Количество выстрелов: ' + bullet, True, (255, 255, 0))
        x_bullet = width // 2 - text_bullet.get_width() // 2
        y_bullet = height // 2
        screen.blit(text, (text_x, text_y))
        screen.blit(text_winner, (x_win, y_win))
        screen.blit(text_time, (x_time, y_time))
        screen.blit(text_bullet, (x_bullet, y_bullet))
        txt_back = font.render('В меню', True, (255, 255, 100))
        screen.blit(txt_back, (width // 2 - txt_back.get_width() // 2, height // 2 + 250))
        self.list_fight = (width // 2 - txt_back.get_width() // 2 - 15, height // 2 + 240,
                           txt_back.get_width() + 25, txt_back.get_height() + 20)
        pygame.draw.rect(screen, (255, 255, 0), self.list_fight, 1)


# отрисовка смены карт
def draw_lvl(screen, choose_maps, maps_1, maps_2):
    if choose_maps:
        if choose_maps == 'map_1':
            pygame.draw.rect(screen, (255, 0, 0), maps_1, 0)
            pygame.draw.rect(screen, (0, 0, 0), maps_2, 0)
            pygame.draw.rect(screen, (0, 0, 0), maps_2, 0)
            screen.blit(map_1_ig, (800 - 666, 800 - 646))
            screen.blit(map_2_ig, (800 - 337, 800 - 646))

        if choose_maps == 'map_2':
            pygame.draw.rect(screen, (0, 0, 0), maps_1, 0)
            pygame.draw.rect(screen, (0, 0, 0), maps_1, 1)
            pygame.draw.rect(screen, (255, 0, 0), maps_2, 0)
            screen.blit(map_1_ig, (800 - 666, 800 - 646))
            screen.blit(map_2_ig, (800 - 337, 800 - 646))
        pygame.display.flip()


# Основная функция, которая отрисовывает все
def main(screen, maps, rezhim):
    tit1 = time.time()
    global green_tank
    global all_sprites
    global blue_tank
    global bullets
    global wall_group
    global blue_bulletss
    global green_bulletss
    clock = pygame.time.Clock()
    lastMove_blue = 'down'
    lastMove_green = 'up'
    running = True
    blue_bulletss = 0
    green_bulletss = 0
    green_bulletss = 4
    blue_bulletss = 4
    col_bullets_for_play = 0
    # отрисовывается выбранная карта и танки
    if maps == 'map_1':
        level_x, level_y = generate_level(load_level('map/map.txt'))
        dragon = AnimatedSprite(375, 750, lastMove_green)
        dragon2 = AnimatedSprite(425, 108, lastMove_blue, color="blue")
    else:
        level_x, level_y = generate_level(load_level('map/map4.txt'))
        dragon = AnimatedSprite(725, 750, lastMove_green)
        dragon2 = AnimatedSprite(75, 108, lastMove_blue, color="blue")
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    if green_bulletss > 0:
                        green_bulletss -= 1
                        col_bullets_for_play += 1
                        dragon.shot(color='green')

                elif event.key == pygame.K_x:
                    if blue_bulletss > 0:
                        blue_bulletss -= 1
                        col_bullets_for_play += 1
                        dragon2.shot(color='blue')

        # Регистрация попадания пуль в танки
        hits = pygame.sprite.groupcollide(blue_tank, bullets, True, True)
        hit = pygame.sprite.groupcollide(green_tank, bullets, True, True)
        if rezhim == 'Обычный':
            if hits:
                winner = 'Зеленый танк'
                bullets = pygame.sprite.Group()
                all_sprites = pygame.sprite.Group()
                wall_group = pygame.sprite.Group()
                blue_tank = pygame.sprite.Group()
                green_tank = pygame.sprite.Group()
                blue_bulletss = 0
                green_bulletss = 0
                tit2 = time.time()
                Final_menu(str(tit2 - tit1), str(col_bullets_for_play), winner)

            elif hit:
                bullets = pygame.sprite.Group()
                all_sprites = pygame.sprite.Group()
                wall_group = pygame.sprite.Group()
                blue_tank = pygame.sprite.Group()
                green_tank = pygame.sprite.Group()
                winner = 'Синий танк'
                blue_bulletss = 0
                green_bulletss = 0

                tit2 = time.time()
                Final_menu(str(tit2 - tit1), str(col_bullets_for_play), winner)
        elif rezhim == 'Захват флага':
            if hits:
                winner = 'Зеленый танк'
                bullets = pygame.sprite.Group()
                all_sprites = pygame.sprite.Group()
                wall_group = pygame.sprite.Group()
                blue_tank = pygame.sprite.Group()
                green_tank = pygame.sprite.Group()
                blue_bulletss = 0
                green_bulletss = 0
                main(screen, maps, rezhim)

            elif hit:
                bullets = pygame.sprite.Group()
                all_sprites = pygame.sprite.Group()
                wall_group = pygame.sprite.Group()
                blue_tank = pygame.sprite.Group()
                green_tank = pygame.sprite.Group()
                winner = 'Синий танк'
                blue_bulletss = 0
                green_bulletss = 0
                main(screen, maps, rezhim)

        # Управление
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            lastMove_green = 'up'
            dragon.move("up", lastMove_green)

        elif keys[pygame.K_DOWN]:
            lastMove_green = 'down'
            dragon.move("down", lastMove_green)

        elif keys[pygame.K_LEFT]:
            lastMove_green = 'left'
            dragon.move("left", lastMove_green)

        elif keys[pygame.K_RIGHT]:
            lastMove_green = 'right'
            dragon.move("right", lastMove_green)

        elif not keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            if not keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
                dragon.move("stop", lastMove_green)

        if keys[pygame.K_w]:
            lastMove_blue = 'up'
            dragon2.move("up", lastMove_blue)

        elif keys[pygame.K_s]:
            lastMove_blue = 'down'
            dragon2.move("down", lastMove_blue)

        elif keys[pygame.K_a]:
            lastMove_blue = 'left'
            dragon2.move("left", lastMove_blue)

        elif keys[pygame.K_d]:
            lastMove_blue = 'right'
            dragon2.move("right", lastMove_blue)

        elif not keys[pygame.K_w] and not keys[pygame.K_s]:
            if not keys[pygame.K_a] and not keys[pygame.K_d]:
                dragon2.move("stop", lastMove_blue)

        all_sprites.update()
        screen.fill(pygame.Color("black"))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)


# загрузка спрайтов
background = load_image('image/menu.png')
map_1_ig = load_image('image/map_one_image.png')
map_2_ig = load_image('image/map_two_image.png')
map_3_ig = load_image('image/map_three_image.png')
map_4_ig = load_image('image/map_three_image.png')

player_group = pygame.sprite.Group()

if __name__ == '__main__':
    Otobraz()
