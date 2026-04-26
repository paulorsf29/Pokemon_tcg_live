from dataclasses import dataclass, field


@dataclass
class Deck:
    nome: str
    cartas: list = field(default_factory=list)

    def comprar(self):
        if not self.cartas:
            return None
        return self.cartas.pop(0)