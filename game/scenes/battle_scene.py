import math
import pygame
from .base_scene import Scene
from .result_scene import ResultScene
from settings import *
from render.ui.ui import Button, draw_panel, draw_text
from game.battle_logic import BattleLogic

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

        self.angle = 0
        self.scale = 1.0

        self.shake_time = 0
        self.shake_strength = 0
        self.shake_offset_x = 0

        self.falling = False
        self.fall_speed = 0
        self.fall_rotation_speed = 0
        self.dead = False

        self.use_pulse_time = 0

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def contains_point(self, pos, zoom=1.0):
        return self.rect().collidepoint(pos)

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

    def trigger_shake(self, duration=0.35, strength=10):
        self.shake_time = duration
        self.shake_strength = strength

    def trigger_use_pulse(self):
        self.use_pulse_time = 0.25

    def trigger_fall(self, direction=1):
        self.falling = True
        self.fall_speed = 0
        self.fall_rotation_speed = 380 * direction

    def update(self, dt):
        if self.use_pulse_time > 0:
            self.use_pulse_time -= dt
            t = max(0, self.use_pulse_time)
            self.scale = 1.0 + math.sin((0.25 - t) * 22) * 0.18
        else:
            self.scale += (1.0 - self.scale) * min(1, dt * 10)

        if self.shake_time > 0:
            self.shake_time -= dt
            freq = 50
            self.shake_offset_x = math.sin(pygame.time.get_ticks() * 0.05 * freq) * self.shake_strength
        else:
            self.shake_offset_x = 0

        if self.falling:
            self.fall_speed += 900 * dt
            self.y += self.fall_speed * dt
            self.angle += self.fall_rotation_speed * dt

            if self.y > HEIGHT + 250:
                self.dead = True

class ActivePokemonVisual:
    def __init__(self, side):
        self.side = side
        self.x = 240 if side == "opponent" else 720
        self.y = 250
        self.angle = 0
        self.scale = 1.0
        self.shake_time = 0
        self.shake_strength = 0
        self.shake_offset_x = 0
        self.falling = False
        self.fall_speed = 0
        self.fall_rotation_speed = 0
        self.drop_y = 0
        self.use_scale_time = 0

    def trigger_shake(self, duration=0.35, strength=10):
        self.shake_time = duration
        self.shake_strength = strength

    def trigger_use_scale(self):
        self.use_scale_time = 0.22

    def trigger_fall(self, direction=1):
        self.falling = True
        self.fall_speed = 0
        self.fall_rotation_speed = 420 * direction

    def update(self, dt):
        if self.use_scale_time > 0:
            self.use_scale_time -= dt
            t = max(0, self.use_scale_time)
            self.scale = 1.0 + math.sin((0.22 - t) * 24) * 0.12
        else:
            self.scale += (1.0 - self.scale) * min(1, dt * 10)

        if self.shake_time > 0:
            self.shake_time -= dt
            self.shake_offset_x = math.sin(pygame.time.get_ticks() * 0.06 * 45) * self.shake_strength
        else:
            self.shake_offset_x = 0

        if self.falling:
            self.fall_speed += 1100 * dt
            self.drop_y += self.fall_speed * dt
            self.angle += self.fall_rotation_speed * dt

