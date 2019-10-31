from Main.Game import Game
from Main.Player import Player
import os
from flask import Flask
from flask import request, Response, jsonify, render_template
import pusher
from random import randrange, randint
import random
import json
from flask_mysqldb import MySQL
app = Flask(__name__)
# ------------------------------------------
# Just DB things...

is_prod = os.environ.get('IS_HEROKU', None)

if is_prod:
    os.environ.get('mysql_host', None)
    app.config['MYSQL_HOST'] = os.environ.get('mysql_host', None)
    app.config['MYSQL_USER'] = os.environ.get("mysql_user", None)
    app.config['MYSQL_PASSWORD'] = os.environ.get("mysql_password", None)
    app.config['MYSQL_DB'] = os.environ.get("mysql_db", None)

else:
    from Main.mysqlconfig import config
    app.config['MYSQL_HOST'] = config["mysql_host"]
    app.config['MYSQL_USER'] = config["mysql_user"]
    app.config['MYSQL_PASSWORD'] = config["mysql_password"]
    app.config['MYSQL_DB'] = config["mysql_db"]
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        details = request.form
        latitude = details['lat']
        longitude = details['lon']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO coordinates(latitude, longitude) VALUES (%s, %s)", (latitude, longitude))
        mysql.connection.commit()
        cur.close()
        return 'success'
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Coordinates")
        data = cur.fetchall()
        cur.close()
        return jsonify(data)
    return render_template('locations.html')


# TODO IF YOU GO BACK IT WILL DELETE THE GAME
# TODO If you go back from waiting room removes you from the list
# TODO sort of the request types from post to patch etc (maybe)
# TODO make amount of rounds customisable
# TODO handle multiple pins:
    # send to the server the guessed locations
    # store that in an array
    # send back at map result
    # push back any further additions


channels_client = pusher.Pusher(
    app_id='890224',
    key='0c067d9d3a75d2722d94',
    secret='b67d9f6cf332e080ce36',
    cluster='mt1',
    ssl=True
)

locations = [[-37.2236053, 145.929006],
             [-42.7111515, 146.8972924],
             [51.5024273, -0.139319],
             [-44.5667837, 170.198597],
             [-38.6770894, 176.07472470]]

takenPins = []

games = {}


@app.route("/remove_player", methods=['POST'])
def remove_player():
    body = request.json
    pin = body["pin"]
    name = body["name"]

    game = games[pin]

    count = 0
    for person in game.arrayOfPlayers:
        if person.name == name:
            del game.arrayOfPlayers[count]
            game.generatePlayerNamesArray()
        count += 1

    channels_client.trigger(str(pin), 'playerLeave', {
                            'message': name + " Has left", "name": name})

    return "asdasd", 204


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

    if not pin in games:
        return handleNotPinInGames(pin), 404
    print("test2")
    del games[pin]
    takenPins.remove(pin)
    return "worked", 204


@app.route('/create_game', methods=['GET'])
def create_game():

    if len(takenPins) == 10000:
        return Response("{'msg': 'No Available Pins'}", status=400, mimetype='application/json')

    pin = generatePin()
    while pin in takenPins:
        pin = generatePin()

    takenPins.append(pin)
    print(takenPins)

    locations = generateLocations(5)

    newGame = Game(pin, locations, 4)

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

    # locations = generateLocations(5)
    newGame = Game("9999", locations, 4)
    games["9999"] = newGame
    newPlayer = Player("test")
    newPlayer2 = Player("hello")
    games["9999"].addPlayer(newPlayer)
    games["9999"].addPlayer(newPlayer2)


    takenPins.append("9999")

    # # print(games["9999"].arrayOfPlayers)

    # # channels_client.trigger("test", 'endGame', {
    # #     'message': "asafs"})

    # return "hi!"

    return " hi "


