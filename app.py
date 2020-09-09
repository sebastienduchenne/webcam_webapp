import os
import mysql.connector
import json
import time
from os import path, listdir
from flask import Flask, request, render_template, jsonify
from datetime import datetime
from multiprocessing import Process


app = Flask(__name__)


mydb = mysql.connector.connect(
  host="localhost",
  user="xxx",
  password="xxx",
  database="db"
)
mycursor = mydb.cursor()

# nb_max_scenes
mycursor.execute("SELECT COUNT(*) FROM scene;")
myresult = mycursor.fetchone()
nb_max_scenes = myresult[0]

# création du dossier temp si inexistant
if os.path.exists("enregistrements/temp") == False:
    os.mkdir("enregistrements/temp")


@app.route("/")
def accueil():
    ''' envoyer accueil.html ''' 
    print("accueil")
    return render_template("accueil.html")


@app.route("/connexion", methods = ['POST'])
def connexion():
    ''' connexion '''
    print("connexion")
    login = request.form.get('login')

    # vérifier que le login existe
    sql = "SELECT login, age, sexe FROM utilisateur WHERE utilisateur.login = '" + login + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchone()
    print(myresult)

    if myresult == None:
        return render_template("accueil.html", error_connexion = "Login incorrect")
    else:
        return render_template("enregistrement.html", login = myresult[0], age = myresult[1], sexe = myresult[2])


@app.route("/subscribe", methods = ['POST'])
def subscribe():
    ''' inscription de l'utilisateur'''
    print("subscribe")

    login = request.form.get('login')
    age = request.form.get('age')
    sexe = request.form.get('sexe')

    # vérifier que le login est inexistant
    sql = "SELECT login, age, sexe FROM utilisateur WHERE utilisateur.login = '" + login + "'"
    mycursor.execute(sql)
    myresult = mycursor.fetchone()

    if myresult == None:
        # ajout du login
        sql = "INSERT INTO utilisateur (login, age, sexe, id_en_cours) VALUES ('" + login + "', '" + age + "', '" + sexe + "', '1')"
        mycursor.execute(sql)
        mydb.commit()

        return render_template("enregistrement.html", login = login, age = age, sexe = sexe)
    else:
        return render_template("accueil.html", error_subscribe = "Ce login existe déjà.")


@app.route('/upload', methods = ['POST'])
def upload():
    ''' conversion de la vidéo en mp4 et extraction de l'audio '''
    print("upload")

    file = request.files['video']
    idScene_login = request.files['video'].filename
    name = idScene_login.split("_")
    idScene = name[0]
    login = name[1]

    # get info sur l'utilisateur
    sql = "SELECT scene.id, age, sexe, emotion FROM scene, utilisateur WHERE scene.id = '" + idScene + "' AND utilisateur.login = '" + login + "'"
    mycursor.execute(sql)
    res = mycursor.fetchone()

    # date
    now = datetime.now()
    dt_string = now.strftime("%Y_%m_%d_%Hh%Mm%Ss") #yyyy_mm_dd_hhmmss

    filename = str(idScene) + "_" + str(res[1]) + "_" + res[2] + "_" + res[3] + "_" + login + "_" + dt_string
    print("filename:",filename)

    # incrémenter id_en_cours
    sql = "UPDATE utilisateur SET id_en_cours = id_en_cours + 1 WHERE login = '" + login + "'"
    mycursor.execute(sql)
    mydb.commit()

    # conversion et extraction audio
    with open("enregistrements/temp/" + filename + ".webm", "wb") as video:
        video_stream = file.read()
        video.write(video_stream)
        p = Process(target=p_convertir, args=(filename,))
        p.start()
    
    return { "status" : "success" }


@app.route("/getScene", methods = ['POST'])
def getScene():
    ''' envoie de la scène en cours '''
    print("getScene")
    global nb_max_scenes

    json = request.get_json()
    login = json["login"]

    # get scene_a_jouer à l'id actuel
    sql = "SELECT id_en_cours FROM utilisateur WHERE login = '" + login +"'"
    mycursor.execute(sql)
    myresult = mycursor.fetchone()

    id_en_cours = myresult[0]

    if id_en_cours > nb_max_scenes:
        return { "status" : "FINI" }
    else:
        return getCurrentScene(login)


def getCurrentScene(login):
    ''' renvoyer la scène en cours '''
    print("getCurrentScene")
    print(login)
    global nb_max_scenes

    # get scene_a_jouer à l'id actuel
    sql = "SELECT scene.id, emotion, contexte, scene_a_jouer, age, sexe FROM scene, utilisateur WHERE utilisateur.id_en_cours = scene.id AND utilisateur.login = '" + login +"'"
    mycursor.execute(sql)
    myresult = mycursor.fetchone()

    id_current_scene = myresult[0]
    emotion = myresult[1]
    contexte = myresult[2]
    scene_a_jouer = myresult[3]
    age = myresult[4]
    sexe = myresult[5]

    res = { 
        'status' : 'ok',
        'nb_max_scenes' : nb_max_scenes,
        'id_en_cours': id_current_scene,
        'emotion': emotion,
        'contexte' : contexte,
        'scene_a_jouer' : scene_a_jouer,
        'age' : age,
        'sexe' : sexe,
    }
    print(res)
    return res


def p_convertir(filename):
    ''' fonction utilisée pour créer un processus qui convertit la vidéo '''
    os.system("..\\FFMPEG\\bin\\ffmpeg.exe -i enregistrements/temp/"+filename+".webm -r 20 -an enregistrements/" + filename + ".mp4") # conversion vidéo
    os.system("..\\FFMPEG\\bin\\ffmpeg.exe -i enregistrements/temp/"+filename+".webm enregistrements/" + filename + ".wav") # extraction audio
    os.remove("enregistrements/temp/" + filename + ".webm")
