from Main.Game import Game
from Main.Player import Player
import os
from flask import Flask
from flask import request, Response, jsonify, render_template
import pusher
from random import randrange, randint
import random
from Main.mysqlconfig import config
import json
from flask_mysqldb import MySQL
app = Flask(__name__)
# ------------------------------------------
# Just DB things...

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


# TODO Make sure the names are unique
# TODO IF YOU GO BACK IT WILL DELETE THE GAME
# TODO If you go back from waiting room removes you from the list
# TODO LOCATIONS NEEDS A REAL LOOK AT WHEN THE DATABASE HAS FINSIHED BE CAREFUL
# TODO End of game response needs to be fixed
# TODO Test


# TODO Make sure the names are unique
# TODO If you go back from waiting room removes you from the list
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
    locations = generateLocations(3)
    newGame = Game("9999", locations, 4)
    games["9999"] = newGame
    newPlayer = Player("test")
    newPlayer2 = Player("hello")
    games["9999"].addPlayer(newPlayer)
    games["9999"].addPlayer(newPlayer2)

    games["9999"].startGame()

    takenPins.append("9999")

    channels_client.trigger("test", 'endGame', {
        'message': "asafs"})

    return "hi!"

    return " hi "


@app.route('/add_player', methods=['POST'])
def add_player():
    body = request.json
    playername = body["name"]
    pin = body["pin"]

    if pin in games:
        # if playername is in games[pin].pl
        if games[pin].started == False:
            newPlayer = Player(playername)
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
        print(games[pin].round)
        print(games[pin].totalRounds)
        games[pin].updateScores(playername, score)
        if games[pin].playerCount == games[pin].answerCount:
            games[pin].answerCount = 0
            games[pin].nextRound()
            if games[pin].round > games[pin].totalRounds:
                channels_client.trigger(str(pin), 'endGame', {
                    'message': games[pin].scores})
                channels_client.trigger(str(pin), 'endRound', {
                    'message': "test"})
                response = {"msg": "End of Game",
                            "scores": games[pin].scores, "nextRound": "none", "locations": [0, 0], "endGame": True}
                json = jsonify(response)
                print("end of game deleted")
                del games[pin]
                takenPins.remove(pin)
                return json, 200

            else:
                channels_client.trigger(str(pin), 'endRound', {
                    'message': "test"})
                response = {"msg": "End of Round",
                            "scores": games[pin].scores, "nextRound": games[pin].round, "locations": games[pin].randomLocations[games[pin].round], "endGame": False}
                json = jsonify(response)
                return json, 200

        elif games[pin].round < 4:
            response = {"msg": "Answer Submitted",
                        "scores": games[pin].scores, "nextRound": games[pin].round+1, "locations": games[pin].randomLocations[games[pin].round+1], "endGame": False}
            json = jsonify(response)
            return json, 200

        else:
            # channels_client.trigger(str(pin), 'endsRound', {
            #     'message': "test"})
            response = {"msg": "End of Game1",
                        "scores": games[pin].scores, "nextRound": "none", "locations": [0, 0], "endGame": True}
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


def generateLocations(numberOfRounds):
    randoms = random.sample(range(5), numberOfRounds)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Coordinates")
    data = cur.fetchall()
    cur.close()
    jsonData = jsonify(data)
    locations = []
    content = {}
    print(randoms)
    print(data[1])
    for i in randoms:
        print(i)
        content = [(data[i])[0], (data[i])[1]]
        locations.append(content)
        content = {}
    print(locations)
    return locations


def findGame(pin):
    return 0

if __name__ == '__main__':
    app.run()