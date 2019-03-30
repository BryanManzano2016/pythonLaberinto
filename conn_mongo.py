import pymongo

def view_user(from_clt):

    print("CONNECT WITH DB")

    validar = False
    repetido = False
    # Datos para conexion
    myclient = pymongo.MongoClient('mongodb://127.0.0.1:27017/')
    mydb = myclient['players_laberinto']
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

def view_record(from_clt):
    print("CONNECT WITH DB")

    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    mydb = myclient['players_laberinto']
    collection_mg = mydb["player"]

    for player in collection_mg.find():

        if from_clt["user_s"] == player["user"] and from_clt["pass_s"] == player["pass"]:

            if from_clt["record"] > player["record"]:

                myquery = {"user":from_clt["user_s"], "pass":from_clt["pass_s"]}
                newvalues = {"$set": {"record": from_clt["record"]}}
                collection_mg.update_one(myquery, newvalues)
