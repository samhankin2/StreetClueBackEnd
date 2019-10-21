class Game:
    """Stores all the relvevant info for a single game to be played"""

    def __init__(self, pin):
        self.pin = pin
        self.arrayOfPlayers = []
        self.scores = {}
        self.round = 0
        self.playerCount = 0
        # self.answerCount = 0

    def addPlayer(self, player):
        self.arrayOfPlayers.append(player)
        self.scores[player] = 0

    def incRound(self):
        self.round += 1
        if(round == 5):
            return self.pin

    def calcPlayerCount(self):
        self.playerCount = len(self.arrayOfPlayers)

    def updateScores(self, player, score):
        self.scores[player] += score
