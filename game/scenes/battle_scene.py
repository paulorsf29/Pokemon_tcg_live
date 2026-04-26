import pygame
from .base_scene import Scene
from settings import *
from render.ui.ui import Button, draw_panel, draw_text
from game.battle_logic import BattleLogicFactory

class CardSprite:
    """Representação visual de uma carta na mão."""

    def __init__(self, data, x, y):
        self.data = data
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.w = CARD_W
        self.h = CARD_H
        self.dragging = False
        self.selected = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    def rect(self, zoom=1.0):
        return pygame.Rect(self.x, self.y, int(self.w * zoom), int(self.h * zoom))

    def contains_point(self, pos, zoom=1.0):
        return self.rect(zoom).collidepoint(pos)

    def start_drag(self, mouse_pos):
        self.dragging = True
        self.drag_offset_x = mouse_pos[0] - self.x
        self.drag_offset_y = mouse_pos[1] - self.y

    def drag(self, mouse_pos):
        self.x = mouse_pos[0] - self.drag_offset_x
        self.y = mouse_pos[1] - self.drag_offset_y

    def reset_position(self):
        self.x = self.base_x
        self.y = self.base_y
        self.dragging = False


class CardSpriteFactory:
    """Factory para criar sprites de cartas na mão do jogador."""

    def __new__(cls, *args, **kwargs):
        raise TypeError("CardSpriteFactory não pode ser instanciada.")

    @staticmethod
    def criar_mao(hand: list[dict], start_x=180, gap=145, y=560) -> list[CardSprite]:
        return [CardSprite(card, start_x + i * gap, y) for i, card in enumerate(hand)]

class CardVisualStrategy:
    """Estratégia de renderização visual de uma carta."""

    @staticmethod
    def draw(surface, x, y, card, zoom=1.0, selected=False):
        w = int(CARD_W * zoom)
        h = int(CARD_H * zoom)
        rect = pygame.Rect(x, y, w, h)
        color = (250, 250, 250) if not selected else (255, 240, 180)

        pygame.draw.rect(surface, color, rect, border_radius=12)
        pygame.draw.rect(surface, ACCENT_2, rect, 3, border_radius=12)

        draw_text(surface, card["name"], FONT_SMALL, BLACK, x + 10, y + 12)
        draw_text(surface, card["type"].upper(), FONT_SMALL, GRAY, x + 10, y + 38)

        if card["type"] == "pokemon":
            draw_text(surface, f"HP {card['hp']}", FONT_SMALL, BLACK, x + 10, y + 64)
            draw_text(surface, f"ATK {card['damage']}", FONT_SMALL, BLACK, x + 10, y + 88)
        else:
            offset_y = 64
            if card["heal"] > 0:
                draw_text(surface, f"Cura {card['heal']}", FONT_SMALL, BLACK, x + 10, y + offset_y)
                offset_y += 24
            if card["damage"] > 0:
                draw_text(surface, f"+Dano {card['damage']}", FONT_SMALL, BLACK, x + 10, y + offset_y)
                offset_y += 24
            if card["draw"] > 0:
                draw_text(surface, f"Compra {card['draw']}", FONT_SMALL, BLACK, x + 10, y + offset_y)
                offset_y += 24
            if card["prize_bonus"] > 0:
                draw_text(surface, "+Premio", FONT_SMALL, BLACK, x + 10, y + offset_y)
                offset_y += 24
            if card["shield"] > 0:
                draw_text(surface, f"Escudo {card['shield']}", FONT_SMALL, BLACK, x + 10, y + offset_y)

        pygame.draw.rect(surface, (220, 220, 235), (x + 10, y + h - 50, w - 20, 35), border_radius=8)

