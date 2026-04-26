"""
BattleLogic adaptado para usar o pipeline novo (JsonDeckProvider + Strategies)
mas expondo a mão/cartas como dicts para o battle_scene continuar funcionando.

Ponte: cartas-objeto (CartaPokemon, CartaItemGenerico, etc.) -> dicts
com as chaves esperadas pelo battle_scene (name, type, hp, damage, heal,
draw, prize_bonus, shield).
"""

import random
from settings import TURN_TIME_LIMIT, MAX_INACTIVE_TURNS

from game.core.services.deck_provider import JsonDeckProvider
from game.core.strategies.condicoes.standard_win_condition import StandardWinCondition

# AI strategies que operam sobre a interface de dicts deste BattleLogic.
# Ficam em game/strategies/ai/ (fora de core/) porque core/ assume cartas-objeto.
from game.strategies.ai.simple_ai_strategy import SimpleAIStrategy
from game.strategies.ai.aggressive_ai_strategy import AggressiveAIStrategy


# ──────────────────────────────────────────────
# Adapter: converte Carta-objeto em dict legado
# ──────────────────────────────────────────────

def _carta_para_dict(carta) -> dict:
    """Converte uma carta-objeto do core para o dict que o battle_scene espera."""
    tipo_valor = getattr(carta.tipo, "value", str(carta.tipo))
    base = {
        "name": carta.nome,
        "type": tipo_valor,
        "hp": 0,
        "damage": 0,
        "heal": 0,
        "draw": 0,
        "prize_bonus": 0,
        "shield": 0,
        "state": getattr(carta, "state", "basic"),
        "image": getattr(carta, "image", None),
        "_obj": carta,  # mantém referência caso seja útil
    }

    if tipo_valor == "pokemon":
        base["hp"] = getattr(carta, "hp_maximo", 0)
        # extrai dano do primeiro ataque (se houver)
        if carta.ataques:
            base["damage"] = _extrair_dano_do_ataque(carta.ataques[0])

    elif tipo_valor in ("item", "supporter"):
        # extrai efeitos das habilidades
        for hab in carta.habilidades:
            for efeito in getattr(hab, "efeitos", []):
                cls_name = type(efeito).__name__
                if cls_name == "EfeitoCurar":
                    base["heal"] += getattr(efeito, "valor", 0)
                elif cls_name == "EfeitoCausarDano":
                    base["damage"] += getattr(efeito, "valor", 0)
                elif cls_name == "EfeitoComprarCartas":
                    base["draw"] += getattr(efeito, "quantidade", 0)
                elif cls_name == "EfeitoPremioExtra":
                    base["prize_bonus"] += getattr(efeito, "quantidade", 0)
                elif cls_name == "EfeitoReducaoDano":
                    base["shield"] += getattr(efeito, "valor", 0)

    return base


def _extrair_dano_do_ataque(ataque) -> int:
    """Soma todos os efeitos de dano dos efeitos do ataque."""
    total = 0
    for efeito in getattr(ataque, "efeitos", []):
        cls_name = type(efeito).__name__
        if cls_name == "EfeitoCausarDano":
            total += getattr(efeito, "valor", 0)
        elif cls_name == "EfeitoDanoPorCartasDescartadas":
            # estimativa: base + multiplicador (assumindo 1 descarte mínimo)
            base_v = getattr(efeito, "base", 0)
            mult = getattr(efeito, "multiplicador", 0)
            total += base_v + mult
    return total


# ──────────────────────────────────────────────
# BattleLogic (interface legada de dicts)
# ──────────────────────────────────────────────

