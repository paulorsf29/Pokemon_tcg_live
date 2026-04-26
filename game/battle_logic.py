import random
from settings import TURN_TIME_LIMIT, MAX_INACTIVE_TURNS
from .card_data import get_deck_by_name

class BattleLogic:
    def __init__(self, player_deck_name):
        self.player_deck_name = player_deck_name
        self.player_deck = get_deck_by_name(player_deck_name)[:]
        self.opponent_deck = get_deck_by_name("Deck Charizard EX")[:]

        random.shuffle(self.player_deck)
        random.shuffle(self.opponent_deck)

        self.player_hand = []
        self.opponent_hand = []

        self.player_active = None
        self.opponent_active = None

        self.player_discard = []
        self.opponent_discard = []

        self.player_prizes_taken = 0
        self.opponent_prizes_taken = 0

        self.current_turn = "player"
        self.turn_timer = TURN_TIME_LIMIT
        self.inactive_turns = {"player": 0, "opponent": 0}

        self.player_bonus_prize = 0
        self.opponent_bonus_prize = 0

        self.player_shield = 0
        self.opponent_shield = 0

        self.winner = None
        self.win_reason = None

        self.setup_game()

    def setup_game(self):
        for _ in range(5):
            self.draw_card("player")
            self.draw_card("opponent")

        self.player_active = self.find_first_pokemon("player")
        self.opponent_active = self.find_first_pokemon("opponent")

        if self.player_active is None:
            self.check_winner("opponent", "Jogador sem pokemon inicial")
        if self.opponent_active is None:
            self.check_winner("player", "Oponente sem pokemon inicial")

    def draw_card(self, side):
        deck = self.player_deck if side == "player" else self.opponent_deck
        hand = self.player_hand if side == "player" else self.opponent_hand

        if len(deck) == 0:
            if side == "player":
                self.check_winner("opponent", "Deckout do jogador")
            else:
                self.check_winner("player", "Deckout do oponente")
            return None

        card = deck.pop(0)
        hand.append(card)
        return card

    def find_first_pokemon(self, side):
        hand = self.player_hand if side == "player" else self.opponent_hand
        for card in hand:
            if card["type"] == "pokemon":
                hand.remove(card)
                return {
                    "name": card["name"],
                    "max_hp": card["hp"],
                    "hp": card["hp"],
                    "damage": card["damage"],
                }
        return None

    def use_card_from_hand(self, index):
        if self.current_turn != "player" or self.winner:
            return False, "Nao e o turno do jogador", None

        if index < 0 or index >= len(self.player_hand):
            return False, "Carta invalida", None

        card = self.player_hand.pop(index)

        if card["type"] == "item" or card["type"] == "supporter":
            if card["heal"] > 0 and self.player_active:
                self.player_active["hp"] = min(self.player_active["max_hp"], self.player_active["hp"] + card["heal"])
            if card["draw"] > 0:
                for _ in range(card["draw"]):
                    self.draw_card("player")
            if card["prize_bonus"] > 0:
                self.player_bonus_prize += card["prize_bonus"]
            if card["shield"] > 0:
                self.player_shield += card["shield"]
            if card["damage"] > 0 and self.player_active:
                self.player_active["damage"] += card["damage"]

            self.player_discard.append(card)
            return True, f"Carta {card['name']} usada", card

        self.player_hand.insert(index, card)
        return False, "Essa carta nao pode ser usada agora", None

    def player_attack(self):
        if self.current_turn != "player" or self.winner:
            return {"ok": False, "message": "Nao e o turno do jogador"}

        if not self.player_active or not self.opponent_active:
            return {"ok": False, "message": "Pokemon ativo ausente"}

        damage = self.player_active["damage"]
        reduced = max(0, damage - self.opponent_shield)
        self.opponent_shield = 0
        self.opponent_active["hp"] -= reduced

        result = {
            "ok": True,
            "message": f"Ataque causou {reduced} de dano",
            "target": "opponent_active",
            "damage": reduced,
            "ko": False
        }

        if self.opponent_active["hp"] <= 0:
            result["ko"] = True
            self.opponent_discard.append(self.opponent_active)
            self.opponent_active = self.find_first_pokemon("opponent")

            prizes = 1 + self.player_bonus_prize
            self.player_bonus_prize = 0
            self.player_prizes_taken += prizes

            if self.player_prizes_taken >= 6:
                self.check_winner("player", "Coletou 6 premios")

            elif self.opponent_active is None:
                self.check_winner("player", "Oponente sem pokemon no campo")

        self.end_turn()
        return result

    def opponent_turn_ai(self):
        if self.current_turn != "opponent" or self.winner:
            return None

        for card in self.opponent_hand[:]:
            real_index = self.opponent_hand.index(card)
            if card["type"] in ["item", "supporter"]:
                if card["heal"] > 0 and self.opponent_active and self.opponent_active["hp"] < self.opponent_active["max_hp"]:
                    self.apply_opponent_card(real_index)
                    break
                elif card["damage"] > 0 or card["draw"] > 0 or card["prize_bonus"] > 0 or card["shield"] > 0:
                    self.apply_opponent_card(real_index)
                    break

        if self.winner:
            return None

        if self.opponent_active and self.player_active:
            damage = self.opponent_active["damage"]
            reduced = max(0, damage - self.player_shield)
            self.player_shield = 0
            self.player_active["hp"] -= reduced

            result = {
                "target": "player_active",
                "damage": reduced,
                "ko": False
            }

            if self.player_active["hp"] <= 0:
                result["ko"] = True
                self.player_discard.append(self.player_active)
                self.player_active = self.find_first_pokemon("player")
                prizes = 1 + self.opponent_bonus_prize
                self.opponent_bonus_prize = 0
                self.opponent_prizes_taken += prizes

                if self.opponent_prizes_taken >= 6:
                    self.check_winner("opponent", "Oponente coletou 6 premios")
                elif self.player_active is None:
                    self.check_winner("opponent", "Jogador sem pokemon no campo")

            self.end_turn()
            return result

        return None

    def apply_opponent_card(self, index):
        card = self.opponent_hand.pop(index)

        if card["heal"] > 0 and self.opponent_active:
            self.opponent_active["hp"] = min(self.opponent_active["max_hp"], self.opponent_active["hp"] + card["heal"])
        if card["draw"] > 0:
            for _ in range(card["draw"]):
                self.draw_card("opponent")
        if card["prize_bonus"] > 0:
            self.opponent_bonus_prize += card["prize_bonus"]
        if card["shield"] > 0:
            self.opponent_shield += card["shield"]
        if card["damage"] > 0 and self.opponent_active:
            self.opponent_active["damage"] += card["damage"]

        self.opponent_discard.append(card)

    def update_timer(self, dt):
        if self.winner:
            return

        self.turn_timer -= dt
        if self.turn_timer <= 0:
            self.inactive_turns[self.current_turn] += 1

            if self.inactive_turns[self.current_turn] >= MAX_INACTIVE_TURNS:
                if self.current_turn == "player":
                    self.check_winner("opponent", "Derrota por inatividade")
                else:
                    self.check_winner("player", "Vitoria por inatividade do oponente")
                return

            self.end_turn(forced=True)

    def register_action(self):
        self.inactive_turns[self.current_turn] = 0
        self.turn_timer = TURN_TIME_LIMIT

    def end_turn(self, forced=False):
        if self.winner:
            return

        self.turn_timer = TURN_TIME_LIMIT
        self.current_turn = "opponent" if self.current_turn == "player" else "player"

        if self.current_turn == "player":
            self.draw_card("player")
        else:
            self.draw_card("opponent")

    def check_winner(self, winner, reason):
        self.winner = winner
        self.win_reason = reason