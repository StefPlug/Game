import pygame, sqlite3, sys, random
import math, os, pickle

# Инициализация
pygame.init()

# Константы
WIDTH, HEIGHT = 1920, 1080
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60
FONT = pygame.font.Font('data/Font/Arial.ttf', 48)
BIG_FONT = pygame.font.Font('data/Font/Arial.ttf', 96)

# Создание окна и загрузка фона
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jumpthrow")
background = pygame.image.load('data/images/background.jpg')  # загрузка изображения
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # редакт картинки
menu_background = pygame.image.load('data/images/menu_background.jpg')  # загрузка изображения
menu_background = pygame.transform.scale(menu_background, (WIDTH, HEIGHT))  # редакт картинки

# Загрузка звуков
sound1 = pygame.mixer.Sound("data/Sounds/select.mp3")
sound2 = pygame.mixer.Sound("data/Sounds/klavisha.mp3")
sound3 = pygame.mixer.Sound("data/Sounds/push.mp3")

# Группы спрайтов
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
fireballs = pygame.sprite.Group()

# глобальные переменные для функций
current_level = None
nickname = ''
change = 0
points = 0
health = 3


# функция завершения работы
def terminate():
    pygame.quit()
    sys.exit()


# класс платформ
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        stone_texture = pygame.image.load('data/images/stone.png')  # загрузка изображения
        stone_texture = pygame.transform.scale(stone_texture, (150, 25))  # редакт картинки
        self.image = stone_texture
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)  # отрисовка платформы


# класс двери
class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/images/door.png')  # загрузка изображения
        self.image = pygame.transform.scale(self.image, (100, 200))  # редакт картинки
        self.rect = self.image.get_rect(topleft=(x, y))


# подключение базы данных
conn = sqlite3.connect("data/game_data.db")
cursor = conn.cursor()

