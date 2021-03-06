#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

#datumi in čas
import datetime
from datetime import datetime


# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import subprocess

#kriptografija za gesla
import hashlib

from datetime import date

#zaokroževanje
import math




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


#definiramo sezname z vsemi možnostmi razvrščanja:
razvrsti_recepte = [('Novejši naprej', 'recept.id DESC'),
                       ('Starejši naprej', 'recept.id ASC'),
                       ('Ime recepta - od A do Ž', 'recept.ime ASC'),
                       ('Ime recepta - od Ž do A', 'recept.ime DESC'),
                       ('Padajoče glede na oceno', 'recept.ocena DESC'),
                       ('Naraščajoče glede na oceno', 'recept.ocena ASC'),
                        ('Padajoče glede na čas priprave', 'recept.cas DESC'),
                       ('Naraščajoče glede na čas priprave', 'recept.cas ASC')]

st_stran = [('10 na stran'),('20 na stran'), ('50 na stran'), ('vsi')]

mozni_casi = [('do 30min', '0 AND 30'),('30min - 1h','30 AND 60'),
    ( '1h - 2h','60 AND 120'), ('2h ali več', ' 120 AND 10000000000000')]
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
    cur.execute("SELECT * FROM recept ORDER BY id DESC")
    return template('recepti.html', username = username, recept=cur, razvrsti = 0, 
            moznosti_razvrscanje = razvrsti_recepte, st_na_stran = 3, moznosti_stran = st_stran,
            st_strani = 1 )

