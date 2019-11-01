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
        body = request.json
        pin = body["pin"]
        name = body["name"]

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO players(latitude, longitude) VALUES (%s, %s)", (latitude, longitude))
        mysql.connection.commit()
        cur.close()
        return 'success'
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        sql = 'SELECT players.name, players.total_score FROM players INNER JOIN games ON players.pin = games.pin WHERE games.pin = %s'
        cur.execute(sql, [3090])
        data = cur.fetchall()
        print(data)
        score = {}

        for row in data:

            score[row[0]] = row[1]

        print(score)

        return jsonify(score)
    return render_template('locations.html')


channels_client = pusher.Pusher(
    app_id='890224',
    key='0c067d9d3a75d2722d94',
    secret='b67d9f6cf332e080ce36',
    cluster='mt1',
    ssl=True
)


@app.route("/remove_player", methods=['POST'])
def remove_player():
    body = request.json
    pin = body["pin"]
    name = body["name"]
    player_id = body["player_id"]

    cur = mysql.connection.cursor()
    sql = "DELETE FROM players WHERE player_id = %s"
    cur.execute(sql, [player_id])
    mysql.connection.commit()
    cur.close()

    channels_client.trigger(str(pin), 'playerLeave', {
                            'message': name + " Has left", "name": name})

    return "asdasd", 204


@app.route("/next_round", methods=['POST'])
def next_round():

    handlePinError = handleNotPinInGames(123123)

    if handlePinError[0] == True:
        return handlePinError[1]


    body = request.json
    pin = body["pin"]

    channels_client.trigger(str(pin), 'nextRound', {
        'message': pin + "next round started"})

    return "worked"


# # this shouldnt be used
# @app.route("/delete_game", methods=['POST'])
# def delete_game():

#     body = request.json
#     pin = body["pin"]

#     if not pin in games:
#         return handleNotPinInGames(pin), 404
#     print("test2")
#     del games[pin]
#     takenPins.remove(pin)
#     return "worked", 204


@app.route('/create_game', methods=['GET', 'POST'])
def create_game():

    # if len(takenPins) == 10000:
    #     return Response("{'msg': 'No Available Pins'}", status=400, mimetype='application/json')

    pin = generatePin()

    # TODO fix this
    # while pin in takenPins:
    #     pin = generatePin()
    location_id = randint(1, 20)
    sql = "INSERT INTO games (pin, total_rounds, current_round, player_count, locations_id, started, answer_count) VALUES (%s, 3,0,0,%s,0,0)"
    cur = mysql.connection.cursor()

    cur.execute(sql, [pin, location_id])
    mysql.connection.commit()

    response = {"msg": "Created game sucessfully", "pin": pin}
    json = jsonify(response)
    return json, 201


# @app.route('/test', methods=['GET', 'POST'])
# def debug():
#     # print(games)
#     # for i in games:
#     #     print(games[i].pin)
#     #     print(games[i].arrayOfPlayers)
#     #     print(games[i].scores)

#     # # print(availablePins)
#     # # print(takenPins)

#     print(takenPins)
#     print(games)

#     # locations = generateLocations(5)
#     newGame = Game("9999", locations, 4)
#     games["9999"] = newGame
#     newPlayer = Player("test")
#     newPlayer2 = Player("hello")
#     games["9999"].addPlayer(newPlayer)
#     games["9999"].addPlayer(newPlayer2)

#     takenPins.append("9999")

#     # # print(games["9999"].arrayOfPlayers)

#     # # channels_client.trigger("test", 'endGame', {
#     # #     'message': "asafs"})

#     # return "hi!"

#     return " hi "


