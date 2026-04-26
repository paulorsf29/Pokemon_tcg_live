import random
from dataclasses import dataclass

from settings import TURN_TIME_LIMIT, MAX_INACTIVE_TURNS
from game.core.modelos.jogador.Jogador import Jogador
from game.core.cartas.factories.CartaFactory import CartaFactory
from game.core.habilidades.EfeitoContexto import EfeitoContexto
from game.core.habilidades.services.HabilidadesService import HabilidadesService


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
        self.turn_time_limit = TURN_TIME_LIMIT
        self.turn_timer = self.turn_time_limit
        self.max_turnos_inativo = MAX_INACTIVE_TURNS

        self.vencedor = None
        self.motivo_vitoria = None
        self.habilidades = HabilidadesService.obter()

        self._montar_decks(deck_name)
        self._setup_inicial()

    def _montar_decks(self, deck_name: str):
        self.jogador.deck = self._criar_deck(deck_name)
        self.oponente.deck = self._criar_deck("charizard")
        random.shuffle(self.jogador.deck)
        random.shuffle(self.oponente.deck)

    def _criar_deck(self, deck_name: str):
        if deck_name.lower() == "charizard":
            return [
                CartaFactory.criar_pokemon("pz001", "Charizard EX", "Pokemon agressivo de fogo", 330, ("AumentarDano",), dano=90),
                CartaFactory.criar_pokemon("pz002", "Charmander", "Pokemon basico", 70, (), dano=30),
                CartaFactory.criar_item_cura("it001", "Potion", "Cura 30"),
                CartaFactory.criar_item_buff_dano("it002", "Power Band", "Aumenta dano"),
                CartaFactory.criar_apoiador_cura("ap001", "Nurse", "Cura pokemon"),
                CartaFactory.criar_apoiador_bloqueio_premio("ap002", "Judge Wall", "Bloqueia premio"),
                CartaFactory.criar_apoiador_reducao_dano("ap003", "Shield Coach", "Reduz dano"),
            ]

        return [
            CartaFactory.criar_pokemon("pk001", "Pikachu EX", "Pokemon eletrico rapido", 220, ("AumentarDano",), dano=60),
            CartaFactory.criar_pokemon("pk002", "Raichu", "Pokemon evoluido", 150, (), dano=70),
            CartaFactory.criar_item_cura("it003", "Potion", "Cura 30"),
            CartaFactory.criar_item_buff_dano("it004", "Power Band", "Aumenta dano"),
            CartaFactory.criar_apoiador_cura("ap004", "Medic", "Cura pokemon"),
            CartaFactory.criar_apoiador_bloqueio_premio("ap005", "Stop Prize", "Bloqueia premio"),
            CartaFactory.criar_apoiador_reducao_dano("ap006", "Defender", "Reduz dano"),
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
            if "CartaPokemon" in carta.__class__.__name__:
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

    def _executar_habilidade(self, nome_habilidade: str, jogador_origem=None, jogador_alvo=None, pokemon_alvo=None, carta=None, valor=0):
        habilidade = self.habilidades.get(nome_habilidade)
        if habilidade is None:
            return False

        contexto = EfeitoContexto(
            jogador_origem=jogador_origem,
            jogador_alvo=jogador_alvo,
            pokemon_alvo=pokemon_alvo,
            carta=carta,
            valor=valor,
        )
        habilidade.executar(contexto)
        return True

    def usar_carta_da_mao(self, index: int) -> BattleActionResult:
        if self.turno_atual != "player":
            return BattleActionResult(False, "Nao e o turno do jogador")

        if index < 0 or index >= len(self.jogador.mao):
            return BattleActionResult(False, "Indice invalido")

        carta = self.jogador.mao[index]
        nome_classe = carta.__class__.__name__

        ok = False

        if "ItemCura" in nome_classe or "ApoiadorCura" in nome_classe:
            ok = self._executar_habilidade(
                "CurarPokemon",
                jogador_origem=self.jogador,
                jogador_alvo=self.jogador,
                pokemon_alvo=self.jogador.pokemon_ativo,
                carta=carta,
                valor=30,
            )

        elif "ItemBuffDano" in nome_classe:
            ok = self._executar_habilidade(
                "AumentarDano",
                jogador_origem=self.jogador,
                jogador_alvo=self.jogador,
                pokemon_alvo=self.jogador.pokemon_ativo,
                carta=carta,
                valor=20,
            )

        elif "BloqueioPremio" in nome_classe:
            ok = self._executar_habilidade(
                "BloquearPremioOponente",
                jogador_origem=self.jogador,
                jogador_alvo=self.jogador,
                pokemon_alvo=self.jogador.pokemon_ativo,
                carta=carta,
                valor=0,
            )

        elif "ReducaoDano" in nome_classe:
            ok = self._executar_habilidade(
                "ReduzirDanoProximoTurno",
                jogador_origem=self.jogador,
                jogador_alvo=self.jogador,
                pokemon_alvo=self.jogador.pokemon_ativo,
                carta=carta,
                valor=0,
            )

        if not ok:
            return BattleActionResult(False, "Essa carta nao pode ser usada agora")

        self.jogador.mao.pop(index)
        self._registrar_acao()
        return BattleActionResult(True, f"{self.nome_carta(carta)} usada")

    def atacar(self) -> BattleActionResult:
        if self.turno_atual != "player":
            return BattleActionResult(False, "Nao e o turno do jogador")

        if self.jogador.pokemon_ativo is None or self.oponente.pokemon_ativo is None:
            return BattleActionResult(False, "Pokemon ativo ausente")

        dano = self.jogador.pokemon_ativo.dano

        if self.oponente.reducao_dano_proximo_turno_ativa:
            dano = max(0, dano - 20)
            self.oponente.reducao_dano_proximo_turno_ativa = False

        self.oponente.pokemon_ativo.receber_dano(dano)

        ko = self.oponente.pokemon_ativo.esta_nocauteado()
        if ko:
            self._processar_nocaute(self.jogador, self.oponente, "player")

        self._registrar_acao()
        self.encerrar_turno()

        return BattleActionResult(
            True,
            f"Ataque causou {dano} de dano",
            target="opponent_active",
            ko=ko,
            winner=self.vencedor,
            reason=self.motivo_vitoria,
        )

    def turno_ia(self) -> BattleActionResult | None:
        if self.turno_atual != "opponent" or self.vencedor:
            return None

        if self.oponente.pokemon_ativo is None or self.jogador.pokemon_ativo is None:
            return None

        dano = self.oponente.pokemon_ativo.dano

        if self.jogador.reducao_dano_proximo_turno_ativa:
            dano = max(0, dano - 20)
            self.jogador.reducao_dano_proximo_turno_ativa = False

        self.jogador.pokemon_ativo.receber_dano(dano)

        ko = self.jogador.pokemon_ativo.esta_nocauteado()
        if ko:
            self._processar_nocaute(self.oponente, self.jogador, "opponent")

        self.encerrar_turno()

        return BattleActionResult(
            True,
            f"Oponente causou {dano} de dano",
            target="player_active",
            ko=ko,
            winner=self.vencedor,
            reason=self.motivo_vitoria,
        )

    def _processar_nocaute(self, atacante: Jogador, defensor: Jogador, lado_vencedor: str):
        if not defensor.bloqueia_premio_do_oponente_no_proximo_nocaute:
            atacante.premios_restantes -= 1
            if atacante.premio_extra_ativo:
                atacante.premios_restantes -= 1
                atacante.premio_extra_ativo = False
        else:
            defensor.bloqueia_premio_do_oponente_no_proximo_nocaute = False

        defensor.pokemon_ativo = self._retirar_primeiro_pokemon_da_mao(defensor)

        if atacante.premios_restantes <= 0:
            self._definir_vencedor(lado_vencedor, "Coletou todos os premios")
            return

        if defensor.pokemon_ativo is None:
            self._definir_vencedor(lado_vencedor, "Pokemon ativo derrotado sem reserva")

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
        if self.vencedor:
            return

        self.turn_timer = self.turn_time_limit
        self.turno_atual = "opponent" if self.turno_atual == "player" else "player"

        if self.turno_atual == "player":
            self.comprar_carta(self.jogador)
        else:
            self.comprar_carta(self.oponente)

    def _definir_vencedor(self, vencedor: str, motivo: str):
        self.vencedor = vencedor
        self.motivo_vitoria = motivo

    def tipo_carta(self, carta):
        nome_classe = carta.__class__.__name__.lower()
        if "pokemon" in nome_classe:
            return "pokemon"
        if "apoiador" in nome_classe:
            return "apoiador"
        if "item" in nome_classe:
            return "item"
        return "carta"

    def nome_carta(self, carta):
        return getattr(carta, "nome", carta.__class__.__name__)

    def descricao_carta(self, carta):
        return getattr(carta, "descricao", "")

    def _card_to_view(self, carta):
        if carta is None:
            return None

        return {
            "nome": self.nome_carta(carta),
            "descricao": self.descricao_carta(carta),
            "tipo": self.tipo_carta(carta),
            "hp": getattr(carta, "hp", 0),
            "max_hp": getattr(carta, "hp_max", getattr(carta, "hp", 0)),
            "dano": getattr(carta, "dano", 0),
            "classe": carta.__class__.__name__,
        }

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
            },
        }