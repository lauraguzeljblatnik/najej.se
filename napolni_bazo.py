# uvozimo ustrezne podatke za povezavo
import auth
auth.db = "sem2019_%s" % auth.user


# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE) # se znebimo problemov s šumniki

import csv
import numpy as np
from datetime import datetime


def izbrisi():
    cur.execute("""
        drop table IF EXISTS uporabnik CASCADE;
        drop TABLE IF EXISTS sestavina CASCADE;
        drop table IF EXISTS vrsta CASCADE;
        drop table IF EXISTS priprava CASCADE;
        drop table IF EXISTS priloznost CASCADE;
        drop table IF EXISTS recept CASCADE;
        drop table IF EXISTS komentar CASCADE;
        drop table IF EXISTS vsebuje CASCADE;
        drop table IF EXISTS priprava_recepta CASCADE;
        drop table IF EXISTS priloznost_recepta CASCADE;
        drop table IF EXISTS vrsta_recepta CASCADE;
    """)
    conn.commit()

def ustvari_uporabnik():
    cur.execute("""
        drop table IF EXISTS uporabnik CASCADE;
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
            recept INTEGER NOT NULL REFERENCES recept(id),
            sestavina INTEGER NOT NULL REFERENCES sestavina(id),
            kolicina NUMERIC NOT NULL,
            enota TEXT,
            PRIMARY KEY (recept, sestavina)
            );
            """)
    conn.commit()


