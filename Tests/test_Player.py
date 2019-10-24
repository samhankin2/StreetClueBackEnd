from Main.Player import Player
 
def test_new_player():
    """
    GIVEN a Player model
    WHEN a new Player is created
    THEN check the name, score, lat and long are defined correctly
    """
    new_player = Player('Sam')
    assert new_player.name == 'Sam'
    assert new_player.score == 0
    assert new_player.lat == 0
    assert new_player.long == 0

def test_addScore():
    """
    GIVEN a Player model
    WHEN a Player's score is updated
    THEN check the score has been updated
    """
    new_player = Player('Sam')
    new_player.addScore(300)
    assert new_player.score == 300

def test_addLatestLocation():
    """
    GIVEN a Player model
    WHEN a Player's location coordinates are updated
    THEN check the score has been updated
    """
    new_player = Player('Sam')
    new_player.addLatestLocation('40.7376767', '-73.9918385')
    assert new_player.lat == '40.7376767'
    assert new_player.long == '-73.9918385'
