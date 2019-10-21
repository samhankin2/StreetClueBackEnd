class Player:
    """Player class to contain all player's data"""
    # TODO getters and setters

    def __init__(self, name):
        self.name = name
        self.score = 0
        # TODO color

    def addScore(self, score):
        self.score += score
