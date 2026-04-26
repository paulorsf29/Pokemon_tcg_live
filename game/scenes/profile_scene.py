import pygame
from .base_scene import Scene
from settings import *
from render.ui.ui import Button, draw_panel, draw_text


class ProfileScene(Scene):
    def __init__(self, game, **kwargs):
        super().__init__(game)
        self.back_btn = Button((30, 30, 140, 50), "Voltar", lambda: self.navigate_to("main_menu"))

    def handle_event(self, event):
        self.back_btn.handle_event(event)

    def draw(self, surface):
        surface.fill(BG)
        draw_text(surface, "Perfil do Jogador", FONT_TITLE, ACCENT, WIDTH // 2, 80, center=True)

        draw_panel(surface, pygame.Rect(220, 160, 840, 430))
        pygame.draw.circle(surface, ACCENT_2, (340, 280), 70)
        draw_text(surface, "Avatar", FONT_SMALL, WHITE, 340, 280, center=True)

        draw_text(surface, "Nickname: Treinador123", FONT_BIG, WHITE, 460, 220)
        draw_text(surface, "Rank atual: Ouro IV", FONT_MED, TEXT, 460, 290)
        draw_text(surface, "Vitorias: 128", FONT, TEXT, 460, 340)
        draw_text(surface, "Derrotas: 74", FONT, TEXT, 460, 380)
        draw_text(surface, "Deck favorito: Charizard EX", FONT, TEXT, 460, 420)
        draw_text(surface, "Amigos online: 3", FONT, TEXT, 460, 460)

        self.back_btn.draw(surface)
