class Game:
    """Stores all the relvevant info for a single game to be played"""

    def __init__(self, pin, randomLocations, totalRounds):
        self.pin = pin
        self.arrayOfPlayers = []
        self.arrayOfPlayerDetails = None
        self.scores = {}
        self.round = 0
        self.totalRounds = totalRounds
        self.playerCount = 0
        self.started = False
        self.randomLocations = randomLocations
        self.answerCount = 0
        self.lastGuesses = []

    def addPlayer(self, player):
        self.arrayOfPlayers.append(player)
        self.generatePlayerDetailsArray()
        self.scores[player.name] = 0

    def calcPlayerCount(self):
        self.playerCount = len(self.arrayOfPlayers)

    def updateScores(self, name, score, latitude, longitude, colour):
        self.answerCount += 1
        self.scores[name]["totalScore"] += score
        self.scores[name]["roundScore"] = score
        self.scores[name]["currLat"] = latitude
        self.scores[name]["currLong"] = longitude
        self.scores[name]["colour"] = colour

    def startGame(self):
        self.playerCount = len(self.arrayOfPlayers)
        self.started = True
        # self.round += 1

    def nextRound(self):
        self.round += 1
        return self.round

    def isEndRound(self):
        playerCount = len(self.arrayOfPlayers)
        return self.answerCount == playerCount

    def isEndGame(self):
        return self.round == self.totalRounds

    def generatePlayerDetailsArray(self):
        names = []
        if len(self.arrayOfPlayers) == 0:
            return 0
            
        for player in self.arrayOfPlayers:
            names.append({"name": player.name, "colour": player.colour})

        self.arrayOfPlayerDetails = names
