import math
import pygame
from .base_scene import Scene
from settings import *
from render.ui.ui import Button, draw_panel, draw_text
from game.battle_logic import BattleLogicFactory


class CardSprite:
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
        self.scale_pulse_time = 0

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
        self.selected = False

    def pulse(self):
        self.scale_pulse_time = 0.18

    def update(self, dt):
        if self.scale_pulse_time > 0:
            self.scale_pulse_time -= dt


class CardSpriteFactory:
    def __new__(cls, *args, **kwargs):
        raise TypeError("CardSpriteFactory não pode ser instanciada.")

    @staticmethod
    def criar_mao(hand: list[dict], start_x=180, gap=145, y=560) -> list:
        return [CardSprite(card, start_x + i * gap, y) for i, card in enumerate(hand)]


class CardVisualStrategy:
    BASE_W = CARD_W
    BASE_H = CARD_H

    @staticmethod
    def _make_font(size, bold=False):
        return pygame.font.SysFont("arial", max(12, int(size)), bold=bold)

    @staticmethod
    def _draw_on_base(card, selected=False):
        base = pygame.Surface((CardVisualStrategy.BASE_W, CardVisualStrategy.BASE_H), pygame.SRCALPHA)

        color = (250, 250, 250) if not selected else (255, 240, 180)
        pygame.draw.rect(base, color, (0, 0, CARD_W, CARD_H), border_radius=12)
        pygame.draw.rect(base, ACCENT_2, (0, 0, CARD_W, CARD_H), 3, border_radius=12)

        title_font = CardVisualStrategy._make_font(20, bold=True)
        type_font = CardVisualStrategy._make_font(16)
        info_font = CardVisualStrategy._make_font(15)

        draw_text(base, card["name"], title_font, BLACK, 10, 10)
        draw_text(base, card["type"].upper(), type_font, GRAY, 10, 40)

        if card["type"] == "pokemon":
            draw_text(base, f"HP {card.get('hp', 0)}", info_font, BLACK, 10, 68)
            draw_text(base, f"ATK {card.get('damage', 0)}", info_font, BLACK, 10, 92)
        else:
            offset_y = 68
            if card.get("heal", 0) > 0:
                draw_text(base, f"Cura {card['heal']}", info_font, BLACK, 10, offset_y)
                offset_y += 22
            if card.get("damage", 0) > 0:
                draw_text(base, f"+Dano {card['damage']}", info_font, BLACK, 10, offset_y)
                offset_y += 22
            if card.get("draw", 0) > 0:
                draw_text(base, f"Compra {card['draw']}", info_font, BLACK, 10, offset_y)
                offset_y += 22
            if card.get("prize_bonus", 0) > 0:
                draw_text(base, "+Premio", info_font, BLACK, 10, offset_y)
                offset_y += 22
            if card.get("shield", 0) > 0:
                draw_text(base, f"Escudo {card['shield']}", info_font, BLACK, 10, offset_y)

        pygame.draw.rect(base, (220, 220, 235), (10, CARD_H - 50, CARD_W - 20, 35), border_radius=8)
        return base

    @staticmethod
    def draw(surface, x, y, card, zoom=1.0, selected=False, pulse_time=0.0):
        pulse_scale = 1.0
        if pulse_time > 0:
            pulse_scale = 1.0 + math.sin((0.18 - pulse_time) * 28) * 0.10

        final_zoom = zoom * pulse_scale
        base = CardVisualStrategy._draw_on_base(card, selected=selected)

        scaled_w = max(1, int(CardVisualStrategy.BASE_W * final_zoom))
        scaled_h = max(1, int(CardVisualStrategy.BASE_H * final_zoom))
        scaled = pygame.transform.smoothscale(base, (scaled_w, scaled_h))
        surface.blit(scaled, (x, y))