class BattleLogic:
    """Lógica de batalha que usa o DeckProvider novo internamente,
    mas expõe a mão/cartas como dicts para a UI."""

    def __init__(
        self,
        player_deck_name: str,
        deck_provider=None,
        ai_strategy=None,
        win_condition=None,
    ):
        self._deck_provider = deck_provider or JsonDeckProvider()
        self._ai_strategy = ai_strategy or SimpleAIStrategy()
        self._win_condition = win_condition or StandardWinCondition()

        # Carrega via novo pipeline e converte para listas de dicts
        deck_player = self._deck_provider.get_deck(player_deck_name)
        deck_opp = self._deck_provider.get_deck("Deck Charizard EX")

        self.player_deck = [_carta_para_dict(c) for c in deck_player.cartas]
        self.opponent_deck = [_carta_para_dict(c) for c in deck_opp.cartas]

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

    # ──────────────────────────────────────────
    # Setup / draws
    # ──────────────────────────────────────────

    def setup_game(self):
        for _ in range(5):
            self.draw_card("player")
            self.draw_card("opponent")

        self.player_active = self._garantir_pokemon_inicial("player")
        self.opponent_active = self._garantir_pokemon_inicial("opponent")

        # Mesmo após "mulligan", se o deck for inviável (nenhum Pokémon),
        # encerra a partida.
        if self.player_active is None:
            self.check_winner("opponent", "Jogador sem pokemon inicial")
        if self.opponent_active is None:
            self.check_winner("player", "Oponente sem pokemon inicial")

    def _garantir_pokemon_inicial(self, side):
        ativo = self.find_first_pokemon(side)
        if ativo is not None:
            return ativo

        deck = self.player_deck if side == "player" else self.opponent_deck
        for card in list(deck):
            if card["type"] == "pokemon" and card.get("state") == "basic":  # <-- adicionar state aqui
                deck.remove(card)
                return {
                    "name": card["name"],
                    "max_hp": card["hp"],
                    "hp": card["hp"],
                    "damage": card["damage"],
                    "image": card.get("image"),
                }
        return None

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
            if card["type"] == "pokemon" and card.get("state") == "basic":
                hand.remove(card)
                return {
                    "name": card["name"],
                    "max_hp": card["hp"],
                    "hp": card["hp"],
                    "damage": card["damage"],
                    "image": card.get("image"),
                }
        return None

    # ──────────────────────────────────────────
    # Ações do jogador
    # ──────────────────────────────────────────

    def use_card_from_hand(self, index):
        if self.current_turn != "player" or self.winner:
            return False, "Nao e o turno do jogador"

        if index < 0 or index >= len(self.player_hand):
            return False, "Carta invalida"

        card = self.player_hand.pop(index)

        if card["type"] in ("item", "supporter"):
            if card["heal"] > 0 and self.player_active:
                self.player_active["hp"] = min(
                    self.player_active["max_hp"],
                    self.player_active["hp"] + card["heal"],
                )
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
            return True, f"Carta {card['name']} usada"

        # carta não jogável agora — devolve para a mão
        self.player_hand.insert(index, card)
        return False, "Essa carta nao pode ser usada agora"

    def player_attack(self):
        if self.current_turn != "player" or self.winner:
            return False, "Nao e o turno do jogador"
        if not self.player_active or not self.opponent_active:
            return False, "Pokemon ativo ausente"

        damage = self.player_active["damage"]
        reduced = max(0, damage - self.opponent_shield)
        self.opponent_shield = 0
        self.opponent_active["hp"] -= reduced

        if self.opponent_active["hp"] <= 0:
            self.opponent_discard.append(self.opponent_active)
            self.opponent_active = self.find_first_pokemon("opponent")

            prizes = 1 + self.player_bonus_prize
            self.player_bonus_prize = 0
            self.player_prizes_taken += prizes

            winner, reason = self._win_condition.checar(self)
            if winner:
                self.check_winner(winner, reason)
                return True, "Vitoria por premios"

            if self.opponent_active is None:
                self.check_winner("player", "Oponente sem pokemon no campo")
                return True, "Vitoria por nocaute final"

        self.end_turn()
        return True, f"Ataque causou {reduced} de dano"

    # ──────────────────────────────────────────
    # Ações do oponente (chamadas pelas AIStrategies)
    # ──────────────────────────────────────────

    def opponent_turn_ai(self):
        """Delega para a estratégia de IA injetada."""
        self._ai_strategy.escolher_acao(self)

    def apply_opponent_card(self, index):
        card = self.opponent_hand.pop(index)

        if card["heal"] > 0 and self.opponent_active:
            self.opponent_active["hp"] = min(
                self.opponent_active["max_hp"],
                self.opponent_active["hp"] + card["heal"],
            )
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

    def executar_ataque_oponente(self):
        """Executa o ataque do oponente e gerencia consequências."""
        if not self.opponent_active or not self.player_active:
            self.end_turn()
            return

        damage = self.opponent_active["damage"]
        reduced = max(0, damage - self.player_shield)
        self.player_shield = 0
        self.player_active["hp"] -= reduced

        if self.player_active["hp"] <= 0:
            self.player_discard.append(self.player_active)
            self.player_active = self.find_first_pokemon("player")
            prizes = 1 + self.opponent_bonus_prize
            self.opponent_bonus_prize = 0
            self.opponent_prizes_taken += prizes

            winner, reason = self._win_condition.checar(self)
            if winner:
                self.check_winner(winner, reason)
                return

            if self.player_active is None:
                self.check_winner("opponent", "Jogador sem pokemon no campo")
                return

        self.end_turn()

    def carta_eh_viavel_para_ia(self, card, side) -> bool:
        """Heurística usada pelas AIStrategies para decidir se vale jogar a carta."""
        if card["type"] not in ("item", "supporter"):
            return False
        active = self.opponent_active if side == "opponent" else self.player_active
        if card["heal"] > 0 and active and active["hp"] < active["max_hp"]:
            return True
        return (
            card["damage"] > 0
            or card["draw"] > 0
            or card["prize_bonus"] > 0
            or card["shield"] > 0
        )

    def carta_aumenta_pressao(self, card) -> bool:
        """Heurística agressiva: prioriza cartas com dano."""
        return card["type"] in ("item", "supporter") and card["damage"] > 0

    # ──────────────────────────────────────────
    # Timer e fim de turno
    # ──────────────────────────────────────────

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


# ──────────────────────────────────────────────
# Factory: BattleLogicFactory (re-exportada aqui
# para compatibilidade com import antigo)
# ──────────────────────────────────────────────

class BattleLogicFactory:
    """Factory para criar instâncias de BattleLogic com estratégias configuráveis."""

    _ai_registry: dict[str, type] = {
        "simple": SimpleAIStrategy,
        "aggressive": AggressiveAIStrategy,
    }

    def __new__(cls, *args, **kwargs):
        raise TypeError("BattleLogicFactory nao pode ser instanciada.")

    @classmethod
    def registrar_ai(cls, nome: str, ai_class: type):
        cls._ai_registry[nome] = ai_class

    @classmethod
    def criar(cls, player_deck_name: str, ai_type: str = "simple",
              deck_provider=None) -> BattleLogic:
        ai_class = cls._ai_registry.get(ai_type, SimpleAIStrategy)
        return BattleLogic(
            player_deck_name=player_deck_name,
            deck_provider=deck_provider or JsonDeckProvider(),
            ai_strategy=ai_class(),
        )
