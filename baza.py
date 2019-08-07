#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

#datumi in čas
import datetime

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

#kriptografija za gesla
import hashlib 





#########################################################################
#konfiguracija

#Da se bodo predloge same osvežile in da bomo dobivali lepa sporocila o napakah
#odkomentiraj, če želiš sporočila o napakah
debug(True)

#datoteka v kateri je baza
baza_datoteka = "napolni_bazo"

#Mapa s staticnimi datotekami
static_dir = "./static"

# Skrivnost za kodiranje cookijev
secret = "to skrivnost je zelo tezko uganiti 1094107c907cw982982c42"

##########################################################################
# Pomožne funkcije

def password_md5(s):
    """Vrni MD5 hash danega UTF-8 niza. Gesla vedno spravimo v bazo
       kodirana s to funkcijo."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()

# To smo dobili na http://stackoverflow.com/questions/1551382/user-friendly-time-format-in-python
# in predelali v slovenščino. Da se še izboljšati, da bo pravilno delovala dvojina itd.
def pretty_date(time):
    """
    Predelaj čas (v formatu Unix epoch) v opis časa, na primer
    'pred 4 minutami', 'včeraj', 'pred 3 tedni' ipd.
    """

    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "zdaj"
        if second_diff < 60:
            return "pred " + str(second_diff) + " sekundami"
        if second_diff < 120:
            return  "pred minutko"
        if second_diff < 3600:
            return "pred " + str( second_diff // 60 ) + " minutami"
        if second_diff < 7200:
            return "pred eno uro"
        if second_diff < 86400:
            return "pred " + str( second_diff // 3600 ) + " urami"
    if day_diff == 1:
        return "včeraj"
    if day_diff < 7:
        return "pred " + str(day_diff) + " dnevi"
    if day_diff < 31:
        return "pred " + str(day_diff//7) + " tedni"
    if day_diff < 365:
        return "pred " + str(day_diff//30) + " meseci"
    return "pred " + str(day_diff//365) + " leti"

def get_user():
    """Poglej cookie in ugotovi, kdo je prijavljeni uporabnik,
       vrni njegov username in ime. 
    """
    # Dobimo username iz piškotka
    username = request.get_cookie('username', secret=secret)
    # Preverimo, ali ta uporabnik obstaja
    if username is not None:
        cur.execute("SELECT ime FROM uporabnik WHERE ime=%s",
                  [username])
        r = cur.fetchone()
        if r is not None:
            # uporabnik obstaja, vrnemo njegove podatke
            return username
    # Če pridemo do sem, uporabnik ni prijavljen, naredimo redirect
    else:
        return None


########################################################################
# Server

@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')

@get('/')
def index():
    username = get_user()
    cur.execute("SELECT * FROM recept ORDER BY id DESC LIMIT 8")
    return template('glavna.html', username = username, recept = cur)

@get('/recepti')
def recepti():
    username = get_user()
    cur.execute("SELECT * FROM recept")
    return template('recepti.html', username = username, recept=cur)

@get("/prijava")
def login():
    """Serviraj formo za login."""
    return template("prijava.html",
                           napaka=None)


@post("/prijava")
def login_post():
    """Obdelaj izpolnjeno formo za prijavo"""
    # Uporabniško ime, ki ga je uporabnik vpisal v formo
    username = request.forms.username
    # Izračunamo MD5 has gesla, ki ga bomo spravili
    password = password_md5(request.forms.password)
    # Preverimo, ali se je uporabnik pravilno prijavil
    cur.execute("SELECT * FROM uporabnik WHERE ime=%s AND geslo=%s",
              [username, password])
    if cur.fetchone() is None:
        # Username in geslo se ne ujemata
        return template("prijava.html",
                               napaka="Nepravilna prijava",
                        username = username)
    else:
        # Vse je v redu, nastavimo cookie in preusmerimo na glavno stran
        response.set_cookie('username', username, path='/', secret=secret)
    redirect("/")

@get('/logout')
def logout():
    """Pobriši cookie in preusmeri na login."""
    response.delete_cookie('username')
    redirect("/")

@get('/registracija')
def register():
    return template("registracija.html", napaka=None, username=None)

@post("/registracija")
def register_post():
    """Registriraj novega uporabnika."""
    username = request.forms.username
    print(username)
    password1 = request.forms.password1
    password2 = request.forms.password2
    # Ali uporabnik že obstaja?
    cur.execute("SELECT * FROM uporabnik WHERE ime=%s", [username])
    if cur.fetchone():
        # Uporabnik že obstaja
        return template("registracija.html",
                               username=username,
                               napaka='To uporabniško ime je že zavzeto')
    elif not password1 == password2:
        # Geslo se ne ujemata
        return template("registracija.html",
                               username=username,
                               napaka='Gesli se ne ujemata')
    else:
        # Vse je v redu, vstavi novega uporabnika v bazo
        password = password_md5(password1)
        cur.execute("INSERT INTO uporabnik (ime, skor, geslo) VALUES (%s, %s, %s)",
                  (username, 0, password))
        conn.commit()
        # Daj uporabniku cookie
        response.set_cookie('username', username, path='/', secret=secret)
        redirect("/")

@get("/mojprofil")
def profil():
    """Prikaži stran uporabnika"""
    username = get_user()
    cur.execute("SELECT * FROM uporabnik WHERE ime=%s", [username])
    uporabnik = cur.fetchall()
    return template("mojprofil.html", username = username, uporabnik = uporabnik)

@get("/dodajrecept")
def dodajrecept():
    username = get_user()
    return template("dodajrecept.html", username = username)

@get("/isci")
def isci():
    username = get_user()
    return template("isci.html", username = username)

#to še popravi!!!!!
@get('/recept/:x')
def recept(x):
    username = get_user()
    cur.execute("SELECT * FROM recept WHERE id = %s", [int(x)])
    recept = cur.fetchall()
    cur.execute("SELECT uporabnik.ime FROM uporabnik JOIN recept ON uporabnik.id = recept.uporabnik WHERE recept.id = %s", [int(x)])
    avtor = cur.fetchall()
    avtor = avtor[0][0]
    cur.execute("SELECT recept, ime FROM priloznost_recepta JOIN priloznost ON priloznost_recepta.priloznost= priloznost.id WHERE recept = %s", [int(x)])
    priloznost = cur.fetchall()
    cur.execute("SELECT recept, ime FROM priprava_recepta JOIN priprava ON priprava_recepta.priprava = priprava.id WHERE recept = %s", [int(x)])
    priprava = cur.fetchall()
    cur.execute("SELECT recept, ime FROM vrsta_recepta JOIN vrsta ON vrsta_recepta.vrsta = vrsta.id WHERE recept = %s", [int(x)])
    vrsta = cur.fetchall()
    cur.execute("SELECT recept, ime, kolicina, enota FROM vsebuje JOIN sestavina ON vsebuje.sestavina = sestavina.id WHERE recept = %s", [int(x)])
    sestavine = cur.fetchall()


    return template('recept.html', username = username, x= x, recept = recept, avtor = avtor, priloznost = priloznost,
    priprava = priprava, vrsta = vrsta, sestavine = sestavine)






@get("/profil/:x")
def profil(x):
    """Prikaži stran uporabnika"""
    username = get_user()
    cur.execute("SELECT * FROM uporabnik WHERE id = %s", [int(x)])
    uporabnik = cur.fetchall()
    return template("profil.html", username = username, x= x, uporabnik = uporabnik)    

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
#dodaj na koncu reloader = True, sem izbirsala ker ni delalo
run(host='localhost', port=8080)