class ActivePokemonVisual:
    def __init__(self, x, y):
        self.base_x = x
        self.base_y = y

        self.shake_time = 0.0
        self.shake_strength = 0
        self.shake_x = 0

        self.falling = False
        self.fall_y = 0.0
        self.angle = 0.0
        self.angular_speed = 0.0
        self.vertical_speed = 0.0

        self.hit_flash_time = 0.0
        self.frozen_card = None

    def capture(self, active):
        self.frozen_card = active.copy() if active else None

    def clear_frozen(self):
        self.frozen_card = None
        self.falling = False
        self.fall_y = 0.0
        self.angle = 0.0
        self.angular_speed = 0.0
        self.vertical_speed = 0.0
        self.hit_flash_time = 0.0
        self.shake_time = 0.0
        self.shake_x = 0

    def trigger_damage_feedback(self):
        self.shake_time = 0.28
        self.shake_strength = 10
        self.hit_flash_time = 0.12

    def trigger_fall(self, knocked_card, direction=1):
        self.frozen_card = knocked_card.copy() if knocked_card else self.frozen_card
        self.falling = True
        self.fall_y = 0.0
        self.angle = 0.0
        self.vertical_speed = -120.0
        self.angular_speed = 420.0 * direction

    def update(self, dt):
        if self.shake_time > 0:
            self.shake_time -= dt
            self.shake_x = math.sin(pygame.time.get_ticks() * 0.08) * self.shake_strength
        else:
            self.shake_x = 0

        if self.hit_flash_time > 0:
            self.hit_flash_time -= dt

        if self.falling:
            self.vertical_speed += 1450 * dt
            self.fall_y += self.vertical_speed * dt
            self.angle += self.angular_speed * dt

    def finished_fall(self):
        return self.falling and (self.base_y + self.fall_y > HEIGHT + 180)

    def current_center(self):
        return (
            self.base_x + 80 + self.shake_x,
            self.base_y + 105 + self.fall_y
        )

    def get_card_to_draw(self, live_active):
        if self.falling and self.frozen_card:
            return self.frozen_card
        return live_active


