class SimpleRegistry:
    def __init__(self, nome: str):
        self.nome = nome
        self._builders = {}

    def registrar(self, chave: str, builder):
        if chave in self._builders:
            raise ValueError(f"{self.nome} '{chave}' já registrado.")
        self._builders[chave] = builder

    def criar(self, data: dict):
        chave = data["type"]
        builder = self._builders.get(chave)

        if builder is None:
            raise ValueError(f"{self.nome} desconhecido: {chave}")

        return builder(data)

    def possui(self, chave: str) -> bool:
        return chave in self._builders

    def listar_chaves(self) -> list[str]:
        return list(self._builders.keys())