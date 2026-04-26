from .base_scene import Scene
from settings import *
from render.ui.ui import draw_text


class SplashScene(Scene):
    def __init__(self, game, **kwargs):
        super().__init__(game)
        self.timer = 2.5

    def update(self, dt):
        self.timer -= dt
        if self.timer <= 0:
            self.navigate_to("main_menu")

    def draw(self, surface):
        surface.fill(BG)
        draw_text(surface, "Pokemon TCG Live", FONT_TITLE, ACCENT, WIDTH // 2, HEIGHT // 2 - 20, center=True)
        draw_text(surface, "Prototipo em Pygame", FONT_MED, WHITE, WIDTH // 2, HEIGHT // 2 + 40, center=True)
