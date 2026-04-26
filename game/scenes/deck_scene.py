import pygame
from .base_scene import Scene
from settings import *
from render.ui.ui import draw_panel, Button, draw_text
from game.core.services.deck_provider import JsonDeckProvider


class DeckScene(Scene):
    def __init__(self, game, **kwargs):
        super().__init__(game)
        self.selected = 0

        # Usa o DeckProvider para obter a lista de decks
        self._deck_provider = JsonDeckProvider()
        self.decks = self._deck_provider.list_decks()

        self.back_btn = Button((30, 30, 140, 50), "Voltar", lambda: self.navigate_to("main_menu"))
        self.play_btn = Button((980, 620, 220, 55), "Usar este deck", self.use_deck)

    def use_deck(self):
        self.game.selected_deck = self.decks[self.selected]
        self.navigate_to("modes")

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.play_btn.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, deck in enumerate(self.decks):
                rect = pygame.Rect(80, 170 + i * 90, 420, 70)
                if rect.collidepoint(event.pos):
                    self.selected = i

    def draw(self, surface):
        surface.fill(BG)
        draw_text(surface, "Decks de Batalha", FONT_TITLE, ACCENT, WIDTH // 2, 80, center=True)

        for i, deck in enumerate(self.decks):
            rect = pygame.Rect(80, 170 + i * 90, 420, 70)
            color = ACCENT_2 if i == self.selected else PANEL
            draw_panel(surface, rect, color=color)
            draw_text(surface, deck, FONT_MED, WHITE, rect.x + 20, rect.y + 20)

        preview = pygame.Rect(560, 170, 620, 400)
        draw_panel(surface, preview, color=PANEL_DARK)

        draw_text(surface, f"Preview: {self.decks[self.selected]}", FONT_BIG, ACCENT, 590, 210)
        draw_text(surface, "Cartas principais:", FONT_MED, WHITE, 590, 280)
        draw_text(surface, "- Pokemon atacante principal", FONT, TEXT, 610, 330)
        draw_text(surface, "- Cartas de apoiador", FONT, TEXT, 610, 365)
        draw_text(surface, "- Cartas de item", FONT, TEXT, 610, 400)
        draw_text(surface, "- Energia", FONT, TEXT, 610, 435)
        draw_text(surface, "Aqui depois voce pode adicionar miniaturas reais das cartas.", FONT_SMALL, TEXT_DIM, 590, 510)

        self.back_btn.draw(surface)
        self.play_btn.draw(surface)
