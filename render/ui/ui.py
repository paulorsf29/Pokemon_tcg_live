import pygame
from abc import ABC, abstractmethod
from settings import *


# ──────────────────────────────────────────────
# Strategy: RenderStrategy (abstração de desenho)
# ──────────────────────────────────────────────

class RenderStrategy(ABC):
    """Estratégia abstrata para renderizar um componente de UI."""

    @abstractmethod
    def render(self, surface: pygame.Surface, **kwargs) -> pygame.Rect:
        pass


class TextRenderStrategy(RenderStrategy):
    """Estratégia de renderização de texto."""

    def render(self, surface, text="", font=None, color=WHITE, x=0, y=0, center=False, **kwargs):
        font = font or FONT
        img = font.render(str(text), True, color)
        rect = img.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        surface.blit(img, rect)
        return rect


class PanelRenderStrategy(RenderStrategy):
    """Estratégia de renderização de painéis."""

    def render(self, surface, rect=None, color=PANEL, border_color=WHITE, radius=16, border=2, **kwargs):
        pygame.draw.rect(surface, color, rect, border_radius=radius)
        pygame.draw.rect(surface, border_color, rect, width=border, border_radius=radius)
        return rect


# ──────────────────────────────────────────────
# Funções utilitárias (retrocompatibilidade)
# ──────────────────────────────────────────────

_text_renderer = TextRenderStrategy()
_panel_renderer = PanelRenderStrategy()


def draw_text(surface, text, font, color, x, y, center=False):
    """Atalho retrocompatível, delega para TextRenderStrategy."""
    return _text_renderer.render(surface, text=text, font=font, color=color, x=x, y=y, center=center)


def draw_panel(surface, rect, color=PANEL, border_color=WHITE, radius=16, border=2):
    """Atalho retrocompatível, delega para PanelRenderStrategy."""
    return _panel_renderer.render(surface, rect=rect, color=color, border_color=border_color, radius=radius, border=border)


# ──────────────────────────────────────────────
# Strategy: InputHandlerStrategy
# ──────────────────────────────────────────────

class InputHandlerStrategy(ABC):
    """Estratégia abstrata para processamento de input."""

    @abstractmethod
    def handle(self, event: pygame.event.Event) -> bool:
        """Retorna True se consumiu o evento."""
        pass


# ──────────────────────────────────────────────
# Composição: UIComponent (base de todos os widgets)
# ──────────────────────────────────────────────

class UIComponent(ABC):
    """Classe base para componentes de UI com composição de estratégias."""

    def __init__(self, render_strategy: RenderStrategy = None):
        self._render_strategy = render_strategy

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass


# ──────────────────────────────────────────────
# Componente: Button (composição de render + input)
# ──────────────────────────────────────────────

class ButtonInputHandler(InputHandlerStrategy):
    """Estratégia de input para botões com clique."""

    def __init__(self, rect: pygame.Rect, callback):
        self.rect = rect
        self.callback = callback

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False


class ButtonRenderStrategy(RenderStrategy):
    """Estratégia de renderização de botões."""

    def render(self, surface, rect=None, text="", bg=PANEL, hover=ACCENT_2, fg=WHITE, **kwargs):
        mouse = pygame.mouse.get_pos()
        color = hover if rect.collidepoint(mouse) else bg
        pygame.draw.rect(surface, color, rect, border_radius=14)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=14)
        draw_text(surface, text, FONT_MED, fg, rect.centerx, rect.centery, center=True)
        return rect


class Button(UIComponent):
    """Botão composto por ButtonRenderStrategy + ButtonInputHandler."""

    def __init__(self, rect, text, callback, bg=PANEL, hover=ACCENT_2, fg=WHITE):
        super().__init__(ButtonRenderStrategy())
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg = bg
        self.hover = hover
        self.fg = fg
        self._input_handler = ButtonInputHandler(self.rect, callback)

    def draw(self, surface):
        self._render_strategy.render(
            surface, rect=self.rect, text=self.text,
            bg=self.bg, hover=self.hover, fg=self.fg
        )

    def handle_event(self, event):
        self._input_handler.handle(event)


# ──────────────────────────────────────────────
# Componente: Slider (composição de render + input)
# ──────────────────────────────────────────────

class SliderInputHandler(InputHandlerStrategy):
    """Estratégia de input para sliders de arrastar."""

    def __init__(self, slider):
        self.slider = slider

    def handle(self, event):
        knob_rect = pygame.Rect(self.slider.knob_x - 14, self.slider.rect.centery - 14, 28, 28)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if knob_rect.collidepoint(event.pos):
                self.slider.dragging = True
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.slider.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.slider.dragging:
            self.slider.knob_x = max(self.slider.rect.left, min(event.pos[0], self.slider.rect.right))
            self.slider.value = int(((self.slider.knob_x - self.slider.rect.x) / self.slider.rect.w) * 100)
            return True

        return False


class SliderRenderStrategy(RenderStrategy):
    """Estratégia de renderização de sliders."""

    def render(self, surface, slider=None, **kwargs):
        draw_text(surface, f"{slider.label}: {slider.value}%", FONT, TEXT, slider.rect.x, slider.rect.y - 35)
        pygame.draw.rect(surface, GRAY, slider.rect, border_radius=5)
        pygame.draw.circle(surface, ACCENT, (slider.knob_x, slider.rect.centery), 12)
        return slider.rect


class Slider(UIComponent):
    """Slider composto por SliderRenderStrategy + SliderInputHandler."""

    def __init__(self, x, y, w, label, value=50):
        super().__init__(SliderRenderStrategy())
        self.rect = pygame.Rect(x, y, w, 8)
        self.knob_x = x + int((value / 100) * w)
        self.label = label
        self.value = value
        self.dragging = False
        self._input_handler = SliderInputHandler(self)

    def draw(self, surface):
        self._render_strategy.render(surface, slider=self)

    def handle_event(self, event):
        self._input_handler.handle(event)


# ──────────────────────────────────────────────
# Factory: UIComponentFactory
# ──────────────────────────────────────────────

class UIComponentFactory:
    """Factory para criar componentes de UI de forma genérica."""

    _registry: dict[str, type] = {
        "button": Button,
        "slider": Slider,
    }

    def __new__(cls, *args, **kwargs):
        raise TypeError("UIComponentFactory não pode ser instanciada.")

    @classmethod
    def registrar(cls, nome: str, component_class: type):
        cls._registry[nome] = component_class

    @classmethod
    def criar(cls, tipo: str, **kwargs) -> UIComponent:
        component_class = cls._registry.get(tipo)
        if component_class is None:
            raise ValueError(f"Componente UI desconhecido: {tipo}")
        return component_class(**kwargs)
