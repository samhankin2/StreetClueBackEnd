from Game import Game
from Player import Player
import os
from flask import Flask
from flask import request, Response, jsonify, render_template
import pusher
from random import randrange, randint
import random
from flask_sqlalchemy import SQLAlchemy

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(
    os.path.join(project_dir, "locationdatabase.db"))

print(database_file)


app = Flask(__name__)

# ------------------------------------------
# Just DB things...

app.config["SQLALCHEMY_DATABASE_URI"] = database_file
db = SQLAlchemy(app)


class Locations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lat = db.Column(db.String(15), nullable=False)
    lon = db.Column(db.String(15), nullable=False)

    def __repr__(self):
        return "{},{}".format(self.lat, self.lon)


# TODO Make sure the names are unique
# TODO If you go back from waiting room removes you from the list
channels_client = pusher.Pusher(
    app_id='882302',
    key='e997856aae5ff49795fd',
    secret='ed6a44d2b024c45766d1',
    cluster='eu',
    ssl=True
)


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

    locations = generateLocations(5)
    print(locations)
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


def generateLocations(numberOfRounds):
    randoms = random.sample(range(132), numberOfRounds)
    location1 = Locations.query.filter_by(id=randoms[0]+1).one()
    location2 = Locations.query.filter_by(id=randoms[1]+1).one()
    location3 = Locations.query.filter_by(id=randoms[2]+1).one()
    location4 = Locations.query.filter_by(id=randoms[3]+1).one()
    location5 = Locations.query.filter_by(id=randoms[4]+1).one()
    locations = [[str(location1)], [str(location2)], [
        str(location3)], [str(location4)], [str(location5)]]
    print(locations)

    return locations
# def generatePlayerNameArray():


def findGame(pin):
    return 0
