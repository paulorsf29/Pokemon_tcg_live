import sys
import pygame
from settings import WIDTH, HEIGHT, FPS, TITLE

class SceneFactory:
    """Factory para criação de cenas por nome registrado."""

    _registry: dict[str, type] = {}

    def __new__(cls, *args, **kwargs):
        raise TypeError("SceneFactory não pode ser instanciada.")

    @classmethod
    def registrar(cls, nome: str, scene_class: type):
        cls._registry[nome] = scene_class

    @classmethod
    def criar(cls, nome: str, game, **kwargs):
        scene_class = cls._registry.get(nome)
        if scene_class is None:
            raise ValueError(f"Cena desconhecida: {nome}")
        return scene_class(game, **kwargs)

    @classmethod
    def listar(cls) -> list[str]:
        return list(cls._registry.keys())


# ──────────────────────────────────────────────
# Composição: Game (loop principal + SceneFactory)
# ──────────────────────────────────────────────

class Game:
    """Loop principal do jogo, composto por cenas via SceneFactory."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_deck = "Deck Pikachu EX"

        # Registra todas as cenas disponíveis
        self._register_scenes()

        # Cena inicial via factory
        self.scene = SceneFactory.criar("splash", self)

    def _register_scenes(self):
        """Registra cenas no SceneFactory sob demanda (lazy import)."""
        from .scenes.splash_scene import SplashScene
        from .scenes.main_menu_scene import MainMenuScene
        from .scenes.deck_scene import DeckScene
        from .scenes.modes_scene import ModesScene
        from .scenes.battle_scene import BattleScene
        from .scenes.result_scene import ResultScene
        from .scenes.profile_scene import ProfileScene
        from .scenes.settings_scene import SettingsScene

        SceneFactory.registrar("splash", SplashScene)
        SceneFactory.registrar("main_menu", MainMenuScene)
        SceneFactory.registrar("deck", DeckScene)
        SceneFactory.registrar("modes", ModesScene)
        SceneFactory.registrar("battle", BattleScene)
        SceneFactory.registrar("result", ResultScene)
        SceneFactory.registrar("profile", ProfileScene)
        SceneFactory.registrar("settings", SettingsScene)

    def change_scene(self, new_scene):
        """Aceita tanto instância direta quanto nome de cena via factory."""
        if isinstance(new_scene, str):
            self.scene = SceneFactory.criar(new_scene, self)
        else:
            self.scene = new_scene

    def change_scene_by_name(self, name: str, **kwargs):
        """Troca de cena por nome registrado, passando kwargs extras."""
        self.scene = SceneFactory.criar(name, self, **kwargs)

    def quit(self):
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        sys.exit()
