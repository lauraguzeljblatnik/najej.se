import csv
import os
import re

csv_vrsta = "vrsta.csv"
csv_priloznost = "priloznost.csv"
csv_priprava = "priprava.csv"
csv_recepti = "recepti.csv"

head_vrsta = ['ID', 'vrsta']
head_priloznost = ['ID', 'priloznost']
head_priprava = ['ID', 'priprava']

#i je vrstica od vrste/priloznisti/priprave v datoteki recepti.csv
#vrsta: i=8
#priloznost: i=5
#priprava: i=6
def pomozna(input_file, csv_head, i):
    with open(csv_recepti, 'r', encoding='utf-8') as recepti:
        with open(input_file, 'w', encoding='utf-8') as dat:
            pisalec= csv.writer(dat,delimiter=',')
            pisalec.writerow(csv_head)
            bralec_receptov = csv.reader(recepti,delimiter=',')

            header = next(bralec_receptov)
            for vrstica in bralec_receptov:
                if len(vrstica) == 0:
                    continue
                #print(vrstica)
                ID = vrstica[4]
                pom = vrstica[i]
                #print(ID,sestavine)
                if pom == "":
                    continue
                pom2 = pom.split(",")

                #print(sez)
                for el in pom2:
                    pisalec.writerow([ID,el])
            
        dat.close()
    recepti.close()
        
pomozna(csv_vrsta, head_vrsta, 8)
pomozna(csv_priprava, head_priprava, 6)
pomozna(csv_priloznost, head_priloznost, 5)
    
    
