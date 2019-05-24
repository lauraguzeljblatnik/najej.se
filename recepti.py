# uvozimo ustrezne podatke za povezavo
import auth
auth.db = "sem2019_%s" % auth.user1


# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv
import numpy as np
from datetime import datetime


def ustvari_uporabnik():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS uporabnik(
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            skor NUMERIC NOT NULL,
            geslo TEXT NOT NULL
            );
        """)
    conn.commit()

def ustvari_sestavina():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sestavina(
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL
            );
    """)
    conn.commit()

def ustvari_vrsta():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vrsta(
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL
            );
    """)
    conn.commit()

def ustvari_priloznost():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS priloznost(
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL
        );
    """)
    conn.commit()

def ustvari_priprava():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS priprava(
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL
        );
    """)
    conn.commit()

    
def ustvari_komentar():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS komentar (
            id SERIAL PRIMARY KEY,
            avtor INTEGER NOT NULL REFERENCES uporabnik(id),
            cas DATE NOT NULL DEFAULT now(),
            vsebina TEXT NOT NULL,
            recept INTEGER REFERENCES recept(id)
            );
            """)
    conn.commit()


def ustvari_recept():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recept (
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            opis TEXT,
            postopek TEXT NOT NULL,
            datum_objave DATE NOT NULL,
            ocena NUMERIC,
            cas TEXT,
            uporabnik INTEGER NOT NULL REFERENCES uporabnik(id)            
            );
            """)
    conn.commit()
    
def ustvari_vrsta_recepta():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vrsta_recepta (
            recept INTEGER NOT NULL REFERENCES recept(id),
            vrsta INTEGER REFERENCES vrsta(id),
            PRIMARY KEY (recept, vrsta)
            );
            """)
    conn.commit()
    
def ustvari_priloznost_recepta():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS priloznost_recepta (
            recept INTEGER NOT NULL REFERENCES recept(id),
            priloznost INTEGER REFERENCES priloznost(id),

            PRIMARY KEY (recept, priloznost)
            );
            """)
    conn.commit()

def ustvari_priprava_recepta():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS priprava_recepta (
            recept INTEGER NOT NULL REFERENCES recept(id),
            priprava INTEGER REFERENCES priprava(id),

            PRIMARY KEY (recept, priprava)
            );
            """)
    conn.commit()

def ustvari_vsebuje():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vsebuje (
            kolicina NUMERIC NOT NULL,
            recept INTEGER NOT NULL REFERENCES recept(id),
            sestavina INTEGER NOT NULL REFERENCES sestavina(id),
            enota TEXT,
            PRIMARY KEY (recept, sestavina)
            );
            """)
    conn.commit()


def uvozi_vrsta_priprava_priloznost(file):
    #odpremo CSV datoteko
    with open(file, 'r', encoding='utf-8') as p:
        vrstica = csv.reader(p, delimiter = ',')
        next(vrstica)# izpusti naslovno vrstico
        #print(vrstica)
        sez1 = []
        sez2 = []
        sez3 = []
        for r in vrstica: 
            if len(r) == 0:
                continue
            pom1 = (r[5].split(','))
            sez1 += pom1
            pom2 = (r[6].split(','))
            sez2 += pom2
            pom3 = (r[8].split(','))
            sez3 += pom3

        priloznost = set()
        for el in sez1:
            if el != '':
                priloznost.add(el.strip())

        priprava = set()
        for el in sez2:
            if el != '':
                priprava.add(el.strip())
                
        vrsta = set()
        for el in sez3:
            if el != '':
                vrsta.add(el.strip())
                
        for el in priloznost:
            cur.execute(
                """INSERT INTO priloznost(ime) VALUES ('%s');""" % str(el))
        for el in priprava:
            cur.execute(
                """INSERT INTO priprava(ime) VALUES ('%s');""" % str(el))
        for el in vrsta:
            cur.execute(
                """INSERT INTO vrsta(ime) VALUES ('%s');""" % str(el))
        conn.commit()

def uvozi_sestavine(file):
    with open(file, 'r', encoding='utf-8') as p:
        vrstica = csv.reader(p, delimiter = ',')
        next(vrstica)# izpusti naslovno vrstico
        sez = []
        for r in vrstica:
            if len(r) == 0:
                continue
            pom = (r[3].split(','))
            sez += pom
        sestavine = set()
        for el in sez:
            if el != '':
                sestavine.add(el.strip())
        for el in sestavine:
            cur.execute(
                """INSERT INTO sestavina(ime) VALUES ('%s');""" % str(el))
        conn.commit()

def uvozi_uporabnik(file):
    with open(file, 'r', encoding='utf-8') as p:
        vrstica = csv.reader(p, delimiter = ',')
        next(vrstica)# izpusti naslovno vrstico
        sez = []
        for r in vrstica:
            if len(r) == 0:
                continue
            pom = (r[2].split(','))
            sez += pom
        uporabnik = set()
        for el in sez:
            if el != '':
                uporabnik.add(el.strip())
        uploaded = {}        
        for el in uporabnik:
            cur.execute(
                """INSERT INTO uporabnik(ime, skor, geslo)
                VALUES ('%s', %s, '%s') RETURNING id;""" %( str(el),0,str(el)))
            uporabnik_id = cur.fetchone()
            uploaded[el] = uporabnik_id
        print(uploaded)  
        conn.commit()
            
  
# uredi pravice za dostop do baze
def pravice():
    cur.execute("""
        GRANT ALL ON ALL TABLES IN SCHEMA public TO klarag;
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO klarag;
        GRANT ALL ON SCHEMA public TO klarag;
        GRANT ALL ON ALL TABLES IN SCHEMA public TO lauragb;
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO lauragb;
        GRANT ALL ON SCHEMA public TO lauragb;
        GRANT CONNECT ON DATABASE sem2019_klarag TO javnost;
        GRANT USAGE ON SCHEMA public TO javnost;
        GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;
        GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO javnost;
    """)
    print("dodane pravice")
    conn.commit()
            
            

#od baze ze odvežeš conn.close()

conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 

#KLICANJE FUNKCIJ

pravice()
ustvari_uporabnik()
ustvari_sestavina()
ustvari_vrsta()
ustvari_priprava()
ustvari_priloznost()
ustvari_recept()
ustvari_komentar()
ustvari_vsebuje()
ustvari_priprava_recepta()
ustvari_priloznost_recepta()
ustvari_vrsta_recepta()

#uvozi_vrsta_priprava_priloznost("recepti.csv")
#uvozi_sestavine("sestavina.csv")
uvozi_uporabnik("recepti.csv")
