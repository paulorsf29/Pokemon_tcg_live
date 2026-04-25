import pygame

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "Pokemon TCG Live - Prototipo"

BG = (18, 24, 38)
PANEL = (32, 42, 64)
PANEL_DARK = (24, 32, 50)
ACCENT = (255, 203, 5)
ACCENT_2 = (59, 76, 202)
WHITE = (245, 247, 250)
TEXT = (230, 230, 235)
TEXT_DIM = (180, 190, 205)
GREEN = (90, 200, 120)
RED = (220, 80, 80)
GRAY = (90, 100, 120)

FONT_BIG = pygame.font.SysFont("arial", 42, bold=True)
FONT_TITLE = pygame.font.SysFont("arial", 56, bold=True)
FONT_MED = pygame.font.SysFont("arial", 28, bold=True)
FONT = pygame.font.SysFont("arial", 22)
FONT_SMALL = pygame.font.SysFont("arial", 18)