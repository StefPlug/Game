import pygame
import sqlite3
import sys
import os
import pickle
import random
import math

pygame.init()

WIDTH, HEIGHT = 1920, 1080
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
FONT = pygame.font.Font('data/Font/Arial.ttf', 48)
BIG_FONT = pygame.font.Font('data/Font/Arial.ttf', 96)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumpthrow")
background = pygame.image.load('data/images/background.jpg')
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
sound1 = pygame.mixer.Sound("data/Sounds/select.mp3")
sound2 = pygame.mixer.Sound("data/Sounds/klavisha.mp3")
sound3 = pygame.mixer.Sound("data/Sounds/push.mp3")

all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
fireballs = pygame.sprite.Group()

conn = sqlite3.connect("game_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    level INTEGER DEFAULT 1,
    score INTEGER DEFAULT 0
)
""")
conn.commit()


def terminate():
    pygame.quit()
    sys.exit()


def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def draw_health_hearts(surface, hearts):
    heart_image = pygame.image.load('data/images/heart.png')
    heart_image = pygame.transform.scale(heart_image, (40, 40))
    for i in range(hearts):
        surface.blit(heart_image, (10 + i * 50, 30))

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        stone_texture = pygame.image.load('data/images/stone.png')
        stone_texture = pygame.transform.scale(stone_texture, (200, 40))
        self.image = stone_texture
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        fireball_image = pygame.image.load('data/images/fireball.png')
        fireball_image = pygame.transform.scale(fireball_image, (73, 32))
        self.image = fireball_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

        self.angle = math.atan2(target_y - y, target_x - x)
        self.vel_x = self.speed * math.cos(self.angle)
        self.vel_y = self.speed * math.sin(self.angle)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()


class Dragon(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        dragon_image = pygame.image.load('data/images/dragon.png')
        dragon_image = pygame.transform.scale(dragon_image, (200, 200))
        self.image = dragon_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.last_fire_time = pygame.time.get_ticks()
        self.speed = 2
        self.direction = random.choice([-1, 1])

    def update(self, hero):
        self.rect.x += self.direction * self.speed
        if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width:
            self.direction *= -1

        now = pygame.time.get_ticks()
        if now - self.last_fire_time > 2000:
            fireball = Fireball(self.rect.centerx, self.rect.bottom, hero.rect.centerx, hero.rect.top)
            fireballs.add(fireball)
            all_sprites.add(fireball)
            self.last_fire_time = now


class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.walk_right = [pygame.transform.scale(pygame.image.load(f'data/images/photo{i}.png'), (200, 200)) for i in
                           range(13, 24)]
        self.walk_left = [pygame.transform.scale(pygame.image.load(f'data/output2/photo{i}.png'), (200, 200)) for i in
                          range(13, 24)]
        self.jump_left = [pygame.transform.scale(pygame.image.load(f'data/images/photo{i}.png'), (200, 200)) for i in
                          range(2, 9)]
        self.jump_right = [pygame.transform.scale(pygame.image.load(f'data/output2/photo{i}.png'), (200, 200)) for i in
                           range(2, 9)]

        self.image = self.walk_right[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.index_walk = 0
        self.index_jump = 0
        self.animation_speed = 0.13
        self.last_update = 0
        self.last_action = 1
        self.health = 10
        self.velocity_y = 0

    def update(self, keys, platforms):
        self.vel_x = 0

        if keys[pygame.K_LEFT]:
            self.vel_x -= 5
            self.image = self.walk_left[int(self.index_walk)]
            self.last_action = -1
        elif keys[pygame.K_RIGHT]:
            self.vel_x += 5
            self.image = self.walk_right[int(self.index_walk)]
            self.last_action = 1
        else:
            if self.last_action == 1:
                self.image = pygame.transform.scale(pygame.image.load(f'data/images/photo{11}.png'), (200, 200))
            else:
                self.image = pygame.transform.scale(pygame.image.load(f'data/output2/photo{11}.png'), (200, 200))

        if not self.on_ground:
            self.vel_y += 0.5
            if self.last_action == 1:
                self.image = self.jump_left[int(self.index_jump)]
            else:
                self.image = self.jump_right[int(self.index_jump)]
        else:
            self.vel_y = 0

        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = -16
            self.on_ground = False

        self.rect.x += self.vel_x
        self.collide(platforms, 'x')
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide(platforms, 'y')

        if self.rect.y >= HEIGHT - 50 - 130:
            self.rect.y = HEIGHT - 50 - 130
            self.on_ground = True

        now = pygame.time.get_ticks()
        if now - self.last_update > 10:
            if self.on_ground:
                self.index_walk = (self.index_walk + self.animation_speed) % len(self.walk_right)
            else:
                self.index_jump = (self.index_jump + self.animation_speed) % len(self.jump_right)

            self.last_update = now

    def collide(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == 'x':
                    if self.vel_x > 0:
                        self.rect.right = platform.rect.left
                    if self.vel_x < 0:
                        self.rect.left = platform.rect.right
                if direction == 'y':
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                    if self.vel_y < 0:
                        self.rect.top = platform.rect.bottom

def create_level():
    second_window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Конструктор уровней")
    font = pygame.font.Font(None, 36)
    running = True
    current_platforms = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_level(current_platforms)
                    platforms.empty()
                    all_sprites.empty()
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    platform = Platform(event.pos[0], event.pos[1], 200, 20)
                    platforms.add(platform)
                    all_sprites.add(platform)
                    current_platforms.append(platform)

        second_window.blit(background, (0, 0))
        all_sprites.draw(second_window)

        text_surface = font.render("Выйти (ESC)", True, (0, 0, 0))
        second_window.blit(text_surface, (10, 10))

        pygame.display.flip()

    pygame.display.set_mode((WIDTH, HEIGHT))
    platforms.empty()


def save_level(platforms):
    """Сохранение уровня в файл."""
    level_data = [(platform.rect.x, platform.rect.y) for platform in platforms]
    if not os.path.exists('levels'):
        os.makedirs('levels')
    level_number = len(os.listdir('levels')) + 1  # Нумерация уровней
    with open(f'levels/level_{level_number}.pkl', 'wb') as f:
        pickle.dump(level_data, f)


def load_levels():
    """Загрузка уровней из папки levels."""
    levels = []
    if os.path.exists('levels'):
        for filename in os.listdir('levels'):
            if filename.endswith('.pkl'):
                levels.append(filename)
    return levels


def select_level():
    """Выбор уровня из сохраненных файлов."""
    levels = load_levels()
    if not levels:
        return  # Если уровни не найдены, ничего не делаем

    selected_level = None
    while selected_level is None:
        screen.fill(WHITE)
        draw_text(screen, "Выберите уровень", FONT, BLACK, WIDTH // 2 - 150, HEIGHT // 4)

        for index, level in enumerate(levels):
            draw_text(screen, f"{index + 1}. {level}", FONT, BLACK, WIDTH // 2 - 150, HEIGHT // 4 + 50 + index * 50)

        draw_text(screen, "ESC - выход", FONT, BLACK, WIDTH // 2 - 150, HEIGHT // 4 + 50 + len(levels) * 50 + 20)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                sound3.play()
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    index = event.key - pygame.K_1
                    if index < len(levels):
                        selected_level = levels[index]  # Сохраняем выбранный уровень в папку

    """Загружаем выбранный уровень"""
    load_level(selected_level)


def load_level(level_filename):
    """Загрузка уровня из файла."""
    with open(f'levels/{level_filename}', 'rb') as f:
        level_data = pickle.load(f)

    platforms.empty()
    all_sprites.empty()

    for x, y in level_data:
        platform = Platform(x, y, 200, 40)
        platforms.add(platform)
        all_sprites.add(platform)

def show_rules():
    running = True
    while running:
        screen.fill(WHITE)

        draw_text(screen, "Правила игры 'Jumpthrow'", BIG_FONT, (0, 128, 255), WIDTH // 2 - 250, HEIGHT // 2 - 50)

        """Правила игры"""
        rules = [
            "1. Цель игры: избегать различных атак и добораться до",
            "конца уровня.",
            "2. Управление:",
            "   - Стрелка влево (←): Двигайтесь влево.",
            "",
            "   - Стрелка вправо (→): Двигайтесь вправо.",
            "",
            "   - Стрелка вверх (↑): Прыгните.",
            "",
            "   - Esc: Вернуться в главное меню.",
            "",
            "3. У героя 3 жизни. Будьте осторожны!",
            "4. Создавайте свои уровни и выбирайте их для игры.",
            "5. Если здоровье героя достигнет 0, игра закончится.",
            "            Нажмите ESC, чтобы вернуться в меню."
        ]

        background_image = pygame.image.load('data/images/background_rules.png')
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        screen.blit(background_image, (0, 0))

        for i, rule in enumerate(rules):
            draw_text(screen, rule, FONT, (255, 255, 255), 370, HEIGHT // 6 - 30 + i * 40)

        pygame.draw.rect(screen, (5, 4, 4), (WIDTH - 350, 0, WIDTH, 95))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

def game_loop(username):
    global all_sprites, fireballs
    all_sprites.empty()
    fireballs.empty()
    font = pygame.font.Font(None, 36)
    running = True

    hero = Hero(0, HEIGHT)
    all_sprites.add(hero)

    for platform in platforms:
        all_sprites.add(platform)

    dragon = Dragon(600, 100)
    all_sprites.add(dragon)

    clock = pygame.time.Clock()

    while running:
        keys = pygame.key.get_pressed()
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        hero.update(keys, platforms)
        dragon.update(hero)
        fireballs.update()

        if pygame.sprite.spritecollide(hero, fireballs, True):
            hero.health -= 1
            if hero.health <= 0:
                game_over()

        for platform in platforms:
            pygame.draw.rect(screen, (0, 0, 255), platform)

        all_sprites.draw(screen)

        draw_text(screen, f"Игрок: {username}", FONT, WHITE, 10, 10)
        draw_health_hearts(screen, hero.health)

        text_surface = font.render("Выйти в меню (ESC)", True, (255, 255, 0))
        screen.blit(text_surface, (1650, 10))

        pygame.display.flip()
        clock.tick(FPS)

def game_over():
    while True:
        screen.fill(BLACK)
        draw_text(screen, "Вы проиграли!", BIG_FONT, WHITE, WIDTH // 2 - 250, HEIGHT // 2 - 50)
        draw_text(screen, "Нажмите ESC для выхода", FONT, WHITE, WIDTH // 2 - 250, HEIGHT // 2 + 50)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text(screen, "Jumpthrow", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 4)
        draw_text(screen, "1. Начать игру", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text(screen, "2. Создать уровень", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2)
        draw_text(screen, "3. Выбрать уровень", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 50)
        draw_text(screen, "4. Правила игры", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 100)
        draw_text(screen, "5. Выход", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 150)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    sound1.play()
                    registration()
                elif event.key == pygame.K_2:
                    sound3.play()
                    create_level()
                elif event.key == pygame.K_3:
                    sound3.play()
                    select_level()
                elif event.key == pygame.K_4:
                    sound1.play()
                    show_rules()
                elif event.key == pygame.K_5:
                    terminate()


def registration():
    username = ""
    password = ""
    is_register = True

    while True:
        screen.fill(WHITE)
        draw_text(screen, "Регистрация" if is_register else "Вход", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 4)
        draw_text(screen, f"Логин: {username}", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text(screen, f"Пароль: {'*' * len(password)}", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2)
        draw_text(screen, "Enter - подтвердить", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 100)
        draw_text(screen, "Tab - переключить (регистрация/вход)", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 150)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if is_register:
                        try:
                            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                            conn.commit()
                            game_loop(username)
                            return
                        except sqlite3.IntegrityError:
                            print("Логин уже существует!")
                    else:
                        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                        user = cursor.fetchone()
                        if user:
                            game_loop(username)
                            return
                        else:
                            print("Неверный логин или пароль!")

                elif event.key == pygame.K_TAB:
                    is_register = not is_register

                elif event.key == pygame.K_BACKSPACE:
                    if len(password) > 0:
                        password = password[:-1]
                    elif len(username) > 0:
                        username = username[:-1]
                else:
                    if len(username) < 10 and len(password) == 0:
                        username += event.unicode
                    elif len(password) < 10:
                        password += event.unicode


if __name__ == "__main__":
    main_menu()
