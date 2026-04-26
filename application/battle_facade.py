import random
from dataclasses import dataclass
from game.core.modelos.jogador.Jogador import Jogador
from game.core.cartas.factories.CartaFactory import CartaFactory


@dataclass(slots=True)
class BattleActionResult:
    ok: bool
    message: str = ""
    target: str | None = None
    ko: bool = False
    winner: str | None = None
    reason: str | None = None


class BattleFacade:
    def __init__(self, player_nickname: str, deck_name: str = "pikachu"):
        self.jogador = Jogador(nickname=player_nickname)
        self.oponente = Jogador(nickname="Oponente")

        self.turno_atual = "player"
        self.turn_time_limit = 30
        self.turn_timer = self.turn_time_limit
        self.max_turnos_inativo = 2

        self.vencedor = None
        self.motivo_vitoria = None

        self.log = []

        self._montar_decks(deck_name)
        self._setup_inicial()

    def _montar_decks(self, deck_name: str):
        self.jogador.deck = self._criar_deck(deck_name)
        self.oponente.deck = self._criar_deck("charizard")

        random.shuffle(self.jogador.deck)
        random.shuffle(self.oponente.deck)

    def _criar_deck(self, deck_name: str):
        if deck_name == "charizard":
            return [
                CartaFactory.criar_pokemon("pz001", "Charizard EX", "Pokemon agressivo de fogo", 330, ("ataque_base",)),
                CartaFactory.criar_pokemon("pz002", "Charmander", "Pokemon basico", 70, ("ataque_fraco",)),
                CartaFactory.criar_item_cura("it001", "Potion", "Cura 30"),
                CartaFactory.criar_item_buff_dano("it002", "Power Band", "Aumenta dano"),
                CartaFactory.criar_apoiador_cura("ap001", "Nurse", "Cura pokemon"),
                CartaFactory.criar_apoiador_reducao_dano("ap002", "Shield Coach", "Reduz dano"),
                CartaFactory.criar_apoiador_bloqueio_premio("ap003", "Judge Wall", "Bloqueia premio"),
            ]
        else:
            return [
                CartaFactory.criar_pokemon("pk001", "Pikachu EX", "Pokemon eletrico rapido", 220, ("ataque_base",)),
                CartaFactory.criar_pokemon("pk002", "Raichu", "Pokemon evoluido", 150, ("ataque_fraco",)),
                CartaFactory.criar_item_cura("it003", "Potion", "Cura 30"),
                CartaFactory.criar_item_buff_dano("it004", "Power Band", "Aumenta dano"),
                CartaFactory.criar_apoiador_cura("ap004", "Medic", "Cura pokemon"),
                CartaFactory.criar_apoiador_reducao_dano("ap005", "Defender", "Reduz dano"),
                CartaFactory.criar_apoiador_bloqueio_premio("ap006", "Stop Prize", "Bloqueia premio"),
            ]

    def _setup_inicial(self):
        for _ in range(5):
            self.comprar_carta(self.jogador)
            self.comprar_carta(self.oponente)

        self.jogador.pokemon_ativo = self._retirar_primeiro_pokemon_da_mao(self.jogador)
        self.oponente.pokemon_ativo = self._retirar_primeiro_pokemon_da_mao(self.oponente)

        if self.jogador.pokemon_ativo is None:
            self._definir_vencedor("opponent", "Jogador sem pokemon inicial")
        elif self.oponente.pokemon_ativo is None:
            self._definir_vencedor("player", "Oponente sem pokemon inicial")

    def _retirar_primeiro_pokemon_da_mao(self, jogador: Jogador):
        for carta in jogador.mao:
            if carta.__class__.__name__ == "CartaPokemon":
                jogador.mao.remove(carta)
                return carta
        return None

    def comprar_carta(self, jogador: Jogador):
        if len(jogador.deck) == 0:
            if jogador == self.jogador:
                self._definir_vencedor("opponent", "Deckout do jogador")
            else:
                self._definir_vencedor("player", "Deckout do oponente")
            return None

        carta = jogador.deck.pop(0)
        jogador.mao.append(carta)
        return carta

    def nome_carta(self, carta):
        return getattr(carta, "nome", carta.__class__.__name__)

    def descricao_carta(self, carta):
        return getattr(carta, "descricao", "")

    def hp_carta(self, carta):
        return getattr(carta, "hp", 0)

    def tipo_carta(self, carta):
        nome_classe = carta.__class__.__name__.lower()
        if "pokemon" in nome_classe:
            return "pokemon"
        if "apoiador" in nome_classe:
            return "apoiador"
        if "item" in nome_classe:
            return "item"
        return "carta"

    def dano_base_pokemon(self, carta):
        return getattr(carta, "dano", 60)

    def usar_carta_da_mao(self, index: int) -> BattleActionResult:
        if self.turno_atual != "player":
            return BattleActionResult(False, "Nao e o turno do jogador")

        if index < 0 or index >= len(self.jogador.mao):
            return BattleActionResult(False, "Indice invalido")

        carta = self.jogador.mao.pop(index)
        nome_classe = carta.__class__.__name__

        if "Cura" in nome_classe and self.jogador.pokemon_ativo:
            hp_atual = getattr(self.jogador.pokemon_ativo, "hp", 0)
            setattr(self.jogador.pokemon_ativo, "hp", hp_atual + 30)
            self.log.append(f"{self.nome_carta(carta)} curou o pokemon ativo.")
            self._registrar_acao()
            return BattleActionResult(True, f"{self.nome_carta(carta)} usada")

        if "BuffDano" in nome_classe and self.jogador.pokemon_ativo:
            dano_atual = getattr(self.jogador.pokemon_ativo, "dano", 60)
            setattr(self.jogador.pokemon_ativo, "dano", dano_atual + 20)
            self.log.append(f"{self.nome_carta(carta)} aumentou o dano.")
            self._registrar_acao()
            return BattleActionResult(True, f"{self.nome_carta(carta)} usada")

        if "BloqueioPremio" in nome_classe:
            self.jogador.bloqueia_premio_do_oponente_no_proximo_nocaute = True
            self.log.append(f"{self.nome_carta(carta)} ativou bloqueio de premio.")
            self._registrar_acao()
            return BattleActionResult(True, f"{self.nome_carta(carta)} usada")

        if "ReducaoDano" in nome_classe:
            self.jogador.modificador_premio_extra_ativo = True
            self.log.append(f"{self.nome_carta(carta)} ativou protecao.")
            self._registrar_acao()
            return BattleActionResult(True, f"{self.nome_carta(carta)} usada")

        self.jogador.mao.insert(index, carta)
        return BattleActionResult(False, "Essa carta nao pode ser usada agora")

    def atacar(self) -> BattleActionResult:
        if self.turno_atual != "player":
            return BattleActionResult(False, "Nao e o turno do jogador")

        if self.jogador.pokemon_ativo is None or self.oponente.pokemon_ativo is None:
            return BattleActionResult(False, "Pokemon ativo ausente")

        dano = getattr(self.jogador.pokemon_ativo, "dano", 60)
        hp_oponente = getattr(self.oponente.pokemon_ativo, "hp", 0)
        novo_hp = hp_oponente - dano
        setattr(self.oponente.pokemon_ativo, "hp", novo_hp)

        ko = novo_hp <= 0
        if ko:
            self._processar_nocaute(atacante=self.jogador, defensor=self.oponente, lado_vencedor="player")

        self._registrar_acao()
        self.encerrar_turno()

        return BattleActionResult(
            True,
            f"Ataque causou {dano} de dano",
            target="opponent_active",
            ko=ko,
            winner=self.vencedor,
            reason=self.motivo_vitoria
        )

    def turno_ia(self) -> BattleActionResult | None:
        if self.turno_atual != "opponent" or self.vencedor:
            return None

        if self.oponente.pokemon_ativo is None or self.jogador.pokemon_ativo is None:
            return None

        dano = getattr(self.oponente.pokemon_ativo, "dano", 50)
        hp_jogador = getattr(self.jogador.pokemon_ativo, "hp", 0)
        novo_hp = hp_jogador - dano
        setattr(self.jogador.pokemon_ativo, "hp", novo_hp)

        ko = novo_hp <= 0
        if ko:
            self._processar_nocaute(atacante=self.oponente, defensor=self.jogador, lado_vencedor="opponent")

        self.encerrar_turno()

        return BattleActionResult(
            True,
            f"Oponente causou {dano} de dano",
            target="player_active",
            ko=ko,
            winner=self.vencedor,
            reason=self.motivo_vitoria
        )

    def _processar_nocaute(self, atacante: Jogador, defensor: Jogador, lado_vencedor: str):
        bloquear_premio = defensor.bloqueia_premio_do_oponente_no_proximo_nocaute

        if not bloquear_premio:
            atacante.premios_restantes -= 1
        else:
            defensor.bloqueia_premio_do_oponente_no_proximo_nocaute = False

        defensor.pokemon_ativo = self._retirar_primeiro_pokemon_da_mao(defensor)

        if atacante.premios_restantes <= 0:
            self._definir_vencedor(lado_vencedor, "Coletou todos os premios")
            return

        if defensor.pokemon_ativo is None:
            self._definir_vencedor(lado_vencedor, "Pokemon ativo derrotado sem reserva")
            return

    def atualizar_tempo(self, dt: float):
        if self.vencedor:
            return

        self.turn_timer -= dt
        if self.turn_timer <= 0:
            if self.turno_atual == "player":
                self.jogador.turnos_inativo_seguidos += 1
                if self.jogador.turnos_inativo_seguidos >= self.max_turnos_inativo:
                    self._definir_vencedor("opponent", "Derrota por inatividade")
                    return
            else:
                self.oponente.turnos_inativo_seguidos += 1
                if self.oponente.turnos_inativo_seguidos >= self.max_turnos_inativo:
                    self._definir_vencedor("player", "Vitoria por inatividade do oponente")
                    return

            self.encerrar_turno()

    def _registrar_acao(self):
        if self.turno_atual == "player":
            self.jogador.turnos_inativo_seguidos = 0
        else:
            self.oponente.turnos_inativo_seguidos = 0
        self.turn_timer = self.turn_time_limit

    def encerrar_turno(self):
        self.turn_timer = self.turn_time_limit
        self.turno_atual = "opponent" if self.turno_atual == "player" else "player"

        if self.turno_atual == "player":
            self.comprar_carta(self.jogador)
        else:
            self.comprar_carta(self.oponente)

    def _definir_vencedor(self, vencedor: str, motivo: str):
        self.vencedor = vencedor
        self.motivo_vitoria = motivo

    def get_view_state(self):
        return {
            "turno_atual": self.turno_atual,
            "turn_timer": self.turn_timer,
            "vencedor": self.vencedor,
            "motivo_vitoria": self.motivo_vitoria,
            "player": {
                "nickname": self.jogador.nickname,
                "premios_restantes": self.jogador.premios_restantes,
                "deck_count": len(self.jogador.deck),
                "inactive_turns": self.jogador.turnos_inativo_seguidos,
                "pokemon_ativo": self._card_to_view(self.jogador.pokemon_ativo),
                "mao": [self._card_to_view(c) for c in self.jogador.mao],
            },
            "opponent": {
                "nickname": self.oponente.nickname,
                "premios_restantes": self.oponente.premios_restantes,
                "deck_count": len(self.oponente.deck),
                "inactive_turns": self.oponente.turnos_inativo_seguidos,
                "pokemon_ativo": self._card_to_view(self.oponente.pokemon_ativo),
                "mao_count": len(self.oponente.mao),
            }
        }

    def _card_to_view(self, carta):
        if carta is None:
            return None

        return {
            "nome": self.nome_carta(carta),
            "descricao": self.descricao_carta(carta),
            "tipo": self.tipo_carta(carta),
            "hp": getattr(carta, "hp", 0),
            "max_hp": getattr(carta, "hp", 0),
            "dano": getattr(carta, "dano", 60 if self.tipo_carta(carta) == "pokemon" else 0),
            "classe": carta.__class__.__name__,
        }