from flask import Flask
from flask import request
import pusher
from random import randrange

from Player import Player
from Game import Game

app = Flask(__name__)


channels_client = pusher.Pusher(
    app_id='882302',
    key='e997856aae5ff49795fd',
    secret='ed6a44d2b024c45766d1',
    cluster='eu',
    ssl=True
)

availablePins = [1425, 8888, 7412, 5520, 1033, 5793]
takenPins = []
games = []

# TODO Error handle if all pins are taken
@app.route('/create_game', methods=['GET'])
def create_game():
    pin = getPin()
    print(pin)

    newGame = Game(pin)

    games.append(newGame)

    # TODO return the pin

    return 'Hello, World!'


@app.route('/test', methods=['GET'])
def add_plater():
    for game in games:
        print(game.pin)
        print(game.arrayOfPlayers)

    print(availablePins)
    print(takenPins)

    return "hi!"


@app.route('/add_player', methods=['POST'])
def add_player():
    body = request.json
    playername = body["name"]
    pin = body["pin"]

    newPlayer = Player(playername)

    for game in games:
        if(game.pin == pin):
            game.addPlayer(newPlayer)

    return "hi!"


def getPin():
    index = randrange(len(availablePins)-1)
    newPin = availablePins[index]
    del availablePins[index]
    takenPins.append(newPin)
    return newPin