# создание таблицы пользователей, если не существует
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT,
    level INTEGER DEFAULT 1,
    score TEXT
)
""")
conn.commit()

# опять спрайты
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
fireballs = pygame.sprite.Group()
fireworks = pygame.sprite.Group()
doors = pygame.sprite.Group()


# функция отрисовки текста
def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))


# функция отрисовки сердечек героя
def draw_health_hearts(surface, hearts):
    heart_image = pygame.image.load('data/images/heart.png')  # загрузка изображения
    heart_image = pygame.transform.scale(heart_image, (40, 40))  # редакт картинки
    for i in range(hearts):
        surface.blit(heart_image, (10 + i * 50, 90))


# класс огненного шара
class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        fireball_image = pygame.image.load('data/images/fireball.png')  # загрузка изображения
        fireball_image = pygame.transform.scale(fireball_image, (73, 32))  # редакт картинки
        self.image = fireball_image
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5  # скорость полета шара

        # вычисление угла и скорости движения огненного шара
        self.angle = math.atan2(target_y - y, target_x - x)
        self.vel_x = self.speed * math.cos(self.angle)
        self.vel_y = self.speed * math.sin(self.angle)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # удаляю огненный шар, если он вышел за экран
        if self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()

        # удаление огненного шара при столкновении с платформой
        if pygame.sprite.spritecollide(self, platforms, False):
            self.kill()
            # создание взрыва
            explosion = Explosion(self.rect.centerx, self.rect.centery)
            all_sprites.add(explosion)


# класс взрывов
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/images/explosion.png')  # загрузка изображения
        self.image = pygame.transform.scale(self.image, (100, 100))  # редакт картинки
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 20

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


# класс дракона
class Dragon(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        dragon_image = pygame.image.load('data/images/dragon.png')  # загрузка изображения
        dragon_image = pygame.transform.scale(dragon_image, (200, 200))  # редакт картинки
        self.image = dragon_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.last_fire_time = pygame.time.get_ticks()
        self.speed = 2  # скорость дракона
        self.direction = random.choice([-1, 1])
        self.shoot = True  # это короче переменная которая дает разрешение на стрельбу дракона
        self.health = 3  # здоровье дракона

    def update(self, hero):
        self.rect.x += self.direction * self.speed
        # проверка выхода за границу экрана
        if self.rect.x <= 0 or self.rect.x >= WIDTH - self.rect.width:
            self.direction *= -1  # изменение направления

        now = pygame.time.get_ticks()
        if now - self.last_fire_time > 2000 and self.shoot:
            fireball = Fireball(self.rect.centerx, self.rect.bottom, hero.rect.centerx, hero.rect.top)
            fireballs.add(fireball)
            all_sprites.add(fireball)
            self.last_fire_time = now


# класс персонажа
class Hero(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.walk_right = [pygame.transform.scale(pygame.image.load(f'data/images/photo{i}.png'), (150, 150)) for i in
                           range(13, 24)]
        self.walk_left = [pygame.transform.scale(pygame.image.load(f'data/output2/photo{i}.png'), (150, 150)) for i in
                          range(13, 24)]
        self.jump_left = [pygame.transform.scale(pygame.image.load(f'data/images/photo{i}.png'), (150, 150)) for i in
                          range(2, 9)]
        self.jump_right = [pygame.transform.scale(pygame.image.load(f'data/output2/photo{i}.png'), (150, 150)) for i in
                           range(2, 9)]

        self.image = self.walk_right[0]  # так скажем Статичное изображение героя
        self.rect = self.image.get_rect(topleft=(x, y))  # начальная позиция героя
        self.vel_x = 0  # начальная скорость по оси X
        self.vel_y = 0  # начальная скорость по оси Y
        self.on_ground = False  # проверка на землю
        self.index_walk = 0
        self.index_jump = 0
        self.animation_speed = 0.13
        self.last_update = 0
        self.last_action = 1  # пременная нужна для того чтобы понять в какую сторону поворачивать персонажа
        self.velocity_y = 0

    def update(self, keys, platforms):
        """Обновление состояния героя, обработка ввода и столкновений"""
        self.vel_x = 0  # сброс скорости по оси X иначе не остановиться будет

        # обработка движений
        if keys[pygame.K_LEFT]:  # движение влево
            self.vel_x -= 5
            self.image = self.walk_left[int(self.index_walk)]
            self.last_action = -1
        elif keys[pygame.K_RIGHT]:  # движение вправо
            self.vel_x += 5
            self.image = self.walk_right[int(self.index_walk)]
            self.last_action = 1
        else:
            # если герой не движется, устанавливаем статическое изображение в зависимости от направления
            if self.last_action == 1:
                self.image = pygame.transform.scale(pygame.image.load(f'data/images/photo{11}.png'), (150, 150))
            else:
                self.image = pygame.transform.scale(pygame.image.load(f'data/output2/photo{11}.png'), (150, 150))
            pygame.mixer.pause()

        # обработка прыжка(полета)
        if not self.on_ground:
            self.vel_y += 0.75
            if self.last_action == 1:
                self.image = self.jump_left[int(self.index_jump)]
            else:
                self.image = self.jump_right[int(self.index_jump)]
        else:
            self.vel_y = 0

        # регулировка высоты прыжка
        if keys[pygame.K_UP] and self.on_ground:
            self.vel_y = -16
            self.on_ground = False

        # обновление позиции героя
        self.rect.x += self.vel_x
        self.collide(platforms, 'x')
        self.rect.y += self.vel_y
        self.on_ground = False
        self.collide(platforms, 'y')

        # проверка на землю
        if self.rect.y >= HEIGHT - 50 - 130:
            self.rect.y = HEIGHT - 50 - 130
            self.on_ground = True

        now = pygame.time.get_ticks()
        if now - self.last_update > 10:  # каждые 10мс проверяем в воздухе герой или нет
            if self.on_ground:
                self.index_walk = (self.index_walk + self.animation_speed) % len(self.walk_right)
            else:
                self.index_jump = (self.index_jump + self.animation_speed) % len(self.jump_right)

            self.last_update = now

    def collide(self, platforms, direction):
        """проверка на столкновения героя с платформами"""
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


class HeroBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image = pygame.transform.scale(pygame.image.load(f'data/images/electro_ball.png'),
                                            (40, 40))  # редакт картинки # загрузка изображения
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.angle = math.atan2(target_y - y, target_x - x)
        self.vel_x = self.speed * math.cos(self.angle)
        self.vel_y = self.speed * math.sin(self.angle)

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # удаляю снаряд, если он выходит за пределы экрана
        if self.rect.x < 0 or self.rect.x > WIDTH or self.rect.y < 0 or self.rect.y > HEIGHT:
            self.kill()


class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        self.size = random.randint(5, 10)
        self.color = random.choice(self.COLORS)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, -5)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 0.1  # Гравитация

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


def create_fireworks(x, y):
    """Создание частиц(салюта)"""
    particles = []
    for _ in range(100):
        particles.append(Particle(x, y))
    pygame.mixer.music.load("data/sounds/fireworks_sound.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    return particles


def draw_results_table():
    """Отрисовка таблицы результатов поверх основного окна"""
    results_background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    results_background.fill((0, 0, 0, 128))

    table_width = 1000
    table_height = 600
    table_surface = pygame.Surface((table_width, table_height))
    table_surface.fill((30, 30, 30))
    table_rect = table_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    # Заголовок
    title = BIG_FONT.render("Таблица рекордов", True, (255, 215, 0))
    title_rect = title.get_rect(center=(table_width // 2, 50))

    # получение данных из БД
    cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 7")
    results = cursor.fetchall()

    running = True
    while running:
        screen.blit(results_background, (0, 0))

        # отрисовка таблицы
        table_surface.fill((30, 30, 30))
        table_surface.blit(title, title_rect)

        # отрисовка данных
        y_offset = 150
        for i, (username, score) in enumerate(results, 1):
            text = FONT.render(f"{i}. {username}: {score} очков", True, WHITE)
            table_surface.blit(text, (100, y_offset))
            y_offset += 50

        # кнопка возврата
        exit_text = FONT.render("Нажмите ESC чтобы вернуться", True, WHITE)
        table_surface.blit(exit_text, (table_width // 2 - 280, table_height - 100))

        screen.blit(table_surface, table_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()


def create_level():
    """Создание уровня"""
    second_window = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Конструктор уровней")
    font = pygame.font.Font(None, 36)
    running = True
    platforms_list = []
    doors_list = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_level(platforms_list)
                    platforms.empty()
                    all_sprites.empty()
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    platform = Platform(event.pos[0], event.pos[1], 150, 15)
                    platforms.add(platform)
                    all_sprites.add(platform)  # добавляем спрайт платформы в all_sprites
                    platforms_list.append(platform)
                if event.button == 3:
                    door = Door(event.pos[0], event.pos[1])
                    doors.add(door)
                    all_sprites.add(door)  # добавляем спрайт двери в all_sprites
                    doors_list.append(door)

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
    for door in doors:
        level_data.append((door.rect.x, door.rect.y))
    if not os.path.exists('data/levels'):
        os.makedirs('data/levels')
    level_number = len(os.listdir('data/levels')) + 1  # Нумерация уровнеи
    with open(f'data/levels/level_{level_number}.pkl', 'wb') as f:
        pickle.dump(level_data, f)


def load_levels():
    """Загрузка уровней из папки levels."""
    levels = []
    if os.path.exists('data/levels'):
        for filename in os.listdir('data/levels'):
            if filename.endswith('.pkl'):
                levels.append(filename)
    return levels


def select_level():
    global current_level
    """Выбор уровня из сохраненных файлов."""
    levels = load_levels()
    if not levels:
        return

    selected_level = None
    while selected_level is None:
        screen.fill((255, 255, 255))
        draw_text(screen, "Выберите уровень", FONT, (0, 0, 0), WIDTH // 2 - 150, HEIGHT // 4)

        for index, level in enumerate(levels):
            draw_text(screen, f"{index + 1}. {level}", FONT, (0, 0, 0), WIDTH // 2 - 150, HEIGHT // 4 + 50 + index * 50)

        draw_text(screen, "ESC - выход", FONT, (0, 0, 0), WIDTH // 2 - 150, HEIGHT // 4 + 50 + len(levels) * 50 + 20)

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
                        selected_level = levels[index]

    current_level = selected_level
    """Загружаем выбранный уровень"""
    load_level(selected_level)


def load_level(level_filename):
    global nickname, current_level, change, doors
    """Загрузка уровня из файла."""
    with open(f'data/levels/{level_filename}', 'rb') as f:
        level_data = pickle.load(f)

    platforms.empty()
    doors.empty()
    all_sprites.empty()

    for x, y in level_data[:-1]:
        platform = Platform(x, y, 200, 40)
        platforms.add(platform)
        all_sprites.add(platform)

    door = Door(level_data[-1][0], level_data[-1][1])
    doors.add(door)
    all_sprites.add(door)

    current_level = level_filename
    if change == 0:
        main_menu()
    else:
        game(nickname)


def load_next_level(current_level):
    """Загрузка следующего уровня."""
    levels = load_levels()
    if levels:
        current_index = levels.index(current_level)
        if current_index + 1 < len(levels):
            load_level(levels[current_index + 1])
            return True
    return False


def show_completion_screen():
    global nickname, points
    """Показать экран завершения игры."""
    pygame.mixer.music.load("data/Sounds/winning_sound.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    particles = create_fireworks(WIDTH // 2, HEIGHT // 2)
    last_firework_time = 0
    running = True
    print(nickname, points)

    while running:
        current_time = pygame.time.get_ticks()
        if current_time - last_firework_time > 2000:  # каждые 2 секунды спавним салют
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT // 2)
            particles.extend(create_fireworks(x, y))
            particles.extend(create_fireworks(WIDTH - x, y))
            last_firework_time = current_time

        screen.fill((0, 0, 0))
        draw_text(screen, "Поздравляем!", BIG_FONT, (255, 255, 255), WIDTH // 2 - 250, HEIGHT // 2 - 50)
        draw_text(screen, "Вы прошли игру!", BIG_FONT, (255, 255, 255), WIDTH // 2 - 290, HEIGHT // 2 + 50)
        draw_text(screen, "Нажмите ESC для выхода", FONT, (255, 255, 255), WIDTH // 2 - 250, HEIGHT // 2 + 150)
        draw_text(screen, "Если хотите посмотреть свои результаты, нажмите Tab", FONT, (255, 255, 255),
                  WIDTH // 2 - 400, HEIGHT // 2 + 200)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                if event.key == pygame.K_TAB:
                    show_results = True
                    # записываем результаты в БД
                    cursor.execute("UPDATE users SET score = ? WHERE username = ?", (points, nickname))
                    conn.commit()
                    draw_results_table()
                    running = False

        for particle in particles:
            particle.update()
            particle.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


def show_rules():
    running = True
    while running:
        screen.fill((255, 255, 255))

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
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))  # редакт картинки
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


def registration():
    global nickname
    username = ""
    password = ""
    is_register = True
    active_login = False
    active_password = False

    # Загрузка фонового изображения
    bg_image = pygame.image.load('data/images/registration_bg.jpg')
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

    # Параметры полей ввода
    input_box_width = 600
    input_box_height = 80
    input_box_y = HEIGHT // 2 - 100
    input_box_x = WIDTH // 2 - input_box_width // 2
    login_rect = pygame.Rect(input_box_x, input_box_y, input_box_width, input_box_height)
    password_rect = pygame.Rect(input_box_x, input_box_y + 120, input_box_width, input_box_height)

    while True:
        screen.blit(bg_image, (0, 0))  # Отрисовываем фон

        # Рисуем полупрозрачную панель
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 150), (0, 0, WIDTH, HEIGHT))
        screen.blit(overlay, (0, 0))

        # Заголовок формы
        title_text = "РЕГИСТРАЦИЯ" if is_register else "АВТОРИЗАЦИЯ"
        draw_text(screen, title_text, BIG_FONT, (255, 255, 255),
                  WIDTH // 2 - 250, HEIGHT // 4 - 50)

        # Координаты для элементов
        input_box_x = WIDTH // 2 - input_box_width // 2

        # Поле для логина
        pygame.draw.rect(screen, (255, 255, 255),
                         (input_box_x, input_box_y,
                          input_box_width, input_box_height), 2)
        draw_text(screen, "Логин:", FONT, (255, 255, 255),
                  input_box_x - 150, input_box_y + 20)
        draw_text(screen, username, FONT, (255, 255, 255),
                  input_box_x + 20, input_box_y + 20)

        # Поле для пароля
        pygame.draw.rect(screen, (255, 255, 255),
                         (input_box_x, input_box_y + 120,
                          input_box_width, input_box_height), 2)
        draw_text(screen, "Пароль:", FONT, (255, 255, 255),
                  input_box_x - 180, input_box_y + 140)
        draw_text(screen, '*' * len(password), FONT, (255, 255, 255),
                  input_box_x + 20, input_box_y + 140)

        # Кнопки и подсказки
        draw_text(screen, "Enter - подтвердить", FONT, (200, 200, 200),
                  150, HEIGHT - 200)
        draw_text(screen, "Tab - переключить режим", FONT, (200, 200, 200),
                  150, HEIGHT - 150)
        draw_text(screen, "Esc - выход в меню", FONT, (200, 200, 200),
                  150, HEIGHT - 100)

        pygame.display.flip()

        # Обработка событий мыши
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Проверка клика по полю логина
                if login_rect.collidepoint(event.pos):
                    active_login = True
                    active_password = False
                # Проверка клика по полю пароля
                elif password_rect.collidepoint(event.pos):
                    active_password = True
                    active_login = False
                else:
                    active_login = False
                    active_password = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    sound1.play()
                    if is_register:
                        try:
                            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                            conn.commit()
                            pygame.mixer.music.load("data/Sounds/background_music.mp3")
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play(-1)
                            nickname = username
                            game(username)
                            return
                        except Exception:
                            print("Логин уже существует!")
                    else:
                        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                        user = cursor.fetchone()
                        if user:
                            pygame.mixer.music.load("data/Sounds/background_music.mp3")
                            pygame.mixer.music.set_volume(0.5)
                            pygame.mixer.music.play(-1)
                            nickname = username
                            game(username)
                            return
                        else:
                            print("Неверный логин или пароль!")

                elif event.key == pygame.K_TAB:
                    sound1.play()
                    is_register = not is_register

                elif event.key == pygame.K_BACKSPACE:
                    if active_login:
                        username = username[:-1]
                    elif active_password:
                        password = password[:-1]
                else:
                    if active_login and len(username) < 10:
                        username += event.unicode
                    elif active_password and len(password) < 10:
                        password += event.unicode


def game(username):
    global all_sprites, fireballs, current_level, change, points, health
    all_sprites.empty()
    fireballs.empty()
    hero_bullets = pygame.sprite.Group()  # группа для снарядов героя
    font = pygame.font.Font(None, 36)
    running = True

    hero = Hero(0, HEIGHT)
    all_sprites.add(hero)

    for platform in platforms:
        all_sprites.add(platform)

    dragon = Dragon(600, 100)
    all_sprites.add(dragon)

    for door in doors:
        all_sprites.add(door)

    clock = pygame.time.Clock()

    # переменные для отображения текста "+100"
    show_points_text = False
    points_text_time = 0

    while running:
        keys = pygame.key.get_pressed()
        screen.blit(background, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    change = 0
                    pygame.mixer.music.stop()
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x1, y1 = event.pos
                    bullet = HeroBullet(hero.rect.centerx, hero.rect.centery, x1, y1)
                    hero_bullets.add(bullet)
                    all_sprites.add(bullet)

        hero.update(keys, platforms)
        dragon.update(hero)
        fireballs.update()
        hero_bullets.update()

        if pygame.sprite.spritecollide(hero, fireballs, True):
            health -= 1
            if health <= 0:
                # записываем результаты в базу данных перед завершением игры
                cursor.execute("UPDATE users SET score = ? WHERE username = ?", (points, nickname))
                conn.commit()
                game_over()

        # проверка попадания снаряда героя в дракона
        for bullet in hero_bullets:
            if pygame.sprite.collide_rect(bullet, dragon):
                dragon.health -= 1
                bullet.kill()
                if dragon.health <= 0:
                    dragon.kill()
                    if dragon.shoot:
                        # прибавляем + 100 очков за убийство дракона
                        points += 100
                        # отображаем текст "+100"
                        show_points_text = True
                        points_text_time = pygame.time.get_ticks()
                    dragon.shoot = False
        # проверка времени отображения текста "+100"
        if show_points_text:
            current_time = pygame.time.get_ticks()
            if current_time - points_text_time > 1000:  # 1000 = 1 секунда
                # скрываем текст
                show_points_text = False

        for explosion in all_sprites:
            if isinstance(explosion, Explosion):
                explosion.update()

        # отрисовываем платформы
        for platform in platforms:
            pygame.draw.rect(screen, (0, 0, 255), platform)

        # проверка столкновения героя с дверью
        if pygame.sprite.spritecollide(hero, doors, False):
            change = 1
            if not load_next_level(current_level):
                # Записываем результаты в базу данных перед завершением игры
                cursor.execute("UPDATE users SET score = ? WHERE username = ?", (points, nickname))
                conn.commit()
                show_completion_screen()
                return
            dragon.shoot = True
            running = False

        all_sprites.draw(screen)

        # отображаем текст "+100" только если истинна
        if show_points_text:
            draw_text(screen, "+100", FONT, (0, 255, 0), dragon.rect.centerx, dragon.rect.centery - 50)

        draw_text(screen, f"Игрок: {username}", FONT, WHITE, 10, 10)
        draw_text(screen, f"Опыт: {points}", FONT, (0, 255, 0), 10, 50)
        draw_health_hearts(screen, health)

        text_surface = font.render("Выйти в меню (ESC)", True, (255, 255, 0))
        screen.blit(text_surface, (1650, 10))

        pygame.display.flip()
        clock.tick(FPS)


# конец игры
def game_over():
    global points
    # Записываем результат в базу данных
    cursor.execute("UPDATE users SET score = ? WHERE username = ?", (points, nickname))
    conn.commit()  # Сохраняем изменения в базе данных

    show_results = False  # Флаг для отображения таблицы результатов
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_text(screen, "Вы проиграли!", BIG_FONT, (255, 255, 255), WIDTH // 2 - 250, HEIGHT // 2 - 50)
        draw_text(screen, "Нажмите ESC для выхода", FONT, (255, 255, 255), WIDTH // 2 - 250, HEIGHT // 2 + 50)
        draw_text(screen, "Если хотите посмотреть свои результаты, нажмите Tab", FONT, (255, 255, 255),
                  WIDTH // 2 - 400, HEIGHT // 2 + 100)

        # Отображение таблицы результатов
        if show_results:
            draw_results_table()
            running = False

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    terminate()
                if event.key == pygame.K_TAB:
                    show_results = True
                    # Записываем результаты в БД
                    cursor.execute("UPDATE users SET score = ? WHERE username = ?", (points, nickname))
                    conn.commit()


# главное меню
def main_menu():
    while True:
        screen.blit(menu_background, (0, 0))

        # размеры и позиции кнопок
        button_width, button_height = 500, 100
        button_x = WIDTH // 2 - button_width // 2
        button_y = HEIGHT // 4

        # список кнопок и их текстов
        buttons = [
            {"text": "Начать игру", "action": "start_game",
             "rect": pygame.Rect(button_x, button_y, button_width, button_height)},
            {"text": "Создать уровень", "action": "create_level",
             "rect": pygame.Rect(button_x, button_y + 120, button_width, button_height)},
            {"text": "Выбрать уровень", "action": "select_level",
             "rect": pygame.Rect(button_x, button_y + 240, button_width, button_height)},
            {"text": "Правила игры", "action": "show_rules",
             "rect": pygame.Rect(button_x, button_y + 360, button_width, button_height)},
            {"text": "Выход", "action": "exit",
             "rect": pygame.Rect(button_x, button_y + 480, button_width, button_height)},
        ]

        # отрисовка кнопок и текста
        for button in buttons:
            # рисуем кнопку
            pygame.draw.rect(screen, (0, 128, 255), button["rect"])
            # выравниваем текст по центру кнопки
            text_surface = FONT.render(button["text"], True, WHITE)
            text_rect = text_surface.get_rect(center=button["rect"].center)
            screen.blit(text_surface, text_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            # если левая кнопка мыши нажата на кнопку то вызываем функцию
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button in buttons:
                    if button["rect"].collidepoint(mouse_pos):
                        sound1.play()
                        if button["action"] == "start_game":
                            registration()
                        elif button["action"] == "create_level":
                            create_level()
                        elif button["action"] == "select_level":
                            select_level()
                        elif button["action"] == "show_rules":
                            show_rules()
                        elif button["action"] == "exit":
                            terminate()
        pygame.display.flip()


# запускаем прогу
if __name__ == "__main__":
    main_menu()
