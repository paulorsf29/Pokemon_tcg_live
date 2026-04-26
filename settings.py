import pygame
from abc import ABC, abstractmethod

pygame.init()


# ──────────────────────────────────────────────
# Strategy: ConfigProvider
# ──────────────────────────────────────────────

class ConfigProvider(ABC):
    """Estratégia abstrata para prover configuração de exibição."""

    @abstractmethod
    def get_resolution(self) -> tuple[int, int]:
        pass

    @abstractmethod
    def get_fps(self) -> int:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass


class DefaultConfigProvider(ConfigProvider):
    """Configuração padrão do jogo."""

    def get_resolution(self) -> tuple[int, int]:
        return 1280, 720

    def get_fps(self) -> int:
        return 60

    def get_title(self) -> str:
        return "Pokemon TCG Live - Prototipo"


# ──────────────────────────────────────────────
# Strategy: ColorScheme
# ──────────────────────────────────────────────

class ColorScheme(ABC):
    """Estratégia abstrata para esquema de cores."""

    @abstractmethod
    def colors(self) -> dict[str, tuple[int, int, int]]:
        pass


class DefaultColorScheme(ColorScheme):
    """Esquema de cores padrão."""

    def colors(self) -> dict[str, tuple[int, int, int]]:
        return {
            "BG": (18, 24, 38),
            "PANEL": (32, 42, 64),
            "PANEL_DARK": (24, 32, 50),
            "ACCENT": (255, 203, 5),
            "ACCENT_2": (59, 76, 202),
            "WHITE": (245, 247, 250),
            "TEXT": (230, 230, 235),
            "TEXT_DIM": (180, 190, 205),
            "GREEN": (90, 200, 120),
            "RED": (220, 80, 80),
            "GRAY": (90, 100, 120),
            "BLACK": (20, 20, 20),
            "TABLE_GREEN": (20, 110, 90),
            "TABLE_GREEN_2": (35, 65, 55),
            "TABLE_GREEN_3": (42, 85, 70),
        }


# ──────────────────────────────────────────────
# Strategy: FontProvider
# ──────────────────────────────────────────────

class FontProvider(ABC):
    """Estratégia abstrata para fontes."""

    @abstractmethod
    def get_fonts(self) -> dict[str, pygame.font.Font]:
        pass


class DefaultFontProvider(FontProvider):
    """Fontes padrão do jogo."""

    def get_fonts(self) -> dict[str, pygame.font.Font]:
        return {
            "BIG": pygame.font.SysFont("arial", 42, bold=True),
            "TITLE": pygame.font.SysFont("arial", 56, bold=True),
            "MED": pygame.font.SysFont("arial", 28, bold=True),
            "DEFAULT": pygame.font.SysFont("arial", 22),
            "SMALL": pygame.font.SysFont("arial", 18),
        }


# ──────────────────────────────────────────────
# Factory: SettingsFactory
# ──────────────────────────────────────────────

class SettingsFactory:
    """Factory que compõe as estratégias de configuração."""

    def __new__(cls, *args, **kwargs):
        raise TypeError("SettingsFactory não pode ser instanciada.")

    @staticmethod
    def build(
        config_provider: ConfigProvider = None,
        color_scheme: ColorScheme = None,
        font_provider: FontProvider = None,
    ) -> dict:
        config = config_provider or DefaultConfigProvider()
        colors = color_scheme or DefaultColorScheme()
        fonts = font_provider or DefaultFontProvider()

        w, h = config.get_resolution()
        result = {
            "WIDTH": w,
            "HEIGHT": h,
            "FPS": config.get_fps(),
            "TITLE": config.get_title(),
        }
        result.update(colors.colors())
        result["FONTS"] = fonts.get_fonts()
        return result


# ──────────────────────────────────────────────
# Instanciação global (retrocompatibilidade)
# ──────────────────────────────────────────────

_settings = SettingsFactory.build()

WIDTH = _settings["WIDTH"]
HEIGHT = _settings["HEIGHT"]
FPS = _settings["FPS"]
TITLE = _settings["TITLE"]

BG = _settings["BG"]
PANEL = _settings["PANEL"]
PANEL_DARK = _settings["PANEL_DARK"]
ACCENT = _settings["ACCENT"]
ACCENT_2 = _settings["ACCENT_2"]
WHITE = _settings["WHITE"]
TEXT = _settings["TEXT"]
TEXT_DIM = _settings["TEXT_DIM"]
GREEN = _settings["GREEN"]
RED = _settings["RED"]
GRAY = _settings["GRAY"]
BLACK = _settings["BLACK"]
TABLE_GREEN = _settings["TABLE_GREEN"]
TABLE_GREEN_2 = _settings["TABLE_GREEN_2"]
TABLE_GREEN_3 = _settings["TABLE_GREEN_3"]

_fonts = _settings["FONTS"]
FONT_BIG = _fonts["BIG"]
FONT_TITLE = _fonts["TITLE"]
FONT_MED = _fonts["MED"]
FONT = _fonts["DEFAULT"]
FONT_SMALL = _fonts["SMALL"]

# Regras de partida
TURN_TIME_LIMIT = 30
INACTIVITY_WARNING_TIME = 15
MAX_INACTIVE_TURNS = 2

# Dimensões de carta
CARD_W = 120
CARD_H = 170