class BattleScene(Scene):
    def __init__(self, game, mode_name):
        super().__init__(game)
        self.mode_name = mode_name
        selected_deck = getattr(self.game, "selected_deck", "Deck Pikachu EX")
        self.logic = BattleLogic(selected_deck)

        self.back_btn = Button((20, 20, 140, 46), "Render-se", self.surrender, bg=RED, hover=(170, 50, 50))
        self.end_turn_btn = Button((1040, 640, 190, 50), "Encerrar turno", self.end_turn)

        self.card_sprites = []
        self.selected_index = None
        self.zoom = 1.0
        self.min_zoom = 1.0
        self.max_zoom = 1.25
        self.opponent_delay = 0.8

        self.player_active_visual = ActivePokemonVisual("player")
        self.opponent_active_visual = ActivePokemonVisual("opponent")

        self.rebuild_hand_positions()

    def rebuild_hand_positions(self):
        self.card_sprites = []
        start_x = 180
        gap = 145
        y = 560

        for i, card in enumerate(self.logic.player_hand):
            sprite = CardSprite(card, start_x + i * gap, y)
            self.card_sprites.append(sprite)

    def surrender(self):
        self.game.change_scene(ResultScene(self.game, "Derrota", "Voce se rendeu"))

    def end_turn(self):
        if self.logic.current_turn == "player":
            self.logic.register_action()
            self.logic.end_turn()
            self.rebuild_hand_positions()

    def handle_card_click(self, mouse_pos):
        for i in range(len(self.card_sprites) - 1, -1, -1):
            sprite = self.card_sprites[i]
            if sprite.contains_point(mouse_pos):
                self.selected_index = i
                sprite.selected = True
                sprite.start_drag(mouse_pos)
                self.logic.register_action()
                return

    def use_selected_card_if_dropped_on_active(self):
        if self.selected_index is None:
            return False

        sprite = self.card_sprites[self.selected_index]
        target_rect = pygame.Rect(720, 250, 160, 210)

        if target_rect.colliderect(sprite.rect()):
            sprite.trigger_use_pulse()
            self.player_active_visual.trigger_use_scale()
            ok, _, _ = self.logic.use_card_from_hand(self.selected_index)

            if ok:
                self.rebuild_hand_positions()

            self.selected_index = None
            return ok

        return False

    def handle_attack_result(self, result):
        if not result or not result.get("ok"):
            return

        if result.get("target") == "opponent_active":
            self.opponent_active_visual.trigger_shake()
            if result.get("ko"):
                self.opponent_active_visual.trigger_fall(direction=1)

        elif result.get("target") == "player_active":
            self.player_active_visual.trigger_shake()
            if result.get("ko"):
                self.player_active_visual.trigger_fall(direction=-1)

    def handle_event(self, event):
        self.back_btn.handle_event(event)
        self.end_turn_btn.handle_event(event)

        if self.logic.winner:
            return

        if self.logic.current_turn == "player":
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
                    used = self.use_selected_card_if_dropped_on_active()
                    if not used:
                        self.card_sprites[self.selected_index].reset_position()
                    self.selected_index = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    result = self.logic.player_attack()
                    if result.get("ok"):
                        self.logic.register_action()
                    self.handle_attack_result(result)

    def update(self, dt):
        if self.logic.winner:
            title = "Vitoria" if self.logic.winner == "player" else "Derrota"
            self.game.change_scene(ResultScene(self.game, title, self.logic.win_reason))
            return

        self.logic.update_timer(dt)

        for sprite in self.card_sprites:
            sprite.update(dt)

        self.player_active_visual.update(dt)
        self.opponent_active_visual.update(dt)

        if self.logic.winner:
            return

        if self.logic.current_turn == "opponent":
            self.opponent_delay -= dt
            if self.opponent_delay <= 0:
                result = self.logic.opponent_turn_ai()
                self.handle_attack_result(result)
                self.opponent_delay = 0.8
                self.rebuild_hand_positions()

    def build_card_surface(self, card, selected=False):
        surf = pygame.Surface((CARD_W, CARD_H), pygame.SRCALPHA)
        color = (250, 250, 250) if not selected else (255, 240, 180)
        pygame.draw.rect(surf, color, (0, 0, CARD_W, CARD_H), border_radius=12)
        pygame.draw.rect(surf, ACCENT_2, (0, 0, CARD_W, CARD_H), 3, border_radius=12)

        draw_text(surf, card["name"], FONT_SMALL, BLACK, 10, 12)
        draw_text(surf, card["type"].upper(), FONT_SMALL, GRAY, 10, 38)

        if card["type"] == "pokemon":
            draw_text(surf, f"HP {card['hp']}", FONT_SMALL, BLACK, 10, 64)
            draw_text(surf, f"ATK {card['damage']}", FONT_SMALL, BLACK, 10, 88)
        else:
            row_y = 64
            if card["heal"] > 0:
                draw_text(surf, f"Cura {card['heal']}", FONT_SMALL, BLACK, 10, row_y)
                row_y += 24
            if card["damage"] > 0:
                draw_text(surf, f"+Dano {card['damage']}", FONT_SMALL, BLACK, 10, row_y)
                row_y += 24
            if card["draw"] > 0:
                draw_text(surf, f"Compra {card['draw']}", FONT_SMALL, BLACK, 10, row_y)
                row_y += 24
            if card["prize_bonus"] > 0:
                draw_text(surf, "+Premio", FONT_SMALL, BLACK, 10, row_y)
                row_y += 24
            if card["shield"] > 0:
                draw_text(surf, f"Escudo {card['shield']}", FONT_SMALL, BLACK, 10, row_y)

        pygame.draw.rect(surf, (220, 220, 235), (10, CARD_H - 50, CARD_W - 20, 35), border_radius=8)
        return surf

    def draw_transformed_surface(self, surface, base_surface, center_x, center_y, angle, scale):
        transformed = pygame.transform.rotozoom(base_surface, angle, scale)
        rect = transformed.get_rect(center=(center_x, center_y))
        surface.blit(transformed, rect)

    def build_active_surface(self, active, label):
        w, h = 160, 210
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, (250, 250, 250), (0, 0, w, h), border_radius=14)
        pygame.draw.rect(surf, ACCENT_2, (0, 0, w, h), 3, border_radius=14)

        draw_text(surf, active["name"], FONT_MED, BLACK, 12, 15)
        draw_text(surf, f"HP: {active['hp']}/{active['max_hp']}", FONT_SMALL, BLACK, 12, 60)
        draw_text(surf, f"ATK: {active['damage']}", FONT_SMALL, BLACK, 12, 90)

        hp_ratio = max(0, active["hp"] / active["max_hp"])
        pygame.draw.rect(surf, GRAY, (12, 130, 130, 16), border_radius=6)
        pygame.draw.rect(surf, GREEN if hp_ratio > 0.4 else RED, (12, 130, int(130 * hp_ratio), 16), border_radius=6)
        return surf

    def draw(self, surface):
        surface.fill(TABLE_GREEN)
        draw_text(surface, f"Batalha - {self.mode_name}", FONT_BIG, WHITE, WIDTH // 2, 30, center=True)

        draw_panel(surface, pygame.Rect(120, 70, 1040, 120), color=TABLE_GREEN_2)
        draw_text(surface, "Oponente", FONT_MED, WHITE, 150, 90)
        draw_text(surface, f"Premios: {self.logic.opponent_prizes_taken}/6", FONT, WHITE, 150, 125)
        draw_text(surface, f"Deck: {len(self.logic.opponent_deck)}", FONT, WHITE, 150, 150)

        draw_panel(surface, pygame.Rect(180, 215, 920, 250), color=TABLE_GREEN_3)

        if self.logic.opponent_active:
            draw_text(surface, "Pokemon Ativo do Oponente", FONT, WHITE, 240, 220)
            base = self.build_active_surface(self.logic.opponent_active, "Oponente")
            center_x = 240 + 80 + self.opponent_active_visual.shake_offset_x
            center_y = 250 + 105 + self.opponent_active_visual.drop_y
            self.draw_transformed_surface(
                surface, base, center_x, center_y,
                self.opponent_active_visual.angle,
                self.opponent_active_visual.scale
            )

        if self.logic.player_active:
            draw_text(surface, "Seu Pokemon Ativo", FONT, WHITE, 720, 220)
            base = self.build_active_surface(self.logic.player_active, "Jogador")
            center_x = 720 + 80 + self.player_active_visual.shake_offset_x
            center_y = 250 + 105 + self.player_active_visual.drop_y
            self.draw_transformed_surface(
                surface, base, center_x, center_y,
                self.player_active_visual.angle,
                self.player_active_visual.scale
            )

        draw_panel(surface, pygame.Rect(70, 520, 930, 170), color=TABLE_GREEN_2)
        draw_text(surface, "Sua mao", FONT_MED, WHITE, 100, 540)

        for i, sprite in enumerate(self.card_sprites):
            selected = (i == self.selected_index)
            base = self.build_card_surface(sprite.data, selected=selected)
            center_x = sprite.x + CARD_W // 2 + sprite.shake_offset_x
            center_y = sprite.y + CARD_H // 2
            final_scale = sprite.scale * self.zoom
            self.draw_transformed_surface(surface, base, center_x, center_y, sprite.angle, final_scale)

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
        draw_text(surface, "Arraste carta", FONT_SMALL, TEXT, 1060, 565)
        draw_text(surface, "SPACE = atacar", FONT_SMALL, TEXT, 1060, 590)
        draw_text(surface, "Scroll = zoom", FONT_SMALL, TEXT, 1060, 615)

        self.back_btn.draw(surface)
        self.end_turn_btn.draw(surface)