@app.route('/add_player', methods=['POST'])
def add_player():

    body = request.json
    playername = body["name"]
    pin = body["pin"]
    handlePinError = handleNotPinInGames(pin)

    print(handlePinError[0])

    if handlePinError[0] == True:
        return handlePinError[1]

    cur = mysql.connection.cursor()
    sql = "SELECT started, locations_id FROM games WHERE pin = %s"
    cur.execute(sql, [pin])
    data = cur.fetchone()
    if data[0] == 1:
        response = {"msg": pin + " has already started"}
        json = jsonify(response)
        return json, 400

    params = (playername, str(pin))
    sql = "INSERT INTO players (name, current_score, total_score, pin) VALUES(%s, 0, 0,%s)"
    cur.execute(sql, params)

    sql = "UPDATE games SET player_count = player_count+1 WHERE pin = %s "
    cur.execute(sql, [pin])
    mysql.connection.commit()

    sql = "SELECT LAST_INSERT_ID();"
    cur.execute(sql)
    id = cur.fetchone()
    print(id[0])

    sql = "SELECT * FROM locations where locations_id = %s"
    location_id = data[1]

    cur.execute(sql, [location_id])
    data = cur.fetchone()

    location = data[1].split(",")

    location[0] = float(location[0])
    location[1] = float(location[1])

    print(location)

    cur.close()

    # if playername in games[pin].arrayOfPlayerNames and len(games[pin].arrayOfPlayers) > 0:
    #     response = {"msg": playername + " is already taken"}
    #     json = jsonify(response)
    #     return json, 400

    channels_client.trigger(str(pin), 'playerJoin', {
                            'message': playername + " Has Joined", "name": playername})

    response = {"msg": "Added "+playername+" Successfully",
                "locations": location, "player_id": id[0]}
    json = jsonify(response)
    return json, 201


@app.route('/start_game', methods=['POST'])
def start_game():
    body = request.json

    pin = body["pin"]

    handlePinError = handleNotPinInGames(pin)

    if handlePinError[0] == True:
        return handlePinError[1]

    cur = mysql.connection.cursor()
    sql = "UPDATE games SET started = TRUE WHERE pin = %s"
    cur.execute(sql, [pin])
    mysql.connection.commit()
    cur.close()

    channels_client.trigger(str(pin), 'startGame', {
                            'message': 'game ' + pin + ' has started'})
    response = {"msg": "started game sucessfully", "pin": pin}
    json = jsonify(response)
    return json


@app.route('/update_score', methods=['POST'])
def update_score():

    body = request.json
    playername = body["name"]
    pin = body["pin"]
    score = body["score"]
    player_id = body["player_id"]

    handlePinError = handleNotPinInGames(pin)

    if handlePinError[0] == True:
        return handlePinError[1]

    cur = mysql.connection.cursor()

    sql = "UPDATE games SET answer_count=answer_count+1 WHERE pin = %s"
    cur.execute(sql, [pin])

    sql = "UPDATE players SET total_score=total_score+%s, current_score=%s WHERE player_id=%s"
    cur.execute(sql, [score, score, player_id])

    mysql.connection.commit()

    sql = "SELECT player_count, answer_count, current_round FROM games WHERE pin = %s"
    cur.execute(sql, [pin])
    data = cur.fetchone()

    playerCount = data[0]
    answerCount = data[1]
    currentRound = data[2]

    endRound = False
    endGame = False

    print(playerCount)
    print(answerCount)

    if playerCount == answerCount:
        endRound = True

    if currentRound == 2:
        endGame = True

    if endRound and endGame:

        sql = 'SELECT players.name, players.total_score FROM players INNER JOIN games ON players.pin = games.pin WHERE games.pin = %s'
        cur.execute(sql, [pin])
        data = cur.fetchall()

        score = {}

        for row in data:
            score[row[0]] = row[1]

        # ON DELETE CASCADE IN THE SCHEMA
        sql = "DELETE FROM games WHERE pin = %s"
        cur.execute(sql, [pin])
        mysql.connection.commit()

        channels_client.trigger(str(pin), 'endGame', {
            'message': score})
        triggerEndRoundPusher(pin)

        response = {"msg": "End of Game",
                    "scores": score, "nextRound": "3", "locations": [0, 0], "endGame": True}

        return jsonify(response), 200

    if endRound and not endGame:
        triggerEndRoundPusher(pin)
        print("end of round and not end of game")

        sql = "UPDATE games SET answer_count=0, current_round=current_round+1 WHERE pin=%s"
        cur.execute(sql, [pin])

        mysql.connection.commit()

        sql = 'SELECT players.name, players.total_score, games.current_round, games.locations_id FROM players INNER JOIN games ON players.pin = games.pin WHERE games.pin = %s'
        cur.execute(sql, [pin])
        data = cur.fetchall()

        score = {}

        for row in data:
            score[row[0]] = row[1]
        print(data)
        location_id = data[0][3]
        currentRound = data[0][2]

        sql = "SELECT location" + \
            str(currentRound)+" FROM locations WHERE locations_id = %s"

        cur.execute(sql, [location_id])
        data = cur.fetchone()

        print(data)

        location = data[0].split(",")

        location[0] = float(location[0])
        location[1] = float(location[1])

        response = {"msg": "End of Round",
                    "scores": score, "nextRound": currentRound, "locations": location, "endGame": False}

        return jsonify(response), 200

    if not endRound and endGame:
        print("not end of game but is end game")

        sql = 'SELECT players.name, players.total_score, games.current_round, games.locations_id FROM players INNER JOIN games ON players.pin = games.pin WHERE games.pin = %s'
        cur.execute(sql, [pin])
        data = cur.fetchall()

        score = {}

        for row in data:
            score[row[0]] = row[1]

        response = {"msg": "Go to leaderboard screen",
                    "scores": score, "nextRound": 3, "locations": [0, 0], "endGame": True}
        json = jsonify(response)
        return json

    if not endRound and not endGame:
        print("not end of game and not end of round")

        sql = 'SELECT players.name, players.total_score, games.current_round, games.locations_id FROM players INNER JOIN games ON players.pin = games.pin WHERE games.pin = %s'
        cur.execute(sql, [pin])
        data = cur.fetchall()

        score = {}

        for row in data:
            score[row[0]] = row[1]
        print(data)
        location_id = data[0][3]
        currentRound = data[0][2]

        sql = "SELECT location" + \
            str(currentRound+1)+" FROM locations WHERE locations_id = %s"

        cur.execute(sql, [location_id])
        data = cur.fetchone()

        print(data)

        location = data[0].split(",")

        location[0] = float(location[0])
        location[1] = float(location[1])

        response = {"msg": "Answer Submitted",
                    "scores": score, "nextRound": currentRound, "locations": location, "endGame": False}

        json = jsonify(response)
        return json

    return "Error", 400


