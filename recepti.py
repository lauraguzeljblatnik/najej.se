# uvozimo ustrezne podatke za povezavo
import auth
auth.db = "sem2019_%s" % auth.user1


# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv


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
            ime TEXT NOT NULL,
            enota TEXT
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
            cas INTEGER NOT NULL DEFAULT (strftime('%s','now')),
            vsebina TEXT NOT NULL,
            recept INTEGER NOT NULL REFERENCES recept(id)
                        
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
            uporabnik INTEGER NOT NULL REFERENCES uporabnik(id),
            komentar INTEGER REFERENCES komentar(id)
            
            );
            """)
    conn.commit()
    
def ustvari_vrsta_recepta():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vsebuje (
            recept INTEGER NOT NULL REFERENCES recept(id),
            vrsta INTEGER REFERENCES vrsta(id),
            PRIMARY KEY (recept, vrsta)
            );
            """)
    conn.commit()
    
def ustvari_priloznost_recepta():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vsebuje (
            recept INTEGER NOT NULL REFERENCES recept(id),
            priloznost INTEGER REFERENCES priloznost(id),

            PRIMARY KEY (recept, priloznost)
            );
            """)
    conn.commit()

def ustvari_priprava_recepta():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vsebuje (
            recept INTEGER NOT NULL REFERENCES recept(id),
            priprava INTEGER REFERENCES priprava(id),

            PRIMARY KEY (recept, vrsta)
            );
            """)
    conn.commit()

def ustvari_vsebuje():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vsebuje (
            količina NUMERIC NOT NULL,
            recept INTEGER NOT NULL REFERENCES recept(id),
            sestavina INTEGER NOT NULL REFERENCES sestavina(id),
            PRIMARY KEY (recept, sestavina)
            );
            """)
    conn.commit()
   

def uvozi_podatke(file):
    #odpremo CSV datoteko
    with open(file, 'r', encoding='utf-8') as p:
        vrstica = csv.reader(p)
        next(vrstica)# izpusti naslovno vrstico
        for r in vrstica:
            print("berem")
            r = [None if x in ('', '-') else x for x in r]
            #r= r[1:(len(r))]
            #print(r)
            cur.execute(
                """INSERT INTO priloznost (priloznost) VALUES (%s)
                    RETURNING id""",r)
            rid, = cur.fetchone()
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

#pravice()
#ustvari_priprava()
#ustvari_priloznost()
uvozi_podatke("recepti.csv")
