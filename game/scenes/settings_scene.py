import pygame
from .base_scene import Scene
from settings import *
from render.ui.ui import Button, Slider, draw_panel, draw_text, UIComponentFactory


class SettingsScene(Scene):
    def __init__(self, game, **kwargs):
        super().__init__(game)
        self.back_btn = Button((30, 30, 140, 50), "Voltar", lambda: self.navigate_to("main_menu"))
        self.volume_slider = UIComponentFactory.criar("slider", x=420, y=260, w=350, label="Volume", value=70)
        self.graphics_slider = UIComponentFactory.criar("slider", x=420, y=360, w=350, label="Graficos", value=60)

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.volume_slider.handle_event(event)
        self.graphics_slider.handle_event(event)

    def draw(self, surface):
        surface.fill(BG)
        draw_text(surface, "Configuracoes", FONT_TITLE, ACCENT, WIDTH // 2, 90, center=True)

        panel = pygame.Rect(300, 180, 680, 300)
        draw_panel(surface, panel, color=PANEL_DARK)

        self.volume_slider.draw(surface)
        self.graphics_slider.draw(surface)

        draw_text(surface, "Sugestao: use graficos medios no prototipo.", FONT_SMALL, TEXT_DIM, 420, 430)

        self.back_btn.draw(surface)
