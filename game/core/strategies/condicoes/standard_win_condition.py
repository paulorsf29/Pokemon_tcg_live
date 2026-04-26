from .win_condition_strategy import WinConditionStrategy


class StandardWinCondition(WinConditionStrategy):
    def checar(self, logic):
        if logic.player_prizes_taken >= 6:
            return "player", "Coletou 6 premios"

        if logic.opponent_prizes_taken >= 6:
            return "opponent", "Oponente coletou 6 premios"

        return None, None