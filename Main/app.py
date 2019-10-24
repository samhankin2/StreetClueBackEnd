from flask import Flask
from flask import request, Response, jsonify
import pusher
from random import randrange, randint
import random

from Player import Player
from Game import Game

app = Flask(__name__)

# TODO Make sure the names are unique
# TODO IF YOU GO BACK IT WILL DELETE THE GAME
# TODO If you go back from waiting room removes you from the list
# TODO LOCATIONS NEEDS A REAL LOOK AT WHEN THE DATABASE HAS FINSIHED BE CAREFUL
# TODO End of game response needs to be fixed


channels_client = pusher.Pusher(
    app_id='882302',
    key='e997856aae5ff49795fd',
    secret='ed6a44d2b024c45766d1',
    cluster='eu',
    ssl=True
)

locations = [[-37.2236053, 145.929006],
             [-42.7111515, 146.8972924],
             [51.5024273, -0.139319],
             [-44.5667837, 170.198597],
             [-38.6770894, 176.07472470]]

takenPins = []
# locations = ["-37.2236053,145.929006",
#              "-42.7111515,146.8972924",
#              "41.2779077,146.036284",
#              "-44.5667837,170.198597",
#              "-38.6770894,176.07472470"]
games = {}


@app.route("/next_round", methods=['POST'])
def next_round():

    body = request.json
    pin = body["pin"]

    channels_client.trigger(str(pin), 'nextRound', {
        'message': pin + "next round started"})

    return "worked"


# this shouldnt be used
@app.route("/delete_game", methods=['POST'])
def delete_game():
    body = request.json
    pin = body["pin"]
    if pin in games:
        del games[pin]
        takenPins.remove(pin)
        return "worked", 204
    else:
        response = {"msg": pin + " Doesnt Exists"}
        json = jsonify(response)
        return json, 404


@app.route('/create_game', methods=['GET'])
def create_game():

    if len(takenPins) == 10000:
        return Response("{'msg': 'No Available Pins'}", status=400, mimetype='application/json')

    pin = generatePin()
    while pin in takenPins:
        pin = generatePin()

    takenPins.append(pin)

    newGame = Game(pin, locations, 5)

    games[pin] = newGame
    response = {"msg": "Created game sucessfully", "pin": pin}
    json = jsonify(response)
    return json, 201


@app.route('/test', methods=['GET', 'POST'])
def debug():
    # print(games)
    # for i in games:
    #     print(games[i].pin)
    #     print(games[i].arrayOfPlayers)
    #     print(games[i].scores)

    # # print(availablePins)
    # # print(takenPins)

    print(takenPins)
    print(games)

    newGame = Game("9999", locations, 3)
    games["9999"] = newGame
    newPlayer = Player("test")
    newPlayer2 = Player("hello")
    games["9999"].addPlayer(newPlayer)
    games["9999"].addPlayer(newPlayer2)

    games["9999"].startGame()

    takenPins.append("9999")

    return "hi!"

    return " hi "


@app.route('/add_player', methods=['POST'])
def add_player():
    body = request.json
    playername = body["name"]
    pin = body["pin"]

    newPlayer = Player(playername)
    if pin in games:
        if games[pin].started == False:
            games[pin].addPlayer(newPlayer)
            channels_client.trigger(str(pin), 'playerJoin', {
                                    'message': playername + " Has Joined", "name": playername})

            response = {"msg": "Added "+playername+" Successfully",
                        "locations": games[pin].randomLocations[0]}
            json = jsonify(response)
            return json, 201
        else:
            response = {"msg": pin + " has already started"}
            json = jsonify(response)
            return json, 400

    else:
        response = {"msg": pin + " Doesnt Exists"}
        json = jsonify(response)
        return json, 404


@app.route('/start_game', methods=['POST'])
def start_game():
    body = request.json

    pin = body["pin"]

    if pin in games:
        games[pin].startGame()
        channels_client.trigger(str(pin), 'startGame', {
                                'message': 'game ' + pin + ' has started'})
        response = {"msg": "started game sucessfully", "pin": pin}
        json = jsonify(response)
        return json

    else:
        response = {"msg": pin + " Doesnt Exists"}
        json = jsonify(response)
        return json, 404


@app.route('/update_score', methods=['POST'])
def update_score():
    # TODO need to sort out the pusher here.. deffo tomoz job`
    body = request.json
    playername = body["name"]
    pin = body["pin"]
    score = body["score"]

    if pin in games:
        games[pin].updateScores(playername, score)
        if games[pin].playerCount == games[pin].answerCount:
            games[pin].answerCount = 0
            games[pin].nextRound()
            if games[pin].round > games[pin].totalRounds:
                channels_client.trigger(str(pin), 'endGame', {
                    'message': games[pin].scores})
                response = {"msg": "End of Game",
                            "scores": games[pin].scores}
                json = jsonify(response)
                del games[pin]
                takenPins.remove(pin)
                return json, 200

            else:
                response = {"msg": "End of Round",
                            "scores": games[pin].scores, "nextRound": games[pin].round, "locations": games[pin].randomLocations[games[pin].round]}
                json = jsonify(response)
                return json, 200
        else:
            response = {"msg": "Answer Submitted",
                        "scores": games[pin].scores, "nextRound": games[pin].round+1, "locations": games[pin].randomLocations[games[pin].round+1]}
            json = jsonify(response)
            return json, 200

    else:
        response = {"msg": pin + " Doesnt Exists"}
        json = jsonify(response)
        return json, 404


@app.route('/get_players', methods=['POST'])
def get_players():
    body = request.json
    pin = body["pin"]
    x = games[pin].scores.keys()

    print(x)
    if pin in games:
        names = []
        for player in games[pin].arrayOfPlayers:
            names.append(player.name)

        response = {
            "players": names}
        json = jsonify(response)
        return json, 200
    else:
        response = {"msg": pin + " Doesnt Exists"}
        json = jsonify(response)
        return json, 404


def generatePin():
    pin = ''.join(str(randint(0, 9)) for _ in range(4))
    return pin


# def getLocations(numberOfRounds):
#     randomLocations = []
#     indexs = random.sample(range(0, len(locations)-1), numberOfRounds)

#     for i in indexs:
#         randomLocations.append(locations[i])

#     return randomLocations


def findGame(pin):
    return 0
