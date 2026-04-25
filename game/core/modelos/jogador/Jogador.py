from dataclasses import dataclass, field


@dataclass(slots=True)
class Jogador:
    nickname: str
    premios_restantes: int = 6
    deck: list = field(default_factory=list)
    mao: list = field(default_factory=list)
    banco: list = field(default_factory=list)
    pokemon_ativo: object | None = None
    modificador_premio_extra_ativo: bool = False
    bloqueia_premio_do_oponente_no_proximo_nocaute: bool = False
    turnos_inativo_seguidos: int = 0