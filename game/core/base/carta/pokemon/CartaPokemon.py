class CartaPokemon:
    def __init__(
        self,
        id_carta: str,
        nome: str,
        descricao: str,
        hp: int,
        habilidades_associadas: tuple[str, ...] = (),
        habilidades: dict[str, object] | None = None,
        dano: int = 60,
    ):
        self.id_carta = id_carta
        self.nome = nome
        self.descricao = descricao

        self.hp = hp
        self.hp_max = hp
        self.dano = dano

        self.habilidades_associadas = habilidades_associadas
        self.habilidades = habilidades or {}

    def receber_dano(self, valor: int) -> None:
        self.hp = max(0, self.hp - valor)

    def curar(self, valor: int) -> None:
        self.hp = min(self.hp_max, self.hp + valor)

    def esta_nocauteado(self) -> bool:
        return self.hp <= 0