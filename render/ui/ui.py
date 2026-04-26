import pygame
from settings import *

def draw_text(surface, text, font, color, x, y, center=False):
    img = font.render(str(text), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)
    return rect

def draw_panel(surface, rect, color=PANEL, border_color=WHITE, radius=16, border=2):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    pygame.draw.rect(surface, border_color, rect, width=border, border_radius=radius)

class Button:
    def __init__(self, rect, text, callback, bg=PANEL, hover=ACCENT_2, fg=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.bg = bg
        self.hover = hover
        self.fg = fg

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        color = self.hover if self.rect.collidepoint(mouse) else self.bg
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=14)
        draw_text(surface, self.text, FONT_MED, self.fg, self.rect.centerx, self.rect.centery, center=True)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

class Slider:
    def __init__(self, x, y, w, label, value=50):
        self.rect = pygame.Rect(x, y, w, 8)
        self.knob_x = x + int((value / 100) * w)
        self.label = label
        self.value = value
        self.dragging = False

    def draw(self, surface):
        draw_text(surface, f"{self.label}: {self.value}%", FONT, TEXT, self.rect.x, self.rect.y - 35)
        pygame.draw.rect(surface, GRAY, self.rect, border_radius=5)
        pygame.draw.circle(surface, ACCENT, (self.knob_x, self.rect.centery), 12)

    def handle_event(self, event):
        knob_rect = pygame.Rect(self.knob_x - 14, self.rect.centery - 14, 28, 28)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if knob_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.knob_x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.value = int(((self.knob_x - self.rect.x) / self.rect.w) * 100)