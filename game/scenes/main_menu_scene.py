from .base_scene import Scene
from settings import *
from render.ui.ui import Button, draw_text, UIComponentFactory


class MainMenuScene(Scene):
    def __init__(self, game, **kwargs):
        super().__init__(game)

        self.buttons = [
            UIComponentFactory.criar("button", rect=(490, 220, 300, 60), text="Batalhar", callback=lambda: self.navigate_to("modes")),
            UIComponentFactory.criar("button", rect=(490, 300, 300, 60), text="Deck de Batalha", callback=lambda: self.navigate_to("deck")),
            UIComponentFactory.criar("button", rect=(490, 380, 300, 60), text="Perfil", callback=lambda: self.navigate_to("profile")),
            UIComponentFactory.criar("button", rect=(490, 460, 300, 60), text="Configuracoes", callback=lambda: self.navigate_to("settings")),
            UIComponentFactory.criar("button", rect=(490, 540, 300, 60), text="Sair", callback=self.game.quit, bg=RED, hover=(170, 50, 50)),
        ]

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, surface):
        surface.fill(BG)
        draw_text(surface, "Pokemon TCG Live", FONT_TITLE, ACCENT, WIDTH // 2, 100, center=True)
        draw_text(surface, "Menu Principal", FONT_MED, WHITE, WIDTH // 2, 150, center=True)

        for button in self.buttons:
            button.draw(surface)
