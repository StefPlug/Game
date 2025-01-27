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
                    '''registration()'''
                elif event.key == pygame.K_4:
                    terminate()


if __name__ == "__main__":
    main_menu()