@post("/recepti")
def recepti_post():
    username = get_user()
    #razvrscanje
    raz = request.forms.razvrsti
    raz = int(raz)
    cur.execute("SELECT * FROM recept ORDER BY " + razvrsti_recepte[raz][1])
    recept = cur.fetchall()
    return template('recepti.html', username = username, recept = recept,
             razvrsti = raz, moznosti_razvrscanje = razvrsti_recepte, st_na_stran = 3, moznosti_stran = st_stran) 

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
        # Gesli se ne ujemata
        return template("registracija.html",
                               username=None,
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
    cur.execute("SELECT COUNT(*) FROM recept JOIN uporabnik ON uporabnik.id = recept.uporabnik WHERE uporabnik.ime=%s", [username])
    [[st_receptov]] = cur.fetchall()
    cur.execute("SELECT id FROM uporabnik WHERE ime=%s", [username])
    [[id_upo]] = cur.fetchall()
    cur.execute("SELECT (skor) FROM uporabnik WHERE ime=%s", [username])
    [[skor]] = cur.fetchall()
    if skor == 0:
        skor = st_receptov
        cur.execute("SELECT ocena FROM recept JOIN uporabnik ON uporabnik.id = recept.uporabnik WHERE uporabnik.ime=%s", [username])
    vse_ocene = cur.fetchall()
    povp_ocena = 0
    nenicelne = 0
    for ocena in vse_ocene:
        if ocena[0] != 0:
            povp_ocena += ocena[0]
            nenicelne += 1
    if nenicelne != 0:
        povp_ocena = povp_ocena/nenicelne
    else:
        povp_ocena = None
    return template("mojprofil.html", username = username, id_upo = id_upo, skor = skor, st_receptov = st_receptov, povp_ocena = povp_ocena)

@post("/mojprofil")
def profil_post():
    username = get_user()
        #iskanje 
    cur.execute("SELECT DISTINCT recept.id, recept.ime, opis, uporabnik.ime, recept.ocena, recept.cas FROM recept "
        "JOIN uporabnik ON uporabnik.id = recept.uporabnik "
        "WHERE (uporabnik.ime) = %s "
        "ORDER BY id DESC", [username])
    recept = cur.fetchall()
    sporocilo = None
    if recept == []:
        sporocilo = "NISI ŠE DODAL RECEPTOV!"
    #st vseh receptov
    cur.execute("SELECT COUNT(*) FROM recept")
    [[st_receptov]] = cur.fetchall()
    return template('rezultati.html', username = username, recept = recept,
             razvrsti = 0, moznosti_razvrscanje = razvrsti_recepte, st_na_stran = 3, moznosti_stran = st_stran,
             st_receptov =  st_receptov, st_strani = 1, sporocilo = sporocilo)




@get("/spremenigeslo")
def spremenigeslo():
    username = get_user()
    return template("spremenigeslo.html", username=username, napaka=None)

@post("/spremenigeslo")
def spremenigeslo_post():
    """Obdelaj formo za spreminjanje podatkov o uporabniku."""
    # Kdo je prijavljen?
    username = get_user()
    # Staro geslo (je obvezno)
    password1 = password_md5(request.forms.password1)
    # Preverimo staro geslo
    cur.execute ("SELECT 1 FROM uporabnik WHERE ime=%s AND geslo=%s",
               [username, password1])
    # Pokazali bomo eno ali več sporočil, ki jih naberemo v seznam
    sporocila = []
    if cur.fetchone():
        # Geslo je ok
        # spremenimo geslo
        password2 = request.forms.password2
        password3 = request.forms.password3
        if password2 or password3:
            # Preverimo, ali se gesli ujemata
            if password2 == password3:
                # Vstavimo v bazo novo geslo
                password2 = password_md5(password2)
                cur.execute ("UPDATE uporabnik SET geslo=%s WHERE ime = %s", [password2, username])
                conn.commit()
                sporocila.append(("alert-success", "Spremenili ste geslo."))
            else:
                return template("spremenigeslo.html",
            username=username,
            napaka='Gesli se ne ujemata')
    else:
        # Geslo ni ok
        return template("spremenigeslo.html",
            username=username,
            napaka='Napačno staro geslo')
    # Prikažemo stran z uporabnikom, z danimi sporočili. Kot vidimo,
    # lahko kar pokličemo funkcijo, ki servira tako stran
    redirect("/mojprofil")


@get("/dodajrecept")
def dodajrecept():
    username = get_user()
    return template("dodajrecept.html", username = username, opozorilo = None)


@post("/dodajrecept")
def dodajrecept_post():
    username = get_user()
    if not username:
        redirect("/")
    ime = request.forms.ime_recepta
    cur.execute("SELECT COUNT(*) FROM recept WHERE ime = %s", [ime])
    [[st_rec]] = cur.fetchall()
    if st_rec != 0:
        opozorilo = "Recept s takim imenom že obstaja!"
        return template("dodajrecept.html", username = username, opozorilo = opozorilo)
    opis = request.forms.opis
    priprava1 = request.forms.nacin_priprave
    priloznost1 = request.forms.priloznost
    vrsta1 = request.forms.vrsta
    postopek = request.forms.postopek
    cas = request.forms.cas
    cas = int(cas)
    #iz baze preberemo id uporabnika 
    cur.execute("SELECT id FROM uporabnik WHERE ime=%s", [username])
    [[up_id]] = cur.fetchall()
    up_id = int(up_id)
    ocena = 0
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    cur.execute("SELECT id FROM recept ORDER BY id DESC LIMIT 1")
    [[re]] = cur.fetchall()
    recept_id =  int(re) + 1
    #print([recept_id, ime, opis, postopek, today, ocena, cas, up_id])
    cur.execute("INSERT INTO recept (id, ime, opis, postopek, datum_objave, ocena, cas, uporabnik) VALUES (%s,%s, %s, %s, %s, %s, %s, %s)",
                   [recept_id, ime, opis, postopek, today, ocena, cas, up_id])
    #print("RECEPT DODAN!")

    #priloznost, priprava, vrsta, poiščemo in če ne obstaja dodamo
    #vrsta
    vrs = vrsta1.split(",")
    for vrsta in vrs:
        if vrsta == "":
            break
        vrsta = vrsta.strip().lower()
        #print(vrsta)
        cur.execute("SELECT id FROM vrsta WHERE ime = %s", [vrsta])
        vrst_id = cur.fetchall()
        #print(vrst_id)
        if vrst_id == []:
            cur.execute("INSERT INTO vrsta(ime) VALUES (%s) RETURNING id", [vrsta])
            [vrst_id] = cur.fetchone()
            vrst_id = int(vrst_id)
        else:
            vrst_id = int(vrst_id[0][0])
        #print(vrst_id)
        cur.execute("INSERT INTO vrsta_recepta(recept, vrsta) VALUES (%s, %s)", 
                    [recept_id, vrst_id])
    #priprava
    prip_pom = priprava1.split(",")
    for priprava in prip_pom:
        if priprava == "":
            break
        priprava = priprava.strip().lower()
        cur.execute("SELECT id FROM priprava WHERE ime = %s", [priprava])
        prip_id = cur.fetchall()
        if prip_id == []:
            cur.execute("INSERT INTO priprava(ime) VALUES (%s) RETURNING id", [priprava])
            [prip_id] = cur.fetchone()
            prip_id = int(prip_id)
        else: 
            prip_id = int(prip_id[0][0])
        cur.execute("INSERT INTO priprava_recepta(recept, priprava) VALUES (%s, %s)", 
                    [recept_id, prip_id])
    #priloznost
    prilo = priloznost1.split(",")
    #print(prilo)
    for priloznost in prilo:
        if priloznost == "":
            break
        priloznost = priloznost.strip().lower()
        cur.execute("SELECT id FROM priloznost WHERE  ime = %s", [priloznost])
        pril_id = cur.fetchall()
        if pril_id == []:
            cur.execute("INSERT INTO priloznost(ime) VALUES (%s) RETURNING id", [priloznost])
            [pril_id] = cur.fetchone()
            pril_id = int(pril_id)
        else:
            pril_id = int(pril_id[0][0])
        cur.execute("INSERT INTO priloznost_recepta(recept, priloznost) VALUES (%s, %s)", 
                    [recept_id, pril_id])
    print("VRSTA; PRIP; PRIL DODANE!")
    #sestavine 
    sest = request.forms.sestavine
    sestavine = sest.split(",")
    for el in sestavine:
        ena_sest = el.split(":")
        ime_sest = ena_sest[0].strip().lower()
        kolicina = int(ena_sest[1])
        enota = ena_sest[2].strip().lower()
        cur.execute("SELECT id FROM sestavina WHERE ime = %s", [ime_sest])
        sest_id = cur.fetchall()
        if sest_id == []:
            #print("DODAJAM SESTAVINO V BAZO")
            cur.execute("INSERT INTO sestavina(ime) VALUES (%s) RETURNING id", [ime_sest])
            [sest_id]  = cur.fetchone()
            sest_id = int(sest_id)
        else:
            sest_id = int(sest_id[0][0])
        cur.execute("INSERT INTO vsebuje(recept,sestavina,kolicina,enota) VALUES (%s, %s, %s, %s)",
                    [recept_id, sest_id, kolicina, enota])
    #print("SESTAVINE DODANE!")

    #če dodaš recept se ti poveča skor
    #iz baze preberemo skor uporabnika
    cur.execute("SELECT skor FROM uporabnik WHERE ime=%s", [username])
    [[skor]] = cur.fetchall()
    skor = int(skor)
    #skor povečamo za 1
    novi_skor = skor+1
    cur.execute("UPDATE uporabnik SET skor=%s WHERE ime = %s", [novi_skor, username])
    conn.commit()
    redirect("/")

@get("/isci")
def isci():
    username = get_user()
    cur.execute("SELECT ime FROM vrsta")
    vse_vrste = cur.fetchall()
    cur.execute("SELECT ime FROM priloznost")
    vse_priloznosti = cur.fetchall()
    cur.execute("SELECT ime FROM priprava")
    vse_priprave = cur.fetchall()
    return template("isci.html", username = username, mozni_casi = mozni_casi, vse_vrste = vse_vrste,
            vse_priloznosti = vse_priloznosti, vse_priprave = vse_priprave, moznosti_razvrscanje = razvrsti_recepte, razvrsti = 0)

@post("/isci")
def isci_post():
    username = get_user()
    naslov = request.forms.ime.lower()
    avtor = request.forms.avtor.lower()
    ocena = request.forms.ocena
    #cas ne dela
    cas1 = request.forms.cas
    if (cas1) in ['0','1','2','3']:
        cas = mozni_casi[int(cas1)][1]
    else:
        cas = '0 AND 999999999999'
        #razvrscanje 
    raz = request.forms.razvrsti
    raz = int(raz)
    sporocilo = None

    pogoji = ["recept.ime ILIKE '%%'||%s||'%%'", # ILIKE ignorira velikost črk
          "uporabnik.ime ILIKE '%%'||%s||'%%'", # procenti morajo biti podvojeni
          "ocena >= %s"]
    podatki = [naslov, avtor, ocena]
    
    ##vrsta
    vrsta1 = request.forms.getall('vrsta')
    vrsta = [(int(i) + 1) for i in vrsta1]
    st_vrst = len(vrsta)
    if st_vrst > 0:
        pogoji.append("({})".format(" OR ".join(["vrsta_recepta.vrsta = %s"] * st_vrst)))
        podatki += vrsta
    
    ##priloznost
    priloznost1 = request.forms.getall('priloznost')
    priloznost = [(int(i) + 1) for i in priloznost1]
    st_pril = len(priloznost)
    if st_pril > 0:
        pogoji.append("({})".format(" OR ".join(["priloznost_recepta.priloznost = %s"] * st_pril)))
        podatki += priloznost

    ##priprava
    priprava1 = request.forms.getall('priprava')
    priprava = [(int(i) + 1) for i in priprava1]
    st_prip = len(priprava)
    if st_prip > 0:
        pogoji.append("({})".format(" OR ".join(["priprava_recepta.priprava = %s"] * st_prip)))
        podatki += priprava
   
    #sestavine
    sest1 = request.forms.sestavine.lower()
    if sest1 != '':
        sestavine = sest1.split(',')
    else:
        sestavine = []
        print("sestavine")
    if len(sestavine) > 0:
        pogoji.append("({})".format(" OR ".join(["sestavina.ime = %s"] * len(sestavine))))
        podatki += sestavine
    
    #iskanje 
    cur.execute("""
    SELECT DISTINCT recept.id, recept.ime, opis, uporabnik.ime, recept.ocena, recept.cas
    FROM recept JOIN uporabnik ON uporabnik.id = recept.uporabnik
    LEFT JOIN vrsta_recepta ON recept.id = vrsta_recepta.recept
    LEFT JOIN priloznost_recepta ON recept.id = priloznost_recepta.recept
    LEFT JOIN priprava_recepta ON recept.id = priprava_recepta.recept
    JOIN vsebuje ON vsebuje.recept = recept.id
    JOIN sestavina ON vsebuje.sestavina = sestavina.id
    WHERE {}
    ORDER BY {}
""".format(" AND ".join(pogoji), razvrsti_recepte[raz][1]), podatki)
    
    print("""
    SELECT DISTINCT recept.id, recept.ime, opis, uporabnik.ime, recept.ocena, recept.cas
    FROM recept JOIN uporabnik ON uporabnik.id = recept.uporabnik
    LEFT JOIN vrsta_recepta ON recept.id = vrsta_recepta.recept
    LEFT JOIN priloznost_recepta ON recept.id = priloznost_recepta.recept
    LEFT JOIN priprava_recepta ON recept.id = priprava_recepta.recept
    JOIN vsebuje ON vsebuje.recept = recept.id
    JOIN sestavina ON vsebuje.sestavina = sestavina.id
    WHERE {}
    ORDER BY {}
""".format(" AND ".join(pogoji), razvrsti_recepte[raz][1]))
    recept = cur.fetchall()

    if recept == []:
        sporocilo = "NI ZADETKOV!"
    #st vseh receptov
    cur.execute("SELECT COUNT(*) FROM recept")
    [[st_receptov]] = cur.fetchall()
    return template('rezultati.html', username = username, recept = recept,
             razvrsti = raz, moznosti_razvrscanje = razvrsti_recepte, st_na_stran = 3, moznosti_stran = st_stran,
             st_receptov =  st_receptov, st_strani = 1, sporocilo = sporocilo)

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
    # komentariji - ok :)
    cur.execute("SELECT avtor, ime, cas, vsebina FROM komentar JOIN uporabnik ON uporabnik.id = komentar.avtor WHERE recept= %s", [int(x)])
    komentarji = cur.fetchall()

    return template('recept.html', username = username, x= x, recept = recept, avtor = avtor, priloznost = priloznost,
    priprava = priprava, vrsta = vrsta, sestavine = sestavine, komentarji=komentarji)

@post('/recept/:x')
def recept(x):
    username = get_user()
    priprava = request.forms.priprava
    priloznost = request.forms.priloznost
    vrsta = request.forms.vrsta
    print(priprava)
    if priprava:
        cur.execute("SELECT DISTINCT recept.id, recept.ime, opis, uporabnik.ime, recept.ocena, recept.cas FROM recept "
        "JOIN uporabnik ON uporabnik.id = recept.uporabnik "
        "LEFT JOIN priprava_recepta ON recept.id = priprava_recepta.recept "
        "JOIN priprava ON priprava_recepta.priprava = priprava.id "
        "WHERE priprava.ime = %s "
        "ORDER BY id DESC", [str(priprava)])
    if vrsta:
        cur.execute("SELECT DISTINCT recept.id, recept.ime,  opis, uporabnik.ime, recept.ocena, recept.cas FROM recept "
        "JOIN uporabnik ON uporabnik.id = recept.uporabnik "
        "LEFT JOIN vrsta_recepta ON recept.id = vrsta_recepta.recept "
        "JOIN vrsta ON vrsta_recepta.vrsta = vrsta.id "
        "WHERE vrsta.ime = %s "
        "ORDER BY id DESC", [str(vrsta)])        
    if priloznost:
        cur.execute("SELECT DISTINCT recept.id, recept.ime,  opis, uporabnik.ime, recept.ocena, recept.cas  FROM recept "
        "JOIN uporabnik ON uporabnik.id = recept.uporabnik "
        "LEFT JOIN priloznost_recepta ON recept.id = priloznost_recepta.recept "
        " JOIN priloznost ON priloznost_recepta.priloznost = priloznost.id "
        "WHERE priloznost.ime = %s "
        "ORDER BY id DESC", [str(priloznost)])
    recept = cur.fetchall()
    sporocilo = None
    #st vseh receptov
    cur.execute("SELECT COUNT(*) FROM recept")
    [[st_receptov]] = cur.fetchall()
    return template('rezultati.html', username = username, recept = recept,
             razvrsti = 0, moznosti_razvrscanje = razvrsti_recepte, st_na_stran = 3, moznosti_stran = st_stran,
             st_receptov =  st_receptov, st_strani = 1, sporocilo = sporocilo)



@post("/komentar/<x:int>/")
def komentar(x):
    """Vnesi nov komentar"""
    username = get_user()
    komentar = request.forms.komentar
    #iz baze preberemo id uporabnika 
    cur.execute("SELECT id FROM uporabnik WHERE ime=%s", [username])
    [[id]] = cur.fetchall()
    id = int(id)
    cur.execute('''INSERT INTO komentar (avtor, vsebina, recept) VALUES (%s, %s, %s)''',
                    [id, komentar, int(x)])
    #za vsak komentar se uporabniku skor poveča za 1
    #iz baze preberemo skor uporabnika
    cur.execute("SELECT skor FROM uporabnik WHERE ime=%s", [username])
    [[skor]] = cur.fetchall()
    skor = int(skor)
    #skor povečamo za 2
    novi_skor = skor+2
    cur.execute("UPDATE uporabnik SET skor=%s WHERE ime = %s", [novi_skor, username])
    conn.commit()
    redirect("/recept/{0}".format(int(x)))



@post("/ocena/<x:int>/")
def ocena(x):
    """oceni recept"""
    username = get_user()
    ocenjeno = request.forms.ocena
    ocenjeno = float(ocenjeno)
    cur.execute("SELECT ocena FROM recept WHERE id = %s", [int(x)])
    [[ocena]] = cur.fetchall()
    ocena = float(ocena)
    if ocena == 0:
        nova_ocena = ocenjeno
        nova_ocena = int(nova_ocena)
    else:
        nova_ocena = int((ocenjeno + ocena)/2)
    cur.execute("UPDATE recept SET ocena=%s WHERE id = %s", (nova_ocena, int(x)))
    #če oceniš recept se ti poveča skor
    #iz baze preberemo skor uporabnika
    cur.execute("SELECT skor FROM uporabnik WHERE ime=%s", [username])
    [[skor]] = cur.fetchall()
    skor = int(skor)
    #skor povečamo za 2
    novi_skor = skor+2
    cur.execute("UPDATE uporabnik SET skor=%s WHERE ime = %s", [novi_skor, username])
    conn.commit()
    redirect("/recept/{0}".format(int(x)))

    
    

@get("/profil/:x")
def profil(x):
    """Prikaži stran uporabnika"""
    username = get_user()
    cur.execute("SELECT ime FROM uporabnik WHERE id = %s", [int(x)])
    [[ime]] = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM recept JOIN uporabnik ON uporabnik.id = recept.uporabnik WHERE uporabnik.id=%s", [int(x)])
    [[st_receptov]] = cur.fetchall()
    cur.execute("SELECT (skor) FROM uporabnik WHERE id=%s", [int(x)])
    [[skor]] = cur.fetchall()
    if skor == 0:
        skor = st_receptov
    cur.execute("SELECT ocena FROM recept JOIN uporabnik ON uporabnik.id = recept.uporabnik WHERE uporabnik.id=%s", [int(x)])
    vse_ocene = cur.fetchall()
    povp_ocena = 0
    nenicelne = 0
    for ocena in vse_ocene:
        if ocena[0] != 0:
            povp_ocena += ocena[0]
            nenicelne += 1
    if nenicelne != 0:
        povp_ocena = povp_ocena/nenicelne
    else:
        povp_ocena = None
    
    return template("profil.html", username = username, x= x, ime = ime, st_receptov = st_receptov, skor = skor,
                        povp_ocena = povp_ocena) 
    
@post("/profil/:x")
def profil_post(x):
    username = get_user()
    #iskanje 
    cur.execute("SELECT DISTINCT recept.id, recept.ime, opis, uporabnik.ime, recept.ocena, recept.cas FROM recept "
        "JOIN uporabnik ON uporabnik.id = recept.uporabnik "
        "WHERE (uporabnik.id) = %s "
        "ORDER BY id DESC", [int(x)])
    recept = cur.fetchall()
    sporocilo = None
    if recept == []:
        sporocilo = "UPORABNIK ŠE NI DODAL RECEPTOV!"
    #st vseh receptov
    cur.execute("SELECT COUNT(*) FROM recept")
    [[st_receptov]] = cur.fetchall()
    return template('rezultati.html', username = username, recept = recept,
             razvrsti = 0, moznosti_razvrscanje = razvrsti_recepte, st_na_stran = 3, moznosti_stran = st_stran,
             st_receptov =  st_receptov, st_strani = 1, sporocilo = sporocilo)



######################################################################
# Glavni program

# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

# poženemo strežnik na portu 8080, glej http://localhost:8080/
#dodaj na koncu reloader = True, sem izbirsala ker ni delalo
run(host='localhost', port=8080)


