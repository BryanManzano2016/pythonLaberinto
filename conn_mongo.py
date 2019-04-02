import pymongo

myclient = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
mydb = myclient['players_laberinto']

def view_user(from_clt):

    validar = False
    repetido = False
    # Collection
    collection_mg = mydb["player"]

    # Leer los jugadores de la base de datos y validar si ya esta lo requerido
    for player in collection_mg.find():
        # user y pass iguales
        if from_clt["user_s"] == player["user"] and from_clt["pass_s"] == player["pass"]:
            validar = True
            repetido = True
        # solo user igual
        elif from_clt["user_s"] == player["user"] and not from_clt["pass_s"] == player["pass"]:
            repetido = True

    # Si no esta crea un objeto
    if not repetido:

        mydict = {"user": from_clt["user_s"], "pass": from_clt["pass_s"], "record": 0}
        # Insert dict
        x = collection_mg.insert_one(mydict)
        # Si se inserto True
        if len(str(x.inserted_id)) != 0:
            validar = True

    return validar

# Valida si el record de un jugador es mayor, si es lo reemplaza
def view_record(from_clt):

    collection_mg = mydb["player"]

    for player in collection_mg.find():
        # Coincide en datos (user, pass)
        if from_clt["user_s"] == player["user"] and from_clt["pass_s"] == player["pass"]:

            if from_clt["record"] > player["record"]:
                # Update
                myquery = {"user":from_clt["user_s"], "pass":from_clt["pass_s"]}
                newvalues = {"$set": {"record": from_clt["record"]}}
                collection_mg.update_one(myquery, newvalues)

def set_result(player_1, player_2, resultado):

    # Si no existe en la base de datos validar es igual a False
    validar = False
    # Datos para conexion
    collection_mg = mydb["multi_game"]
    # Son los nombres de los records de cada player, llave_n es la llave del ganador
    llave_1 = "record_" + player_1
    llave_2 = "record_" + player_2
    llave_n = "record_" + resultado

    # Leer los jugadores de la base de datos y validar si ya esta lo requerido
    for game in collection_mg.find():

        options_1 = player_1 == game["player_1"] and player_2 == game["player_2"]
        options_2 = player_1 == game["player_2"] and player_2 == game["player_1"]
        # users no estan
        if  not options_1 and not options_2:
            continue
        elif options_1 or options_2:
            # Puntos del ganador
            points = game[llave_n]
            ''' Que el jugador 1 sea player_1 en la base de datos, sino cuando los mismos jugadores inicien en defiferente orden el juego
            se crearia otro registro '''
            if options_1:
                # Update
                myquery = {"player_1": player_1, "player_2": player_2, llave_n: points}
                newvalues = {"$set": {llave_n: points + 1}}
                collection_mg.update_one(myquery, newvalues)
            elif options_2:
                myquery = {"player_1": player_2, "player_2": player_1, llave_n: points}
                newvalues = {"$set": {llave_n: points + 1}}
                collection_mg.update_one(myquery, newvalues)
            # Ya no es 1era vez
            validar = True

    if not validar:
        if player_1 == resultado:
            # Insert dependiendo del ganador
            mydict = {"player_1": player_1, "player_2": player_2, llave_1: 1, llave_2: 0}
            x = collection_mg.insert_one(mydict)
        elif player_2 == resultado:
            mydict = {"player_1": player_1, "player_2": player_2, llave_1: 0, llave_2: 1}
            x = collection_mg.insert_one(mydict)



