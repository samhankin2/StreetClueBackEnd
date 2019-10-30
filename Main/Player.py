class Player:
    """Player class to contain all player's data"""
    # TODO getters and setters

    def __init__(self, name):
        self.name = name
        self.score = 0
        self.lat = 0
        self.long = 0

    def addScore(self, score):
        self.score += score

    def addLatestLocation(self, lat, long):
        self.lat = lat
        self.long = long