class BattleScene(Scene):
    def __init__(self, game, mode_name="Padrao", **kwargs):
        super().__init__(game)
        self.mode_name = mode_name
        selected_deck = getattr(self.game, "selected_deck", "Deck Pikachu EX")

        # Usa BattleLogicFactory para criar a lógica
        self.logic = BattleLogicFactory.criar(selected_deck)

        self.back_btn = Button((20, 20, 140, 46), "Render-se", self.surrender, bg=RED, hover=(170, 50, 50))
        self.end_turn_btn = Button((1040, 640, 190, 50), "Encerrar turno", self.end_turn)

        self.card_sprites = []
        self.selected_index = None
        self.zoom = 1.0
        self.min_zoom = 1.0
        self.max_zoom = 1.25
        self.opponent_delay = 0.8

        # Estratégia de renderização de cartas
        self._card_visual = CardVisualStrategy()

        self.rebuild_hand_positions()

    def rebuild_hand_positions(self):
        self.card_sprites = CardSpriteFactory.criar_mao(self.logic.player_hand)

    def surrender(self):
        from .result_scene import ResultScene
        self.game.change_scene(ResultScene(self.game, result_title="Derrota", reason="Voce se rendeu"))

    def end_turn(self):
        if self.logic.current_turn == "player":
            self.logic.register_action()
            self.logic.end_turn()
            self.rebuild_hand_positions()

    def handle_card_click(self, mouse_pos):
        for i in range(len(self.card_sprites) - 1, -1, -1):
            sprite = self.card_sprites[i]
            if sprite.contains_point(mouse_pos, self.zoom):
                self.selected_index = i
                sprite.selected = True
                sprite.start_drag(mouse_pos)
                self.logic.register_action()
                return

    def use_selected_card_if_dropped_on_active(self):
        if self.selected_index is None:
            return False

        sprite = self.card_sprites[self.selected_index]
        target_rect = pygame.Rect(720, 270, CARD_W, CARD_H)

        if target_rect.colliderect(sprite.rect()):
            ok, _ = self.logic.use_card_from_hand(self.selected_index)
            self.rebuild_hand_positions()
            self.selected_index = None
            return ok
        return False

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.end_turn_btn.handle_event(event)

        if self.logic.winner:
            return

        if self.logic.current_turn != "player":
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.handle_card_click(event.pos)
            elif event.button == 4:
                self.zoom = min(self.max_zoom, self.zoom + 0.05)
            elif event.button == 5:
                self.zoom = max(self.min_zoom, self.zoom - 0.05)

        elif event.type == pygame.MOUSEMOTION:
            if self.selected_index is not None:
                self.card_sprites[self.selected_index].drag(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.selected_index is not None:
                idx = self.selected_index
                used = self.use_selected_card_if_dropped_on_active()
                # use_selected_... pode ter zerado selected_index e recriado a lista;
                # só reseta posição se o índice antigo ainda for válido na lista atual.
                if not used and idx is not None and 0 <= idx < len(self.card_sprites):
                    self.card_sprites[idx].reset_position()
                self.selected_index = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ok, _ = self.logic.player_attack()
                if ok:
                    self.logic.register_action()

    def update(self, dt):
        if self.logic.winner:
            title = "Vitoria" if self.logic.winner == "player" else "Derrota"
            from .result_scene import ResultScene
            self.game.change_scene(ResultScene(self.game, result_title=title, reason=self.logic.win_reason))
            return

        self.logic.update_timer(dt)

        if self.logic.winner:
            return

        if self.logic.current_turn == "opponent":
            self.opponent_delay -= dt
            if self.opponent_delay <= 0:
                self.logic.opponent_turn_ai()
                self.opponent_delay = 0.8
                self.rebuild_hand_positions()

    def draw_active_pokemon(self, surface, x, y, active, label):
        draw_text(surface, label, FONT, WHITE, x, y - 30)
        rect = pygame.Rect(x, y, 160, 210)
        pygame.draw.rect(surface, (250, 250, 250), rect, border_radius=14)
        pygame.draw.rect(surface, ACCENT_2, rect, 3, border_radius=14)

        draw_text(surface, active["name"], FONT_MED, BLACK, x + 12, y + 15)
        draw_text(surface, f"HP: {active['hp']}/{active['max_hp']}", FONT_SMALL, BLACK, x + 12, y + 60)
        draw_text(surface, f"ATK: {active['damage']}", FONT_SMALL, BLACK, x + 12, y + 90)

        hp_ratio = max(0, active["hp"] / active["max_hp"])
        pygame.draw.rect(surface, GRAY, (x + 12, y + 130, 130, 16), border_radius=6)
        pygame.draw.rect(surface, GREEN if hp_ratio > 0.4 else RED, (x + 12, y + 130, int(130 * hp_ratio), 16), border_radius=6)

    def draw(self, surface):
        surface.fill(TABLE_GREEN)
        draw_text(surface, f"Batalha - {self.mode_name}", FONT_BIG, WHITE, WIDTH // 2, 30, center=True)

        draw_panel(surface, pygame.Rect(120, 70, 1040, 120), color=TABLE_GREEN_2)
        draw_text(surface, "Oponente", FONT_MED, WHITE, 150, 90)
        draw_text(surface, f"Premios: {self.logic.opponent_prizes_taken}/6", FONT, WHITE, 150, 125)
        draw_text(surface, f"Deck: {len(self.logic.opponent_deck)}", FONT, WHITE, 150, 150)

        draw_panel(surface, pygame.Rect(180, 215, 920, 250), color=TABLE_GREEN_3)

        if self.logic.opponent_active:
            self.draw_active_pokemon(surface, 240, 250, self.logic.opponent_active, "Pokemon Ativo do Oponente")
        if self.logic.player_active:
            self.draw_active_pokemon(surface, 720, 250, self.logic.player_active, "Seu Pokemon Ativo")

        draw_panel(surface, pygame.Rect(70, 520, 930, 170), color=TABLE_GREEN_2)
        draw_text(surface, "Sua mao", FONT_MED, WHITE, 100, 540)

        for i, sprite in enumerate(self.card_sprites):
            selected = (i == self.selected_index)
            self._card_visual.draw(surface, sprite.x, sprite.y, sprite.data, zoom=self.zoom, selected=selected)

        draw_panel(surface, pygame.Rect(1030, 120, 210, 500), color=PANEL_DARK)
        draw_text(surface, "Turno", FONT_MED, ACCENT, 1135, 155, center=True)
        draw_text(surface, self.logic.current_turn.upper(), FONT, WHITE, 1135, 190, center=True)

        timer_color = RED if self.logic.turn_timer <= INACTIVITY_WARNING_TIME else WHITE
        draw_text(surface, int(self.logic.turn_timer), FONT_TITLE, timer_color, 1135, 245, center=True)

        draw_text(surface, "Inatividade:", FONT, WHITE, 1060, 320)
        draw_text(surface, f"Voce: {self.logic.inactive_turns['player']}/{MAX_INACTIVE_TURNS}", FONT_SMALL, TEXT, 1060, 350)
        draw_text(surface, f"Oponente: {self.logic.inactive_turns['opponent']}/{MAX_INACTIVE_TURNS}", FONT_SMALL, TEXT, 1060, 375)

        draw_text(surface, "Premios:", FONT, WHITE, 1060, 430)
        draw_text(surface, f"Voce: {self.logic.player_prizes_taken}/6", FONT_SMALL, TEXT, 1060, 460)
        draw_text(surface, f"Oponente: {self.logic.opponent_prizes_taken}/6", FONT_SMALL, TEXT, 1060, 485)

        draw_text(surface, "Comandos:", FONT, WHITE, 1060, 535)
        draw_text(surface, "Arraste carta para", FONT_SMALL, TEXT, 1060, 565)
        draw_text(surface, "seu pokemon ativo", FONT_SMALL, TEXT, 1060, 590)
        draw_text(surface, "SPACE = atacar", FONT_SMALL, TEXT, 1060, 615)
        draw_text(surface, "Scroll = zoom", FONT_SMALL, TEXT, 1060, 640)

        self.back_btn.draw(surface)
        self.end_turn_btn.draw(surface)
