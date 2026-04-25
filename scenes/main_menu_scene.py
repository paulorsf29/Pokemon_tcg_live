from scenes.base_scene import Scene
from settings import *
from ui import Button, draw_text

class MainMenuScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.buttons = [
            Button((490, 220, 300, 60), "Batalhar", self.go_modes),
            Button((490, 300, 300, 60), "Deck de Batalha", self.go_decks),
            Button((490, 380, 300, 60), "Perfil", self.go_profile),
            Button((490, 460, 300, 60), "Configuracoes", self.go_settings),
            Button((490, 540, 300, 60), "Sair", self.game.quit, bg=RED, hover=(170, 50, 50)),
        ]

    def go_modes(self):
        from scenes.modes_scene import ModesScene
        self.game.change_scene(ModesScene(self.game))

    def go_decks(self):
        from scenes.deck_scene import DeckScene
        self.game.change_scene(DeckScene(self.game))

    def go_profile(self):
        from scenes.profile_scene import ProfileScene
        self.game.change_scene(ProfileScene(self.game))

    def go_settings(self):
        from scenes.settings_scene import SettingsScene
        self.game.change_scene(SettingsScene(self.game))

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self, surface):
        surface.fill(BG)
        draw_text(surface, "Pokemon TCG Live", FONT_TITLE, ACCENT, WIDTH // 2, 100, center=True)
        draw_text(surface, "Menu Principal", FONT_MED, WHITE, WIDTH // 2, 150, center=True)

        for button in self.buttons:
            button.draw(surface)