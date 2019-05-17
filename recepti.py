# uvozimo ustrezne podatke za povezavo
import auth
auth.db = "sem2019_%s" % auth.user

#prijava na bazo, (z sqlite3):
#conn = sqlite3.connect('...')
#curzor :
#cur = conn.cursor()

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv
import sqlite3

def ustvari_uporabnik():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS uporabnik(
            id SERIAL NOT NULL,
            ime TEXT NOT NULL,
            skor NUMERIC NOT NULL
        """)
    conn.commit()

def ustvari_sestavina():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sestavina(
            id SERIAL PRIMARY KEY NOT NULL,
            ime TEXT NOT NULL
    """)
    conn.commit()

def ustvari_vrsta():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vrsta(
            id SERIAL PRIMARY KEY NOT NULL,
            kategorija TEXT NOT NULL
    """)
    conn.commit()

def ustvari_priloznost():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS priloznost(
            id SERIAL PRIMARY KEY NOT NULL,
            priloznost TEXT NOT NULL
    """)
    conn.commit()

def ustvari_priprava():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS priprava(
            id SERIAL PRIMARY KEY NOT NULL
            priprava TEXT NOT NULL
    """)
    conn.commit()    

def ustvari_recept():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recept (
            id SERIAL PRIMARY KEY,
            ime TEXT NOT NULL,
            opis TEXT NOT NULL,
            postopek TEXT NOT NULL,
            datum DATE NOT NULL,
            ocena NUMERIC,
            cas TEXT,
            rec_sestavina TEXT REFERENCES sestavina(id),
            rec_vrsta TEXT REFERENCES vrsta(kategorija),
            rec_uporabnik REFERENCES uporabnik(id),
            rec_priloznost REFERENCES priloznost(priloznost),
            rec_priprava REFERENCES priprava(priprava)
            komentar TEXT
            
            );
            """)
    conn.commit()

def ustvari_vsebuje():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vsebuje (
            količina NUMERIC,
            recept INT
            rec_sestavina TEXT REFERENCES sestavina(id),
                        
            );
            """)
    conn.commit()



def uvozi_podatke():
    #odpremo CSV datoteko
    with open('recepti_data.csv', 'r', encoding='utf-8') as p:
        vrstice = csv.reader(p)
        next(vrstice) # izpusti naslovno vrstico
        for(ime, opis, uporabnik, datum, ID, priložnost, priprava, sezona, vrsta, sestavine, postopek) in vrstice:
            cur.execute(
                """INSERT INTO recept (ID, ime, opis, postopek, datum, cas) VALUES (?,?,?,?.?.?)"""
                [ID, ime, opis, postopek, datum, cas])
        conn.commit()
            
            