class BattleScene(Scene):
    def __init__(self, game, mode_name="Padrao", **kwargs):
        super().__init__(game)
        self.mode_name = mode_name
        selected_deck = getattr(self.game, "selected_deck", "Deck Pikachu EX")
        self.logic = BattleLogicFactory.criar(selected_deck)

        self.back_btn = Button((20, 20, 140, 46), "Render-se", self.surrender, bg=RED, hover=(170, 50, 50))
        self.end_turn_btn = Button((1035, 675, 210, 52), "Encerrar turno", self.end_turn)

        self.zoom = 1.0
        self.min_zoom = 0.85
        self.max_zoom = 1.35
        self.zoom_step = 0.05

        self.card_sprites = []
        self.selected_index = None
        self.opponent_delay = 0.8
        self._card_visual = CardVisualStrategy()

        self.player_visual = ActivePokemonVisual(720, 250)
        self.opponent_visual = ActivePokemonVisual(240, 250)

        self.pending_result = None
        self.pending_result_delay = 0.0
        self.waiting_ko_animation = False

        self.last_player_hp = None
        self.last_opponent_hp = None

        self.pre_player_active = None
        self.pre_opponent_active = None

        self.right_panel_rect = pygame.Rect(1030, 120, 220, 530)

        self.rebuild_hand_positions()
        self._sync_last_hp()

    def _sync_last_hp(self):
        self.last_player_hp = self.logic.player_active["hp"] if self.logic.player_active else None
        self.last_opponent_hp = self.logic.opponent_active["hp"] if self.logic.opponent_active else None

    def _capture_pre_action_state(self):
        self.pre_player_active = self.logic.player_active.copy() if self.logic.player_active else None
        self.pre_opponent_active = self.logic.opponent_active.copy() if self.logic.opponent_active else None

    def rebuild_hand_positions(self):
        self.card_sprites = CardSpriteFactory.criar_mao(self.logic.player_hand)

    def surrender(self):
        from .result_scene import ResultScene
        self.game.change_scene(ResultScene(self.game, result_title="Derrota", reason="Voce se rendeu"))

    def end_turn(self):
        if self.logic.current_turn == "player" and not self.waiting_ko_animation:
            self.logic.register_action()
            self.logic.end_turn()
            self.rebuild_hand_positions()

    def adjust_zoom(self, delta):
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom + delta))

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

        if target_rect.colliderect(sprite.rect(self.zoom)):
            ok, _ = self.logic.use_card_from_hand(self.selected_index)
            if ok:
                sprite.pulse()
                self.rebuild_hand_positions()
            self.selected_index = None
            return ok
        return False

    def _check_damage_feedback(self):
        if self.logic.player_active and self.last_player_hp is not None:
            if self.logic.player_active["hp"] < self.last_player_hp:
                self.player_visual.trigger_damage_feedback()

        if self.logic.opponent_active and self.last_opponent_hp is not None:
            if self.logic.opponent_active["hp"] < self.last_opponent_hp:
                self.opponent_visual.trigger_damage_feedback()

        self._sync_last_hp()

    def _start_ko_sequence_if_needed(self):
        if self.logic.winner and not self.waiting_ko_animation:
            self.pending_result = (
                "Vitoria" if self.logic.winner == "player" else "Derrota",
                self.logic.win_reason
            )
            self.pending_result_delay = 0.0
            self.waiting_ko_animation = True

            if self.logic.winner == "player":
                knocked = self.pre_opponent_active or self.logic.opponent_active
                self.opponent_visual.trigger_fall(knocked, direction=1)
            else:
                knocked = self.pre_player_active or self.logic.player_active
                self.player_visual.trigger_fall(knocked, direction=-1)

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.end_turn_btn.handle_event(event)

        if self.waiting_ko_animation or self.logic.winner:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.adjust_zoom(self.zoom_step)
                return
            elif event.button == 5:
                self.adjust_zoom(-self.zoom_step)
                return

            if event.button == 1:
                plus_rect = pygame.Rect(self.right_panel_rect.right - 30, self.right_panel_rect.bottom - 64, 24, 24)
                minus_rect = pygame.Rect(self.right_panel_rect.right - 30, self.right_panel_rect.bottom - 34, 24, 24)

                if plus_rect.collidepoint(event.pos):
                    self.adjust_zoom(self.zoom_step)
                    return
                if minus_rect.collidepoint(event.pos):
                    self.adjust_zoom(-self.zoom_step)
                    return

        if self.logic.current_turn != "player":
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_card_click(event.pos)

        elif event.type == pygame.MOUSEMOTION:
            if self.selected_index is not None:
                self.card_sprites[self.selected_index].drag(event.pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.selected_index is not None:
                idx = self.selected_index
                used = self.use_selected_card_if_dropped_on_active()
                if not used and idx is not None and 0 <= idx < len(self.card_sprites):
                    self.card_sprites[idx].reset_position()
                self.selected_index = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._capture_pre_action_state()
                ok, _ = self.logic.player_attack()
                if ok:
                    self.logic.register_action()
                    self._check_damage_feedback()
                    self._start_ko_sequence_if_needed()

            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                self.adjust_zoom(self.zoom_step)

            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                self.adjust_zoom(-self.zoom_step)

    def update(self, dt):
        for sprite in self.card_sprites:
            sprite.update(dt)

        self.player_visual.update(dt)
        self.opponent_visual.update(dt)

        if self.waiting_ko_animation:
            if self.player_visual.finished_fall() or self.opponent_visual.finished_fall():
                from .result_scene import ResultScene
                title, reason = self.pending_result
                self.game.change_scene(ResultScene(self.game, result_title=title, reason=reason))
                return

            self.pending_result_delay += dt
            if self.pending_result_delay >= 2.0:
                from .result_scene import ResultScene
                title, reason = self.pending_result
                self.game.change_scene(ResultScene(self.game, result_title=title, reason=reason))
                return
            return

        self.logic.update_timer(dt)

        if self.logic.winner:
            self._start_ko_sequence_if_needed()
            return

        if self.logic.current_turn == "opponent":
            self.opponent_delay -= dt
            if self.opponent_delay <= 0:
                self._capture_pre_action_state()
                self.logic.opponent_turn_ai()
                self._check_damage_feedback()
                self._start_ko_sequence_if_needed()
                self.opponent_delay = 0.8
                self.rebuild_hand_positions()

    def _build_active_surface(self, active, flash=False):
        surf = pygame.Surface((160, 210), pygame.SRCALPHA)
        color = (255, 255, 255) if flash else (250, 250, 250)

        pygame.draw.rect(surf, color, (0, 0, 160, 210), border_radius=14)
        pygame.draw.rect(surf, ACCENT_2, (0, 0, 160, 210), 3, border_radius=14)

        draw_text(surf, active["name"], FONT_MED, BLACK, 12, 15)
        draw_text(surf, f"HP: {active['hp']}/{active['max_hp']}", FONT_SMALL, BLACK, 12, 60)
        draw_text(surf, f"ATK: {active['damage']}", FONT_SMALL, BLACK, 12, 90)

        max_hp = max(1, active["max_hp"])
        hp_ratio = max(0, active["hp"] / max_hp)
        pygame.draw.rect(surf, GRAY, (12, 130, 130, 16), border_radius=6)
        pygame.draw.rect(
            surf,
            GREEN if hp_ratio > 0.4 else RED,
            (12, 130, int(130 * hp_ratio), 16),
            border_radius=6
        )
        return surf

    def _draw_active_with_anim(self, surface, active, label, visual):
        draw_text(surface, label, FONT, WHITE, visual.base_x, visual.base_y - 30)

        card_to_draw = visual.get_card_to_draw(active)
        if not card_to_draw:
            return

        flash = visual.hit_flash_time > 0
        base = self._build_active_surface(card_to_draw, flash=flash)
        transformed = pygame.transform.rotozoom(base, visual.angle, 1.0)
        rect = transformed.get_rect(center=visual.current_center())
        surface.blit(transformed, rect)

    def _draw_zoom_controls(self, surface):
        plus_rect = pygame.Rect(self.right_panel_rect.right - 30, self.right_panel_rect.bottom - 64, 24, 24)
        minus_rect = pygame.Rect(self.right_panel_rect.right - 30, self.right_panel_rect.bottom - 34, 24, 24)

        pygame.draw.rect(surface, (45, 52, 70), plus_rect, border_radius=8)
        pygame.draw.rect(surface, (45, 52, 70), minus_rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, plus_rect, 1, border_radius=8)
        pygame.draw.rect(surface, WHITE, minus_rect, 1, border_radius=8)

        draw_text(surface, "+", FONT_SMALL, WHITE, plus_rect.centerx, plus_rect.centery - 1, center=True)
        draw_text(surface, "-", FONT_SMALL, WHITE, minus_rect.centerx, minus_rect.centery - 1, center=True)

    def _draw_right_panel_content(self, surface, panel_rect):
        old_clip = surface.get_clip()
        surface.set_clip(panel_rect)

        center_x = panel_rect.centerx
        x = panel_rect.x + 18
        y = panel_rect.y + 24
        line_gap = 28
        block_gap = 34

        draw_text(surface, "Turno", FONT_MED, ACCENT, center_x, y, center=True)
        y += 44
        draw_text(surface, self.logic.current_turn.upper(), FONT, WHITE, center_x, y, center=True)
        y += 56

        timer_color = RED if self.logic.turn_timer <= INACTIVITY_WARNING_TIME else WHITE
        draw_text(surface, str(int(self.logic.turn_timer)), FONT_TITLE, timer_color, center_x, y, center=True)
        y += 86

        draw_text(surface, "Inatividade:", FONT, WHITE, x, y)
        y += line_gap
        draw_text(surface, f"Voce: {self.logic.inactive_turns['player']}/{MAX_INACTIVE_TURNS}", FONT_SMALL, TEXT, x, y)
        y += line_gap
        draw_text(surface, f"Oponente: {self.logic.inactive_turns['opponent']}/{MAX_INACTIVE_TURNS}", FONT_SMALL, TEXT, x, y)

        y += block_gap
        draw_text(surface, "Premios:", FONT, WHITE, x, y)
        y += line_gap
        draw_text(surface, f"Voce: {self.logic.player_prizes_taken}/6", FONT_SMALL, TEXT, x, y)
        y += line_gap
        draw_text(surface, f"Oponente: {self.logic.opponent_prizes_taken}/6", FONT_SMALL, TEXT, x, y)

        y += block_gap
        draw_text(surface, "Zoom mao:", FONT, WHITE, x, y)
        y += line_gap
        draw_text(surface, f"{self.zoom:.2f}x", FONT_SMALL, TEXT, x, y)
        y += line_gap
        draw_text(surface, "Scroll / + / -", FONT_SMALL, TEXT, x, y)

        y += block_gap
        draw_text(surface, "Comandos:", FONT, WHITE, x, y)
        y += line_gap
        draw_text(surface, "SPACE = atacar", FONT_SMALL, TEXT, x, y)

        surface.set_clip(old_clip)

    def draw(self, surface):
        surface.fill(TABLE_GREEN)
        draw_text(surface, f"Batalha - {self.mode_name}", FONT_BIG, WHITE, WIDTH // 2, 30, center=True)

        draw_panel(surface, pygame.Rect(120, 70, 1040, 120), color=TABLE_GREEN_2)
        draw_text(surface, "Oponente", FONT_MED, WHITE, 150, 90)
        draw_text(surface, f"Premios: {self.logic.opponent_prizes_taken}/6", FONT, WHITE, 150, 125)
        draw_text(surface, f"Deck: {len(self.logic.opponent_deck)}", FONT, WHITE, 150, 150)

        draw_panel(surface, pygame.Rect(180, 215, 920, 250), color=TABLE_GREEN_3)

        self._draw_active_with_anim(surface, self.logic.opponent_active, "Pokemon Ativo do Oponente", self.opponent_visual)
        self._draw_active_with_anim(surface, self.logic.player_active, "Seu Pokemon Ativo", self.player_visual)

        draw_panel(surface, pygame.Rect(70, 520, 930, 170), color=TABLE_GREEN_2)
        draw_text(surface, "Sua mao", FONT_MED, WHITE, 100, 540)

        for i, sprite in enumerate(self.card_sprites):
            selected = (i == self.selected_index)
            self._card_visual.draw(
                surface,
                sprite.x,
                sprite.y,
                sprite.data,
                zoom=self.zoom,
                selected=selected,
                pulse_time=sprite.scale_pulse_time
            )

        draw_panel(surface, self.right_panel_rect, color=PANEL_DARK)
        self._draw_right_panel_content(surface, self.right_panel_rect)
        self._draw_zoom_controls(surface)

        self.back_btn.draw(surface)
        self.end_turn_btn.draw(surface)