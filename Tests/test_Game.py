from Main.Game import Game
from Main.Player import Player

def test_new_game():
    """
    GIVEN a Game model
    WHEN a new Player is created
    THEN check the name, score, lat and long are defined correctly
    """
    new_game = Game('1234', ["-37.2236053,145.929006",
             "-42.7111515,146.8972924",
             "41.2779077,146.036284",
             "-44.5667837,170.198597",
             "-38.6770894,176.07472470"], 5)
    assert new_game.pin == '1234'
    assert new_game.arrayOfPlayers == []
    assert new_game.scores == {}
    assert new_game.round == 0
    assert new_game.totalRounds == 5
    assert new_game.playerCount == 0
    assert new_game.started == False
    assert new_game.randomLocations == ["-37.2236053,145.929006",
             "-42.7111515,146.8972924",
             "41.2779077,146.036284",
             "-44.5667837,170.198597",
             "-38.6770894,176.07472470"]
    assert new_game.answerCount == 0

def test_addPlayer():
    """
    GIVEN a Game model and Player model
    WHEN a player is added to a game
    THEN check the player is added to the arrayOfPlayers
    """
    new_player = Player('Sam')
    new_game = Game('1234', ["-37.2236053,145.929006"], 5)
    new_game.addPlayer(new_player)
    assert new_game.pin == '1234'
    assert new_game.arrayOfPlayers == [new_player]
    assert new_game.scores == {"Sam": 0}
    assert new_game.round == 0
    assert new_game.totalRounds == 5
    assert new_game.playerCount == 0
    assert new_game.started == False
    assert new_game.randomLocations == ["-37.2236053,145.929006"]
    assert new_game.answerCount == 0

def test_calcPlayerCount():
    """
    GIVEN a Game model and Player models
    WHEN a player is added to a game
    THEN check playerCount is calculated based on the items in arrayOfPlayers
    """
    new_game = Game('1234', ["-37.2236053,145.929006"], 5)
    player_one = Player('Sam')
    player_two = Player('Dan')
    player_three = Player('Mo')
    new_game.addPlayer(player_one)
    new_game.addPlayer(player_two)
    new_game.addPlayer(player_three)
    new_game.calcPlayerCount()
    assert new_game.pin == '1234'
    assert new_game.arrayOfPlayers == [player_one, player_two, player_three]
    assert new_game.scores == {"Sam": 0, "Dan": 0, "Mo": 0}
    assert new_game.round == 0
    assert new_game.totalRounds == 5
    assert new_game.playerCount == 3
    assert new_game.started == False
    assert new_game.randomLocations == ["-37.2236053,145.929006"]
    assert new_game.answerCount == 0

def test_updateScores():
    """
    GIVEN a Game model and Player models
    WHEN a score is updated
    THEN check scores are updated correctly for each player and the answer count increases
    """
    new_game = Game('1234', ["-37.2236053,145.929006"], 5)
    player_one = Player('Sam')
    player_two = Player('Dan')
    player_three = Player('Mo')
    new_game.addPlayer(player_one)
    new_game.addPlayer(player_two)
    new_game.addPlayer(player_three)
    new_game.calcPlayerCount()
    new_game.updateScores("Mo", 300)
    new_game.updateScores("Sam", 600)
    new_game.updateScores("Dan", 900)
    assert new_game.pin == '1234'
    assert new_game.arrayOfPlayers == [player_one, player_two, player_three]
    assert new_game.scores == {"Sam": 600, "Dan": 900, "Mo": 300}
    assert new_game.round == 0
    assert new_game.totalRounds == 5
    assert new_game.playerCount == 3
    assert new_game.started == False
    assert new_game.randomLocations == ["-37.2236053,145.929006"]
    assert new_game.answerCount == 3

def test_startGame():
    """
    GIVEN a Game model and Player models
    WHEN a game is started
    THEN check count of players, change the started flag to 'true' and increment the round
    """
    new_game = Game('1234', ["-37.2236053,145.929006"], 5)
    player_one = Player('Sam')
    player_two = Player('Dan')
    player_three = Player('Mo')
    new_game.addPlayer(player_one)
    new_game.addPlayer(player_two)
    new_game.addPlayer(player_three)
    new_game.startGame()
    assert new_game.pin == '1234'
    assert new_game.arrayOfPlayers == [player_one, player_two, player_three]
    assert new_game.scores == {"Sam": 0, "Dan": 0, "Mo": 0}
    assert new_game.round == 1
    assert new_game.totalRounds == 5
    assert new_game.playerCount == 3
    assert new_game.started == True
    assert new_game.randomLocations == ["-37.2236053,145.929006"]
    assert new_game.answerCount == 0