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
BLACK = (20, 20, 20)

TABLE_GREEN = (20, 110, 90)
TABLE_GREEN_2 = (35, 65, 55)
TABLE_GREEN_3 = (42, 85, 70)

FONT_BIG = pygame.font.SysFont("arial", 42, bold=True)
FONT_TITLE = pygame.font.SysFont("arial", 56, bold=True)
FONT_MED = pygame.font.SysFont("arial", 28, bold=True)
FONT = pygame.font.SysFont("arial", 22)
FONT_SMALL = pygame.font.SysFont("arial", 18)

TURN_TIME_LIMIT = 30
INACTIVITY_WARNING_TIME = 15
MAX_INACTIVE_TURNS = 2

CARD_W = 120
CARD_H = 170