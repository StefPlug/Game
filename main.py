import pygame
import sqlite3
import sys
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

def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def terminate():
    pygame.quit()
    sys.exit()

def draw_text(surface, text, font, color, x, y):
    text_obj = font.render(text, True, color)
    surface.blit(text_obj, (x, y))

def main_menu():
    while True:
        screen.fill(WHITE)
        draw_text(screen, "Jumpthrow", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 4)
        draw_text(screen, "1. Начать игру", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 - 50)
        draw_text(screen, "2. Выбрать уровень", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2)
        draw_text(screen, "3. Настройки", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 50)
        draw_text(screen, "4. Выход", FONT, BLACK, WIDTH // 2 - 100, HEIGHT // 2 + 100)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    registration()
                elif event.key == pygame.K_4:
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
                            """game_loop(username) тут типа будет сама игра запускаться"""
                            return
                        except sqlite3.IntegrityError:
                            print("Логин уже существует!")
                    else:
                        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
                        user = cursor.fetchone()
                        if user:
                            """game_loop(username)"""
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