@app.route('/add_player', methods=['POST'])
def add_player():

    body = request.json
    playername = body["name"]
    pin = body["pin"]

    if not pin in games:
        print(games)
        return handleNotPinInGames(pin), 404

    games[pin].generatePlayerNamesArray()

    if games[pin].started == True:
        response = {"msg": pin + " has already started"}
        json = jsonify(response)
        return json, 400

    if playername in games[pin].arrayOfPlayerNames and len(games[pin].arrayOfPlayers) > 0:
        response = {"msg": playername + " is already taken"}
        json = jsonify(response)
        return json, 400

    newPlayer = Player(playername)
    games[pin].addPlayer(newPlayer)
    channels_client.trigger(str(pin), 'playerJoin', {
                            'message': playername + " Has Joined", "name": playername})

    response = {"msg": "Added "+playername+" Successfully",
                "locations": games[pin].randomLocations[0]}
    json = jsonify(response)
    return json, 201


@app.route('/start_game', methods=['POST'])
def start_game():
    body = request.json

    pin = body["pin"]

    if not pin in games:
        return handleNotPinInGames(pin), 404

    games[pin].startGame()
    channels_client.trigger(str(pin), 'startGame', {
                            'message': 'game ' + pin + ' has started'})
    response = {"msg": "started game sucessfully", "pin": pin}
    json = jsonify(response)
    return json


@app.route('/update_score', methods=['POST'])
def update_score():


    print(takenPins)
    print("here")
    print(games)

    # TODO need to sort out the pusher here.. deffo tomoz job`
    body = request.json
    playername = body["name"]
    pin = body["pin"]
    score = body["score"]

    if not pin in games:
        return handleNotPinInGames(pin), 404

    game = games[pin]
    game.updateScores(playername, score)

    if game.isEndRound() and game.isEndGame():
        channels_client.trigger(str(pin), 'endGame', {
            'message': game.scores})
        triggerEndRoundPusher(pin)
        print("test1")
        del games[pin]
        takenPins.remove(pin)
        return endGameResponseHandler(game, "End of Game"), 200

    if game.isEndRound() and not game.isEndGame():

        triggerEndRoundPusher(pin)
        print("end of round and not end of game")
        response = answerSubmittedHandler(game, "End of Round")
        game.answerCount = 0
        game.nextRound()
        return response, 200

    if not game.isEndRound() and game.isEndGame():
        print("not end of round and end of game")
        return endGameResponseHandler(game, "Go To Leaderboard screen next"), 200

    if not game.isEndRound() and not game.isEndGame():
        print("not end of game and not end of round")
        return answerSubmittedHandler(game, "Answer Submitted"), 200


@app.route('/get_players', methods=['POST'])
def get_players():
    body = request.json
    pin = body["pin"]

    if not pin in games:
        return handleNotPinInGames(pin), 404
    game = games[pin]
    game.generatePlayerNamesArray()

    response = {
        "players": game.arrayOfPlayerNames}
    json = jsonify(response)
    return json, 200


def generatePin():
    pin = ''.join(str(randint(0, 9)) for _ in range(4))
    return pin


def generateLocations(numberOfRounds):
    randoms = random.sample(range(5), numberOfRounds)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Coordinates")
    data = cur.fetchall()
    cur.close()
    jsonData = jsonify(data)
    locations = []

    print(randoms)
    print(data[1])
    for i in randoms:
        print(i)
        content = [(data[i])[1], (data[i])[2]]
        locations.append(content)
        content = []
    print(locations)
    return locations



def triggerEndRoundPusher(pin):
    channels_client.trigger(str(pin), 'endRound', {
        'message': "test"})


def endGameResponseHandler(game, msg):
    response = {"msg": msg,
                "scores": game.scores, "nextRound": "none", "locations": [0, 0], "endGame": True}
    json = jsonify(response)
    return json


def answerSubmittedHandler(game, msg):
    response = {"msg": msg,
                "scores": game.scores, "nextRound": game.round+1, "locations": game.randomLocations[game.round+1], "endGame": False}
    json = jsonify(response)
    return json


def handleNotPinInGames(pin):
    response = {"msg": pin + " Doesnt Exists"}
    json = jsonify(response)
    return json

def findGame(pin):
    return 0

if __name__ == '__main__':
    app.run()