@app.route('/get_players', methods=['POST'])
def get_players():
    body = request.json
    pin = body["pin"]

    handlePinError = handleNotPinInGames(pin)

    if handlePinError[0] == True:
        return handlePinError[1]

    cur = mysql.connection.cursor()

    sql = "SELECT name FROM players WHERE pin = %s "
    cur.execute(sql, [pin])

    data = cur.fetchall()
    print(data)
    arrayOfPlayers = []

    for rows in data:
        arrayOfPlayers.append(rows[0])

    response = {
        "players": arrayOfPlayers}
    json = jsonify(response)
    return json, 200


def generatePin():
    pin = ''.join(str(randint(0, 9)) for _ in range(4))
    return pin


# def generateLocations(numberOfRounds):
#     randoms = random.sample(range(5), numberOfRounds)
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM Coordinates")
#     data = cur.fetchall()
#     cur.close()
#     jsonData = jsonify(data)
#     locations = []

#     print(randoms)
#     print(data[1])
#     for i in randoms:
#         print(i)
#         content = [(data[i])[1], (data[i])[2]]
#         locations.append(content)
#         content = []
#     print(locations)
#     return locations


def triggerEndRoundPusher(pin):
    channels_client.trigger(str(pin), 'endRound', {
        'message': "test"})


# def endGameResponseHandler(game, msg):
#     response = {"msg": msg,
#                 "scores": game.scores, "nextRound": "none", "locations": [0, 0], "endGame": True}
#     json = jsonify(response)
#     return json


# def answerSubmittedHandler(game, msg):
#     response = {"msg": msg,
#                 "scores": game.scores, "nextRound": game.round+1, "locations": game.randomLocations[game.round+1], "endGame": False}
#     json = jsonify(response)
#     return json


def handleNotPinInGames(pin):

    cur = mysql.connection.cursor()
    sql = "SELECT COUNT(1) FROM games WHERE pin = %s"
    cur.execute(sql, [str(pin)])

    data = cur.fetchone()

    if data[0] == 0:
        response = {"msg": "Pin Doesnt Exists"}
        json = jsonify(response)
        return [True, json]

    else:
        return [False]


# def findGame(pin):
#     return 0
if __name__ == '__main__':
    app.run()
