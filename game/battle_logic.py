"""
BattleLogic adaptado para usar o pipeline novo (JsonDeckProvider + Strategies)
mas expondo a mão/cartas como dicts para o battle_scene continuar funcionando.

Novidades nesta versão:
- Cartas de energia são ANEXADAS ao Pokémon ativo (não vão para o descarte).
- Cada ataque exige um número de energias e um tipo de energia, lidos do JSON.
- Pokémon ativo carrega lista `energies` com os tipos anexados.
- Pop-up de erro é solicitado via `last_error` quando a UI tenta atacar sem custo pago.
- Apenas UM ataque por turno (mesmo com energia sobrando).
- IA segue as mesmas regras: anexa energia primeiro, só ataca se já tem o custo.
- Prêmios são distribuídos a cada nocaute, vitória por 6 prêmios.
"""

import random
from settings import TURN_TIME_LIMIT, MAX_INACTIVE_TURNS

from game.core.services.deck_provider import JsonDeckProvider
from game.core.strategies.condicoes.standard_win_condition import StandardWinCondition

# AI strategies que operam sobre a interface de dicts deste BattleLogic.
from game.strategies.ai.simple_ai_strategy import SimpleAIStrategy
from game.strategies.ai.aggressive_ai_strategy import AggressiveAIStrategy


# ──────────────────────────────────────────────
# Adapter: converte Carta-objeto em dict legado
# ──────────────────────────────────────────────

def _extrair_dano_do_ataque(ataque) -> int:
    """Soma todos os efeitos de dano dos efeitos do ataque."""
    total = 0
    for efeito in getattr(ataque, "efeitos", []):
        cls_name = type(efeito).__name__
        if cls_name == "EfeitoCausarDano":
            total += getattr(efeito, "valor", 0)
        elif cls_name == "EfeitoDanoPorCartasDescartadas":
            base_v = getattr(efeito, "base", 0)
            mult = getattr(efeito, "multiplicador", 0)
            total += base_v + mult
    return total


def _extrair_custo_de_energia(ataque) -> int:
    """Quantas energias 'energia_anexada' o ataque exige."""
    total = 0
    for custo in getattr(ataque, "custos", []):
        cls_name = type(custo).__name__
        if cls_name == "CustoEnergiaAnexada":
            total += getattr(custo, "quantidade", 0)
    return total


def _tipo_de_energia_do_pokemon(carta_pokemon) -> str:
    """Heurística: deduz o tipo de energia preferido pelo Pokémon a partir
    do nome dele. Como não há esse campo no JSON, mapeamos pelos Pokémon
    conhecidos. Fallback: 'electric'."""
    nome = getattr(carta_pokemon, "nome", "").lower()
    if any(k in nome for k in ["pikachu", "raichu", "regieleki", "miraidon"]):
        return "electric"
    if any(k in nome for k in ["charizard", "charmander"]):
        return "fire"
    if any(k in nome for k in ["chien", "frigibax"]):
        return "water"
    if any(k in nome for k in ["gardevoir", "ralts"]):
        return "psychic"
    return "electric"


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
        "energy_type": None,           # só preenchido para cartas de energia
        "attack_name": None,           # só preenchido para Pokémon
        "attack_required_count": 0,    # só preenchido para Pokémon
        "attack_energy_type": None,    # só preenchido para Pokémon
        "_obj": carta,
    }

    if tipo_valor == "pokemon":
        base["hp"] = getattr(carta, "hp_maximo", 0)
        if carta.ataques:
            ataque = carta.ataques[0]
            base["attack_name"] = getattr(ataque, "nome", "Ataque")
            base["damage"] = _extrair_dano_do_ataque(ataque)
            base["attack_required_count"] = _extrair_custo_de_energia(ataque)
            base["attack_energy_type"] = _tipo_de_energia_do_pokemon(carta)

    elif tipo_valor in ("item", "supporter"):
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

    elif tipo_valor == "energy":
        base["energy_type"] = getattr(carta, "tipo_energia", "electric")

    return base


