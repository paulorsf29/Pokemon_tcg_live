from abc import ABC, abstractmethod


class SceneTransitionStrategy(ABC):
    """Estratégia abstrata para transição entre cenas."""

    @abstractmethod
    def transition(self, game, target_scene_name: str, **kwargs):
        pass


class DirectTransitionStrategy(SceneTransitionStrategy):
    """Transição direta sem efeitos."""

    def transition(self, game, target_scene_name: str, **kwargs):
        from game.game import SceneFactory
        game.change_scene(SceneFactory.criar(target_scene_name, game, **kwargs))


class Scene:
    """Classe base de cena com composição de estratégia de transição."""

    def __init__(self, game, transition_strategy: SceneTransitionStrategy = None):
        self.game = game
        self._transition = transition_strategy or DirectTransitionStrategy()

    def navigate_to(self, scene_name: str, **kwargs):
        """Navega para outra cena usando a estratégia de transição."""
        self._transition.transition(self.game, scene_name, **kwargs)

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass
