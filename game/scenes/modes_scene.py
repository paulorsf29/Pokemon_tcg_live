from .base_scene import Scene
from settings import *
from render.ui.ui  import Button, draw_panel, draw_text

class ModesScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.buttons = [
            Button((380, 260, 240, 80), "Padrao", self.play_standard),
            Button((660, 260, 240, 80), "Ranqueado", self.play_ranked),
            Button((30, 30, 140, 50), "Voltar", self.go_back),
        ]

    def play_standard(self):
        from .battle_scene import BattleScene
        self.game.change_scene(BattleScene(self.game, "Padrao"))

    def play_ranked(self):
        from .battle_scene import BattleScene
        self.game.change_scene(BattleScene(self.game, "Ranqueado"))

    def go_back(self):
        from .main_menu_scene import MainMenuScene
        self.game.change_scene(MainMenuScene(self.game))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, surface):
        surface.fill(BG)
        draw_text(surface, "Selecao de Modo", FONT_TITLE, ACCENT, WIDTH // 2, 90, center=True)

        draw_panel(surface, pygame.Rect(300, 180, 680, 260))
        draw_text(surface, "Escolha o modo de batalha", FONT_MED, WHITE, WIDTH // 2, 210, center=True)
        draw_text(surface, "Padrao: partidas casuais sem premios externos.", FONT, TEXT_DIM, WIDTH // 2, 380, center=True)
        draw_text(surface, "Ranqueado: modo competitivo com progressao.", FONT, TEXT_DIM, WIDTH // 2, 410, center=True)

        for button in self.buttons:
            button.draw(surface)