from flask import Flask
from flask import request, Response, jsonify
import pusher
from random import randrange, randint

from Player import Player
from Game import Game

app = Flask(__name__)


# TODO Use Dictionary as the {pin:GameObject}

channels_client = pusher.Pusher(
    app_id='882302',
    key='e997856aae5ff49795fd',
    secret='ed6a44d2b024c45766d1',
    cluster='eu',
    ssl=True
)


takenPins = []

games = {}


@app.route('/create_game', methods=['GET'])
def create_game():

    if len(takenPins) == 10000:
        return Response("{'msg': 'No Available Pins'}", status=400, mimetype='application/json')

    pin = generatePin()
    while pin in takenPins:
        pin = generatePin()

    takenPins.append(pin)

    newGame = Game(pin)
    games[pin] = newGame

    response = {"msg": "Created game sucessfully", "pin": pin}
    json = jsonify(response)
    return json


@app.route('/test', methods=['GET'])
def debug():
    print(games)
    for i in games:
        print(games[i].pin)
        print(games[i].arrayOfPlayers)
        print(games[i].scores)

    # print(availablePins)
    # print(takenPins)

    return "hi!"


@app.route('/add_player', methods=['POST'])
def add_player():
    body = request.json
    playername = body["name"]
    pin = body["pin"]

    newPlayer = Player(playername)
    if pin in games:
        games[pin].addPlayer(newPlayer)
        channels_client.trigger(str(pin), 'playerJoin', {
                                'message': playername + " Has Joined"})
        response = {"msg": "Added "+playername+" Successfully"}
        json = jsonify(response)
        return json, 201
    else:
        response = {"msg": pin + " Doesnt Exists"}
        json = jsonify(response)
        return json, 404

    # TODO need to sort out the responses


@app.route('/update_score', methods=['POST'])
def update_score():
    body = request.json
    playername = body["name"]
    pin = body["pin"]
    score = body["score"]

    if pin in games:
        games[pin].updateScores(playername, score)
        # TODO Pusher goes here for updating score realtime
        return "Updated"

    else:
        return "No Game Exists"


# @app.route('/next_round', methods=['POST'])
# def next_round():
#     # pin = body["pin"]
#     # for


# TODO sort out how we are negotiating the next round
# TODO all pins needs to be strings or leading 0s wont work


def generatePin():
    pin = ''.join(str(randint(0, 9)) for _ in range(4))
    return pin


def findGame(pin):
    return 0
