import pygame
import os
import sys


# инициализация Pygame:
pygame.init()
# размеры окна:
size = width, height = 500, 500
# screen — холст, на котором нужно рисовать:
screen = pygame.display.set_mode(size)
pygame.display.set_caption('Перемещение героя')


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    intro_text = ["Перемещение героя", "",
                  "Герой двигается",
                  "Карта на месте"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    FPS = 50
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')



def load_level(filename):
    filename = filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))



def game():
    screen.fill('black')

    tile_width = tile_height = 50

    # основной персонаж
    player = None

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    grasses_group = pygame.sprite.Group()
    walls_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()

    class Grass(pygame.sprite.Sprite):
        def __init__(self, tile_type, pos_x, pos_y):
            super().__init__(grasses_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)

    class Wall(pygame.sprite.Sprite):
        def __init__(self, tile_type, pos_x, pos_y):
            super().__init__(walls_group, all_sprites)
            self.image = tile_images[tile_type]
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)

    class Player(pygame.sprite.Sprite):
        def __init__(self, pos_x, pos_y):
            super().__init__(player_group, all_sprites)
            self.image = player_image
            self.rect = self.image.get_rect().move(
                tile_width * pos_x + 15, tile_height * pos_y + 5)

    class Camera:
        # зададим начальный сдвиг камеры
        def __init__(self):
            pass

        def update(self, dx, dy, group):
            for i in group:
                if not isinstance(i, Player):
                    i.rect.x -= dx
                    if i.rect.x < 0:
                        i.rect.x = width - tile_width
                    elif i.rect.x >= width:
                        i.rect.x = 0
                    i.rect.y -= dy
                    if i.rect.y < 0:
                        i.rect.y = height - tile_height
                    elif i.rect.y >= height:
                        i.rect.y = 0

        def not_update(self, dx, dy, group):
            for i in group:
                if not isinstance(i, Player):
                    i.rect.x += dx
                    if i.rect.x < 0:
                        i.rect.x = width - tile_width
                    elif i.rect.x >= width:
                        i.rect.x = 0
                    i.rect.y += dy
                    if i.rect.y < 0:
                        i.rect.y = height - tile_height
                    elif i.rect.y >= height:
                        i.rect.y = 0

    def generate_level(level):
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    Grass('empty', x, y)
                elif level[y][x] == '#':
                    Wall('wall', x, y)
                elif level[y][x] == '@':
                    Grass('empty', x, y)
                    new_player = Player(x, y)
        # вернем игрока, а также размер поля в клетках
        return new_player, x, y

    player, level_x, level_y = generate_level(load_level('new_map.txt'))
    camera = Camera()
    all_sprites.draw(screen)
    while True:
        screen.fill('black')
        dx, dy = 0, 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    dy = -tile_height
                elif event.key == pygame.K_DOWN:
                    dy = tile_height
                elif event.key == pygame.K_LEFT:
                    dx = -tile_width
                elif event.key == pygame.K_RIGHT:
                    dx = tile_width
        camera.update(dx, dy, walls_group)
        camera.update(dx, dy, grasses_group)
        if pygame.sprite.spritecollideany(player, walls_group):
            camera.not_update(dx, dy, walls_group)
            camera.not_update(dx, dy, grasses_group)
        grasses_group.draw(screen)
        walls_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()


def main():
    start_screen()
    game()


main()