def uvozi(recepti, sestavine):
    #odpremo CSV datoteko
    with open(recepti, 'r', encoding='utf-8') as p:
        with open(sestavine, 'r', encoding='utf-8') as f:
            vrs_rec = csv.reader(p, delimiter = ',')
            vrs_ses = csv.reader(f, delimiter = ',')
            next(vrs_rec)# izpusti naslovno vrstico
            next(vrs_ses)
            #ustvarimo prazne sezname
            pril = []
            prip = []
            vrst = []
            upo = []
            ime = []
            opis = []
            id_ = []
            datum = []
            cas = []
            postopek = []
            ocena= []
            sest = []
            pomozni_vsebuje = []


            #peljemo se čez recept
            for r in vrs_rec: 
                if len(r) == 0:
                    continue
                pril1 = (r[5].split(','))
                pril.append((pril1[0]).strip())
                prip1 = (r[6].split(','))
                prip.append((prip1[0]).strip())
                vrst1 = (r[8].split(','))
                vrst.append((vrst1[0]).strip())
                upo1 = (r[2].split(','))
                upo += upo1
                ime1 =  (r[0])
                ime.append(str(ime1))
                opis1 = (r[1])
                opis.append(str(opis1))
                datum1 = (r[3].split(','))
                datum2 = datetime.strptime(datum1[0], '%d.%m.%Y')
                datum.append(datum2.date())
                id1 = (r[4].split(','))
                id_.append(int(id1[0]))
                cas1 = (r[9].split('..'))
                cas += cas1
                postopek1 = (r[10])
                postopek.append(str(postopek1))
                ocena += [0]

            #polepšamo podatke
            uporabnik = set()
            for el in upo:
                if el != '':
                    uporabnik.add(el.strip())   

            priloznost = set()
            for el in pril:
                if el != '':
                    priloznost.add(el.strip())

            priprava = set()
            for el in prip:
                if el != '':
                    priprava.add(el.strip())
                    
            vrsta = set()
            for el in vrst:
                if el != '':
                    vrsta.add(el.strip())
                    
            nepodvojeni = []
            #peljemo se čez sestavine
            for r in vrs_ses:
                if len(r) == 0:
                    continue
                sest1 = (r[3].split(','))
                id_recepta = r[0].split(',')
                kolicina = r[1].split(',')
                enota = r[2].split(',')
                sest2 = sest1[0].strip()
                sest.append(sest2)
                if [sest2, int(id_recepta[0])] not in nepodvojeni:
                    nepodvojeni.append([sest2, int(id_recepta[0])])
                    pomozni_vsebuje.append((int(id_recepta[0]), float(kolicina[0]), enota[0]))
            sestavine = set()
            for el in sest:
                if el != '':
                    sestavine.add(el.strip())

            #prazni slovarji uploadanih podatkov
            uploaded_uporabnik = {}
            uploaded_sestavina = {}
            uploaded_recept = {}
            uploaded_vrsta = {}
            uploaded_priprava = {}
            uploaded_priloznost = {}

            #zapišemo podatke v tabele
            for el in priloznost:
                cur.execute(
                    """INSERT INTO priloznost(ime) VALUES ('%s') RETURNING id ;""" % str(el))
                priloznost_id, = cur.fetchone()
                uploaded_priloznost[el] = priloznost_id
            
            for el in priprava:
                cur.execute(
                    """INSERT INTO priprava(ime) VALUES ('%s') RETURNING id;""" % str(el))
                priprava_id, = cur.fetchone()
                uploaded_priprava[el] = priprava_id

            for el in vrsta:
                cur.execute(
                    """INSERT INTO vrsta(ime) VALUES ('%s') RETURNING id;""" % str(el))
                vrsta_id, = cur.fetchone()
                uploaded_vrsta[el] = vrsta_id
            
            for el in sestavine:
                cur.execute(
                    """INSERT INTO sestavina(ime) VALUES ('%s') RETURNING id;""" % str(el))
                sestavina_id, = cur.fetchone()
                uploaded_sestavina[el] = sestavina_id
                
            for el in uporabnik:
                cur.execute(
                """INSERT INTO uporabnik(ime, skor, geslo)
                VALUES ('%s', %s, '%s') RETURNING id;""" %( str(el),0,str(el)))
                uporabnik_id, = cur.fetchone()
                uploaded_uporabnik[el] = uporabnik_id

            #spremeni, če dodaš še več podatkov
            for i in range(107):
                cur.execute(
                """INSERT INTO recept(id, ime, opis, postopek, datum_objave, ocena, cas, uporabnik)
                VALUES (%(id)s, %(ime)s, %(opis)s, %(postopek)s, %(datum)s, %(ocena)s, %(cas)s, %(uporabnik)s) RETURNING id;""",
                {'id': id_[i], 'ime': ime[i], 'opis': opis[i], 'postopek': postopek[i],
                 'datum': datum[i], 'ocena': ocena[i], 'cas': cas[i],
                 'uporabnik': uploaded_uporabnik[upo[i]]})
                recept_id = cur.fetchone()
                uploaded_recept[i] = recept_id

            #print(pomozni_vsebuje)
            #print(uploaded_recept)
            #print(vrst)
            #print(uploaded_vrsta)
            
            #zapišemo relacijske tabele
            for i in range(len(sest)):
                cur.execute(
                    """INSERT INTO vsebuje(recept, sestavina,kolicina,enota)
                        VALUES (%s, %s, %s, '%s'); """
                    %(pomozni_vsebuje[i][0], uploaded_sestavina[sest[i]], pomozni_vsebuje[i][1], pomozni_vsebuje[i][2])
                )

            for i in range(107):
                if vrst[i] !=  '':
                    cur.execute(
                        """INSERT INTO vrsta_recepta(recept, vrsta)
                            VALUES (%s, %s); """
                        %(uploaded_recept[i][0], uploaded_vrsta[vrst[i]])
                    )
                if pril[i] != '':
                    cur.execute(
                        """INSERT INTO priloznost_recepta(recept, priloznost)
                            VALUES (%s, %s); """
                        %(uploaded_recept[i][0], uploaded_priloznost[pril[i]])
                    )
                if prip[i] !=  '':
                    cur.execute(
                        """INSERT INTO priprava_recepta(recept, priprava)
                            VALUES (%s, %s); """
                        %(uploaded_recept[i][0], uploaded_priprava[prip[i]])
                    )
                



            

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

izbrisi()

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

uvozi("recepti.csv", "sestavina.csv")

