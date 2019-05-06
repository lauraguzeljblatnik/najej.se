# uvozimo ustrezne podatke za povezavo
import auth
auth.db = "sem2019_%s" % auth.user

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv

def ustvari_uporabnik():
    cur.execute("""
        CREATE TABLE uporabnik(
            id SERIAL NOT NULL,
            ime TEXT NOT NULL,
            skor NUMERIC NOT NULL
        """)
    conn.commit()

def ustvari_sestavina():
    cur.execute("""
        CREATE TABLE sestavina(
            id SERIAL NOT NULL,
            ime TEXT NOT NULL
    """)
    conn.commit()

def ustvari_vrsta():
    cur.execute("""
        CREATE TABLE vrsta(
            kategorija TEXT NOT NULL
    """)
    conn.commit()

def ustvari_priloznost():
    cur.execute("""
        CREATE TABLE priloznost(
            priloznost TEXT NOT NULL
    """)
    conn.commit()

def ustvari_priprava():
    cur.execute("""
        CREATE TABLE priprava(
            priprava TEXT NOT NULL
    """)
    conn.commit()    

def ustvari_recept():
    cur.execute("""
        CREATE TABLE recept (
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
    
            
            
