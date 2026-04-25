import pygame
from scenes.base_scene import Scene
from settings import *
from ui import Button, draw_panel, draw_text

class BattleScene(Scene):
    def __init__(self, game, mode_name):
        super().__init__(game)
        self.mode_name = mode_name
        self.turn_time = 30
        self.accumulator = 0
        self.back_btn = Button((20, 20, 140, 46), "Render-se", self.surrender, bg=RED, hover=(170, 50, 50))
        self.end_turn_btn = Button((1050, 640, 180, 50), "Encerrar turno", self.end_turn)

    def surrender(self):
        from scenes.main_menu_scene import MainMenuScene
        self.game.change_scene(MainMenuScene(self.game))

    def end_turn(self):
        self.turn_time = 30

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.end_turn_btn.handle_event(event)

    def update(self, dt):
        self.accumulator += dt
        if self.accumulator >= 1:
            self.accumulator = 0
            self.turn_time -= 1
            if self.turn_time <= 0:
                self.turn_time = 30

    def draw_card(self, surface, x, y, title, hp, selected=False):
        rect = pygame.Rect(x, y, 120, 170)
        color = (250, 250, 250) if not selected else (255, 240, 180)
        pygame.draw.rect(surface, color, rect, border_radius=12)
        pygame.draw.rect(surface, ACCENT_2, rect, 3, border_radius=12)
        draw_text(surface, title, FONT_SMALL, (20, 20, 20), x + 10, y + 12)
        draw_text(surface, f"HP {hp}", FONT_SMALL, (20, 20, 20), x + 10, y + 40)
        pygame.draw.rect(surface, (220, 220, 235), (x + 10, y + 70, 100, 60), border_radius=8)
        draw_text(surface, "Arte", FONT_SMALL, GRAY, x + 60, y + 100, center=True)

    def draw(self, surface):
        surface.fill((20, 110, 90))
        draw_text(surface, f"Batalha - {self.mode_name}", FONT_BIG, WHITE, WIDTH // 2, 30, center=True)

        selected_deck = getattr(self.game, "selected_deck", "Deck Padrao")

        draw_panel(surface, pygame.Rect(120, 70, 1040, 120), color=(35, 65, 55))
        draw_text(surface, "Oponente", FONT_MED, WHITE, 150, 90)
        draw_text(surface, "Premios restantes: 6", FONT, WHITE, 150, 125)
        draw_text(surface, "Cartas no deck: 32", FONT, WHITE, 150, 150)

        draw_panel(surface, pygame.Rect(180, 215, 920, 250), color=(42, 85, 70))
        draw_text(surface, "Pokemon Ativo do Oponente", FONT, WHITE, 280, 240)
        self.draw_card(surface, 240, 270, "Charizard", 330)

        draw_text(surface, "Seu Pokemon Ativo", FONT, WHITE, 760, 240)
        self.draw_card(surface, 720, 270, "Pikachu", 220, selected=True)

        draw_panel(surface, pygame.Rect(70, 520, 930, 170), color=(35, 65, 55))
        draw_text(surface, "Sua mao", FONT_MED, WHITE, 100, 540)

        hand_names = ["Energia", "Pocao", "Apoiador", "Item", "Pokemon"]
        for i, name in enumerate(hand_names):
            self.draw_card(surface, 180 + i * 145, 560, name, "--")

        draw_panel(surface, pygame.Rect(1030, 120, 210, 500), color=PANEL_DARK)
        draw_text(surface, "Turno", FONT_MED, ACCENT, 1135, 155, center=True)
        timer_color = RED if self.turn_time <= 15 else WHITE
        draw_text(surface, str(self.turn_time), FONT_TITLE, timer_color, 1135, 225, center=True)

        draw_text(surface, "Objetivo:", FONT, WHITE, 1060, 310)
        draw_text(surface, "Pegar 6 cartas", FONT_SMALL, TEXT, 1060, 345)
        draw_text(surface, "de premio antes", FONT_SMALL, TEXT, 1060, 370)
        draw_text(surface, "do adversario.", FONT_SMALL, TEXT, 1060, 395)

        draw_text(surface, "Deck:", FONT, WHITE, 1060, 445)
        draw_text(surface, selected_deck, FONT_SMALL, TEXT, 1060, 475)

        draw_text(surface, "Acoes:", FONT, WHITE, 1060, 525)
        draw_text(surface, "- Selecionar carta", FONT_SMALL, TEXT, 1060, 555)
        draw_text(surface, "- Usar habilidade", FONT_SMALL, TEXT, 1060, 580)
        draw_text(surface, "- Atacar", FONT_SMALL, TEXT, 1060, 605)

        self.back_btn.draw(surface)
        self.end_turn_btn.draw(surface)