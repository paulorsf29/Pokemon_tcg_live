from .base_scene import Scene
from settings import *
from render.ui.ui import Button, draw_text

class ResultScene(Scene):
    def __init__(self, game, result_title, reason):
        super().__init__(game)
        self.result_title = result_title
        self.reason = reason

        self.menu_btn = Button((490, 420, 300, 60), "Voltar ao menu", self.go_menu)
        self.exit_btn = Button((490, 500, 300, 60), "Sair", self.game.quit, bg=RED, hover=(170, 50, 50))

    def go_menu(self):
        from .main_menu_scene import MainMenuScene
        self.game.change_scene(MainMenuScene(self.game))

    def handle_event(self, event):
        self.menu_btn.handle_event(event)
        self.exit_btn.handle_event(event)

    def draw(self, surface):
        surface.fill(BG)
        color = GREEN if "Vitoria" in self.result_title else RED
        draw_text(surface, self.result_title, FONT_TITLE, color, WIDTH // 2, 180, center=True)
        draw_text(surface, self.reason, FONT_MED, WHITE, WIDTH // 2, 270, center=True)

        self.menu_btn.draw(surface)
        self.exit_btn.draw(surface)