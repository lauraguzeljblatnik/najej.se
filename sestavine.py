import csv
import os
import re

csv_sestavine = "sestavina_data.csv"
csv_recepti = "recepti_data.csv"

head = ['ID', 'količina', 'sestavina', 'merska enota']


def izberi_podatke(text):
    pattern = re.compile(
                        r'(?P<kolicina>\d+|nekaj|malo|sol|ščepec) (?P<sestavina>.*)'
                         , re.DOTALL)
    listt =[]
    for pat in re.finditer(pattern, text):
        listt += [[pat.group('kolicina'),pat.group('sestavina')]]
    return listt



with open(csv_recepti, 'r', encoding='utf-8') as recepti:
    with open(csv_sestavine, 'w', encoding='utf-8') as sestavine:
        pisalec_sestavin = csv.writer(sestavine,delimiter=',')
        pisalec_sestavin.writerow(head)
        bralec_receptov = csv.reader(recepti,delimiter=',')

        sez = []
        header = next(bralec_receptov)
        for vrstica in bralec_receptov:
            if len(vrstica) == 0:
                continue
            #print(vrstica)
            ID = vrstica[4]
            sestavine = vrstica[11]
            #print(ID,sestavine)
            sez += izberi_podatke(sestavine)
            #print(sez)
            for kolicina, sestavina in sez:
                pisalec_sestavin.writerow([ID,kolicina, sestavina])


        
    sestvine.close()
recepti.close()
        

    
    