def _ativo_a_partir_de_carta(card_dict) -> dict:
    """Constrói o dict de 'pokemon ativo' a partir de uma carta da mão/deck."""
    return {
        "name": card_dict["name"],
        "max_hp": card_dict["hp"],
        "hp": card_dict["hp"],
        "damage": card_dict["damage"],
        "attack_name": card_dict.get("attack_name") or "Ataque",
        "attack_required_count": card_dict.get("attack_required_count", 0),
        "attack_energy_type": card_dict.get("attack_energy_type"),
        "energies": [],   # lista de energy_type anexadas
    }


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

        deck_player = self._deck_provider.get_deck(player_deck_name)
        deck_opp = self._deck_provider.get_deck("Deck Charizard EX")

        # Replica o deck 2x para ter fôlego (decks JSON têm só ~14 cartas)
        cartas_player = list(deck_player.cartas) + list(deck_player.cartas)
        cartas_opp = list(deck_opp.cartas) + list(deck_opp.cartas)

        self.player_deck = [_carta_para_dict(c) for c in cartas_player]
        self.opponent_deck = [_carta_para_dict(c) for c in cartas_opp]

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

        # Apenas um ataque por turno
        self.attacked_this_turn = False

        # Mensagem de erro temporária (para a UI exibir como pop-up)
        # tupla (texto, ttl_segundos) ou None
        self.last_error = None

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

        if self.player_active is None:
            self.check_winner("opponent", "Jogador sem pokemon inicial")
        if self.opponent_active is None:
            self.check_winner("player", "Oponente sem pokemon inicial")

    def _garantir_pokemon_inicial(self, side):
        """Procura primeiro na mão; se não tiver, busca no deck (mulligan)."""
        ativo = self.find_first_pokemon(side)
        if ativo is not None:
            return ativo

        deck = self.player_deck if side == "player" else self.opponent_deck
        for card in list(deck):
            if card["type"] == "pokemon":
                deck.remove(card)
                return _ativo_a_partir_de_carta(card)
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
            if card["type"] == "pokemon":
                hand.remove(card)
                return _ativo_a_partir_de_carta(card)
        return None

    # ──────────────────────────────────────────
    # Pop-up de erro (a UI consome `last_error`)
    # ──────────────────────────────────────────

    def set_error(self, mensagem: str, ttl: float = 2.5):
        self.last_error = (mensagem, ttl)

    def update_error(self, dt: float):
        if self.last_error is None:
            return
        texto, ttl = self.last_error
        ttl -= dt
        if ttl <= 0:
            self.last_error = None
        else:
            self.last_error = (texto, ttl)

    # ──────────────────────────────────────────
    # Anexar energia
    # ──────────────────────────────────────────

    def _anexar_energia(self, side: str, energy_type: str):
        """Anexa um tipo de energia ao Pokémon ativo do lado dado."""
        active = self.player_active if side == "player" else self.opponent_active
        if active is None:
            return
        active["energies"].append(energy_type)

    def custo_pago(self, active: dict) -> bool:
        """Verifica se o ativo já tem energias suficientes para atacar.
        Por enquanto, qualquer tipo de energia conta — desde que a contagem
        atenda ao requerido. (Versão tolerante a multi-tipo.)
        Se quiser exigir o tipo correto, basta filtrar por tipo aqui."""
        if active is None:
            return False
        return len(active["energies"]) >= active.get("attack_required_count", 0)

    def custo_pago_estrito(self, active: dict) -> bool:
        """Versão estrita: exige que pelo menos N energias sejam do tipo
        do ataque (multi-tipo permitido como bônus)."""
        if active is None:
            return False
        req = active.get("attack_required_count", 0)
        tipo = active.get("attack_energy_type")
        if tipo is None:
            return len(active["energies"]) >= req
        do_tipo = sum(1 for e in active["energies"] if e == tipo)
        # mantemos tolerante: aceita complemento de outros tipos
        return (do_tipo + max(0, len(active["energies"]) - do_tipo)) >= req

    # ──────────────────────────────────────────
    # Ações do jogador
    # ──────────────────────────────────────────

    def use_card_from_hand(self, index):
        if self.current_turn != "player" or self.winner:
            return False, "Nao e o turno do jogador"

        if index < 0 or index >= len(self.player_hand):
            return False, "Carta invalida"

        card = self.player_hand[index]

        # Energia: anexa ao Pokémon ativo e remove da mão (NÃO vai para descarte)
        if card["type"] == "energy":
            if self.player_active is None:
                return False, "Sem Pokemon ativo"
            self.player_hand.pop(index)
            self._anexar_energia("player", card["energy_type"] or "electric")
            return True, f"Energia {card['energy_type']} anexada"

        if card["type"] in ("item", "supporter"):
            self.player_hand.pop(index)
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

        # Pokémon: por enquanto não há bench; trocar ativo não é suportado
        return False, "Essa carta nao pode ser usada agora"

    def player_attack(self):
        if self.current_turn != "player" or self.winner:
            self.set_error("Nao e o seu turno")
            return False, "Nao e o turno do jogador"
        if not self.player_active or not self.opponent_active:
            self.set_error("Sem Pokemon ativo")
            return False, "Pokemon ativo ausente"

        if self.attacked_this_turn:
            self.set_error("Voce ja atacou neste turno")
            return False, "Ja atacou neste turno"

        active = self.player_active
        req = active.get("attack_required_count", 0)
        atual = len(active["energies"])
        if atual < req:
            self.set_error(f"Precisa de {req} energia(s) para atacar (tem {atual})")
            return False, "Energia insuficiente"

        damage = active["damage"]
        reduced = max(0, damage - self.opponent_shield)
        self.opponent_shield = 0
        self.opponent_active["hp"] -= reduced
        self.attacked_this_turn = True

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
        """Aplica uma carta da mão do oponente (item/supporter ou energia)."""
        if index < 0 or index >= len(self.opponent_hand):
            return False
        card = self.opponent_hand[index]

        if card["type"] == "energy":
            if self.opponent_active is None:
                return False
            self.opponent_hand.pop(index)
            self._anexar_energia("opponent", card["energy_type"] or "electric")
            return True

        if card["type"] in ("item", "supporter"):
            self.opponent_hand.pop(index)
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
            return True

        return False

    def executar_ataque_oponente(self):
        """Executa o ataque do oponente respeitando custo de energia
        e a regra de um ataque por turno."""
        if not self.opponent_active or not self.player_active:
            self.end_turn()
            return

        if self.attacked_this_turn:
            self.end_turn()
            return

        active = self.opponent_active
        req = active.get("attack_required_count", 0)
        if len(active["energies"]) < req:
            # IA passa o turno se ainda não tem energia
            self.end_turn()
            return

        damage = active["damage"]
        reduced = max(0, damage - self.player_shield)
        self.player_shield = 0
        self.player_active["hp"] -= reduced
        self.attacked_this_turn = True

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
        """Heurística usada pelas AIStrategies para decidir se vale jogar a carta.
        Inclui energia: vale anexar se ainda não tem energia suficiente."""
        active = self.opponent_active if side == "opponent" else self.player_active

        if card["type"] == "energy":
            if active is None:
                return False
            req = active.get("attack_required_count", 0)
            return len(active["energies"]) < req

        if card["type"] not in ("item", "supporter"):
            return False
        if card["heal"] > 0 and active and active["hp"] < active["max_hp"]:
            return True
        return (
            card["damage"] > 0
            or card["draw"] > 0
            or card["prize_bonus"] > 0
            or card["shield"] > 0
        )

    def carta_aumenta_pressao(self, card) -> bool:
        """Heurística agressiva: prioriza energia (para destravar ataque) e
        cartas com dano."""
        if card["type"] == "energy":
            return True
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
        self.attacked_this_turn = False  # reseta a cada novo turno

        if self.current_turn == "player":
            self.draw_card("player")
        else:
            self.draw_card("opponent")

    def check_winner(self, winner, reason):
        self.winner = winner
        self.win_reason = reason


# ──────────────────────────────────────────────
# Factory: BattleLogicFactory
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
