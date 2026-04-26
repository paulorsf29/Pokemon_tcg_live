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
    def criar_mao(hand: list[dict], start_x=180, y=560) -> list:
        return [CardSprite(card, start_x, y) for card in hand]


class CardVisualStrategy:
    BASE_W = CARD_W
    BASE_H = CARD_H

    @staticmethod
    def _fit_font_for_text(text, max_width, start_size, min_size=10, bold=False):
        size = start_size
        while size >= min_size:
            font = pygame.font.SysFont("arial", size, bold=bold)
            if font.size(text)[0] <= max_width:
                return font
            size -= 1
        return pygame.font.SysFont("arial", min_size, bold=bold)

    @staticmethod
    def _ellipsize(text, font, max_width):
        if font.size(text)[0] <= max_width:
            return text
        result = text
        while len(result) > 0 and font.size(result + "...")[0] > max_width:
            result = result[:-1]
        return result + "..."

    @staticmethod
    def _draw_fitted_text(base, text, color, x, y, max_width, start_size, min_size=10, bold=False):
        font = CardVisualStrategy._fit_font_for_text(text, max_width, start_size, min_size, bold)
        final_text = CardVisualStrategy._ellipsize(text, font, max_width)
        draw_text(base, final_text, font, color, x, y)

    @staticmethod
    def _draw_card_3d_face(base, rect, selected=False):
        x, y, w, h = rect
        fill = (252, 252, 252) if not selected else (255, 244, 200)
        border = (66, 86, 210)

        pygame.draw.rect(base, fill, (x, y, w, h), border_radius=14)
        pygame.draw.rect(base, border, (x, y, w, h), 3, border_radius=14)

        top_glow = pygame.Surface((w - 10, 12), pygame.SRCALPHA)
        pygame.draw.rect(top_glow, (255, 255, 255, 85), (0, 0, w - 10, 12), border_radius=8)
        base.blit(top_glow, (x + 5, y + 4))

        side_shadow = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.line(side_shadow, (0, 0, 0, 30), (w - 8, 10), (w - 8, h - 14), 4)
        pygame.draw.line(side_shadow, (0, 0, 0, 18), (10, h - 8), (w - 10, h - 8), 3)
        base.blit(side_shadow, (x, y))

    @staticmethod
    def _draw_hp_bar(base, x, y, w, ratio):
        pygame.draw.rect(base, GRAY, (x, y, w, 18), border_radius=8)
        fill_w = max(0, int(w * ratio))
        pygame.draw.rect(base, GREEN if ratio > 0.4 else RED, (x, y, fill_w, 18), border_radius=8)

    @staticmethod
    def _draw_on_base(card, selected=False, w=None, h=None):
        w = w or CARD_W
        h = h or CARD_H

        base = pygame.Surface((w, h), pygame.SRCALPHA)
        CardVisualStrategy._draw_card_3d_face(base, (0, 0, w, h), selected=selected)

        pad_x = 12
        text_w = w - 24

        CardVisualStrategy._draw_fitted_text(
            base, card.get("name", "Carta"), BLACK, pad_x, 12, text_w, start_size=22, min_size=11, bold=True
        )
        CardVisualStrategy._draw_fitted_text(
            base, card.get("type", "").upper(), GRAY, pad_x, 46, text_w, start_size=16, min_size=10
        )

        if card.get("type") == "pokemon":
            CardVisualStrategy._draw_fitted_text(
                base,
                f"HP: {card.get('hp', 0)}/{card.get('max_hp', card.get('hp', 0))}",
                BLACK, pad_x, 82, text_w, start_size=17, min_size=10
            )
            CardVisualStrategy._draw_fitted_text(
                base,
                f"ATK: {card.get('damage', 0)}",
                BLACK, pad_x, 112, text_w, start_size=17, min_size=10
            )

            max_hp = max(1, card.get("max_hp", card.get("hp", 1)))
            hp_ratio = max(0, min(1, card.get("hp", 0) / max_hp))
            CardVisualStrategy._draw_hp_bar(base, 12, h - 44, w - 24, hp_ratio)
        else:
            offset_y = 74
            lines = []

            if card.get("heal", 0) > 0:
                lines.append(f"Cura {card['heal']}")
            if card.get("damage", 0) > 0:
                lines.append(f"+Dano {card['damage']}")
            if card.get("draw", 0) > 0:
                lines.append(f"Compra {card['draw']}")
            if card.get("prize_bonus", 0) > 0:
                lines.append("+Premio")
            if card.get("shield", 0) > 0:
                lines.append(f"Escudo {card['shield']}")
            if not lines:
                lines.append("Sem efeito")

            for line in lines[:4]:
                CardVisualStrategy._draw_fitted_text(
                    base, line, BLACK, pad_x, offset_y, text_w, start_size=15, min_size=10
                )
                offset_y += 22

            pygame.draw.rect(base, (220, 220, 235), (12, h - 48, w - 24, 34), border_radius=8)

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
    def __init__(self, x, y, facing_angle=0):
        self.base_x = x
        self.base_y = y
        self.facing_angle = facing_angle
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
        return self.base_x + self.shake_x, self.base_y + self.fall_y

    def current_angle(self):
        return self.facing_angle + self.angle

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

        self.center_battle_rect = pygame.Rect(140, 190, 980, 320)
        self.player_visual = ActivePokemonVisual(760, 355, facing_angle=-8)
        self.opponent_visual = ActivePokemonVisual(430, 355, facing_angle=8)

        self.pending_result = None
        self.pending_result_delay = 0.0
        self.waiting_ko_animation = False

        self.last_player_hp = None
        self.last_opponent_hp = None

        self.pre_player_active = None
        self.pre_opponent_active = None

        self.right_panel_rect = pygame.Rect(1030, 120, 220, 530)

        self.hand_panel_rect = pygame.Rect(70, 545, 930, 170)
        self.hand_view_rect = pygame.Rect(115, 585, 820, 120)
        self.hand_start_x = self.hand_view_rect.x
        self.hand_y = self.hand_view_rect.y
        self.hand_scroll_x = 0
        self.hand_min_gap = 18

        self.left_arrow_rect = pygame.Rect(80, 620, 28, 50)
        self.right_arrow_rect = pygame.Rect(945, 620, 28, 50)

        self.active_card_size = (200, 260)

        self.rebuild_hand_positions()
        self._sync_last_hp()

    def _sync_last_hp(self):
        self.last_player_hp = self.logic.player_active["hp"] if self.logic.player_active else None
        self.last_opponent_hp = self.logic.opponent_active["hp"] if self.logic.opponent_active else None

    def _capture_pre_action_state(self):
        self.pre_player_active = self.logic.player_active.copy() if self.logic.player_active else None
        self.pre_opponent_active = self.logic.opponent_active.copy() if self.logic.opponent_active else None

    def _card_draw_size(self):
        return int(CARD_W * self.zoom), int(CARD_H * self.zoom)

    def _scaled_gap(self):
        return max(self.hand_min_gap, int(18 * self.zoom))

    def _total_hand_width(self):
        if not self.card_sprites:
            return 0
        card_w, _ = self._card_draw_size()
        gap = self._scaled_gap()
        return len(self.card_sprites) * card_w + (len(self.card_sprites) - 1) * gap

    def _max_hand_scroll(self):
        return max(0, self._total_hand_width() - self.hand_view_rect.width)

    def _clamp_hand_scroll(self):
        self.hand_scroll_x = max(0, min(self.hand_scroll_x, self._max_hand_scroll()))

    def _layout_hand_cards(self):
        card_w, _ = self._card_draw_size()
        gap = self._scaled_gap()

        for i, sprite in enumerate(self.card_sprites):
            target_x = self.hand_start_x + i * (card_w + gap) - self.hand_scroll_x
            sprite.base_x = target_x
            if not sprite.dragging:
                sprite.x = target_x
                sprite.y = self.hand_y

    def rebuild_hand_positions(self):
        self.card_sprites = CardSpriteFactory.criar_mao(self.logic.player_hand, start_x=self.hand_start_x, y=self.hand_y)
        self._clamp_hand_scroll()
        self._layout_hand_cards()

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
        self._clamp_hand_scroll()
        self._layout_hand_cards()

    def scroll_hand(self, delta):
        self.hand_scroll_x += delta
        self._clamp_hand_scroll()
        self._layout_hand_cards()

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
        target_rect = pygame.Rect(660, 225, 260, 280)

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

        mouse_pos = pygame.mouse.get_pos()
        mouse_in_hand = self.hand_view_rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                if mouse_in_hand:
                    self.scroll_hand(-120)
                else:
                    self.adjust_zoom(self.zoom_step)
                return

            elif event.button == 5:
                if mouse_in_hand:
                    self.scroll_hand(120)
                else:
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
                if self.left_arrow_rect.collidepoint(event.pos):
                    self.scroll_hand(-180)
                    return
                if self.right_arrow_rect.collidepoint(event.pos):
                    self.scroll_hand(180)
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
                    self._layout_hand_cards()
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

            elif event.key == pygame.K_LEFT:
                self.scroll_hand(-180)

            elif event.key == pygame.K_RIGHT:
                self.scroll_hand(180)

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

    def _draw_active_ground_shadow(self, surface, center_x, center_y, width=170, height=36):
        shadow = pygame.Surface((width + 30, height + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 85), (10, 4, width, height))
        pygame.draw.ellipse(shadow, (0, 0, 0, 45), (18, 10, width - 16, height - 10))
        surface.blit(shadow, (center_x - (width + 30) // 2, center_y + 118))

    def _build_active_surface(self, active, flash=False):
        w, h = self.active_card_size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (255, 228, 228) if flash else (250, 250, 250)

        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=16)
        pygame.draw.rect(surf, ACCENT_2, (0, 0, w, h), 4, border_radius=16)

        shine = pygame.Surface((w - 12, 16), pygame.SRCALPHA)
        pygame.draw.rect(shine, (255, 255, 255, 90), (0, 0, w - 12, 16), border_radius=10)
        surf.blit(shine, (6, 5))

        text_w = w - 28
        name_font = CardVisualStrategy._fit_font_for_text(active["name"], text_w, 24, min_size=12, bold=True)
        final_name = CardVisualStrategy._ellipsize(active["name"], name_font, text_w)
        draw_text(surf, final_name, name_font, BLACK, 14, 18)

        CardVisualStrategy._draw_fitted_text(
            surf, f"HP: {active['hp']}/{active['max_hp']}", BLACK, 14, 78, text_w, start_size=20, min_size=11
        )
        CardVisualStrategy._draw_fitted_text(
            surf, f"ATK: {active['damage']}", BLACK, 14, 112, text_w, start_size=20, min_size=11
        )

        max_hp = max(1, active["max_hp"])
        hp_ratio = max(0, active["hp"] / max_hp)
        pygame.draw.rect(surf, GRAY, (14, h - 52, w - 28, 18), border_radius=8)
        pygame.draw.rect(
            surf,
            GREEN if hp_ratio > 0.4 else RED,
            (14, h - 52, int((w - 28) * hp_ratio), 18),
            border_radius=8
        )
        return surf

    def _draw_active_with_anim(self, surface, active, label, visual):
        label_x = visual.base_x
        label_y = visual.base_y - 175
        draw_text(surface, label, FONT, WHITE, label_x, label_y, center=True)

        card_to_draw = visual.get_card_to_draw(active)
        if not card_to_draw:
            return

        flash = visual.hit_flash_time > 0
        base = self._build_active_surface(card_to_draw, flash=flash)

        self._draw_active_ground_shadow(surface, visual.current_center()[0], visual.current_center()[1])

        transformed = pygame.transform.rotozoom(base, visual.current_angle(), 1.0)
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
        draw_text(surface, "Scroll ou setas", FONT_SMALL, TEXT, x, y)

        y += block_gap
        draw_text(surface, "Comandos:", FONT, WHITE, x, y)
        y += line_gap
        draw_text(surface, "SPACE = atacar", FONT_SMALL, TEXT, x, y)
        y += line_gap
        draw_text(surface, "Setas = navegar", FONT_SMALL, TEXT, x, y)

        surface.set_clip(old_clip)

    def _draw_hand_arrows(self, surface):
        show_left = self.hand_scroll_x > 0
        show_right = self.hand_scroll_x < self._max_hand_scroll()

        if show_left:
            pygame.draw.rect(surface, PANEL_DARK, self.left_arrow_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, self.left_arrow_rect, 1, border_radius=8)
            draw_text(surface, "<", FONT_MED, WHITE, self.left_arrow_rect.centerx, self.left_arrow_rect.centery - 2, center=True)

        if show_right:
            pygame.draw.rect(surface, PANEL_DARK, self.right_arrow_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, self.right_arrow_rect, 1, border_radius=8)
            draw_text(surface, ">", FONT_MED, WHITE, self.right_arrow_rect.centerx, self.right_arrow_rect.centery - 2, center=True)

    def _draw_hand_cards(self, surface):
        old_clip = surface.get_clip()
        surface.set_clip(self.hand_view_rect)

        self._layout_hand_cards()
        dragging_sprite = None

        for i, sprite in enumerate(self.card_sprites):
            if sprite.dragging and i == self.selected_index:
                dragging_sprite = sprite
                continue

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

        surface.set_clip(old_clip)

        if dragging_sprite is not None:
            self._card_visual.draw(
                surface,
                dragging_sprite.x,
                dragging_sprite.y,
                dragging_sprite.data,
                zoom=self.zoom,
                selected=True,
                pulse_time=dragging_sprite.scale_pulse_time
            )

    def draw(self, surface):
        surface.fill(TABLE_GREEN)
        draw_text(surface, f"Batalha - {self.mode_name}", FONT_BIG, WHITE, WIDTH // 2, 30, center=True)

        draw_panel(surface, pygame.Rect(120, 70, 1040, 120), color=TABLE_GREEN_2)
        draw_text(surface, "Oponente", FONT_MED, WHITE, 150, 90)
        draw_text(surface, f"Premios: {self.logic.opponent_prizes_taken}/6", FONT, WHITE, 150, 125)
        draw_text(surface, f"Deck: {len(self.logic.opponent_deck)}", FONT, WHITE, 150, 150)

        draw_panel(surface, self.center_battle_rect, color=TABLE_GREEN_3)
        self._draw_active_with_anim(surface, self.logic.opponent_active, "Pokemon Ativo do Oponente", self.opponent_visual)
        self._draw_active_with_anim(surface, self.logic.player_active, "Seu Pokemon Ativo", self.player_visual)

        draw_panel(surface, self.hand_panel_rect, color=TABLE_GREEN_2)
        draw_text(surface, "Sua mao", FONT_MED, WHITE, 95, 560)
        self._draw_hand_cards(surface)
        self._draw_hand_arrows(surface)

        draw_panel(surface, self.right_panel_rect, color=PANEL_DARK)
        self._draw_right_panel_content(surface, self.right_panel_rect)
        self._draw_zoom_controls(surface)

        self.back_btn.draw(surface)
        self.end_turn_btn.draw(surface)