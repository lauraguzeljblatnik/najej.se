import requests
import os
import re
import csv
from bs4 import BeautifulSoup

#url of the main page of the audi listing
recepti_frontpage_url = "https://www.kulinarika.net/recepti/"

#the directory to which we save out data
recepti_directory = "recepti_data"
#the file name we use to save the frontpage
frontpage_filename = "recepti_data.html"
#the filename for the csv file for the extracted data
csv_filename = "recepti_data.csv"

head = ['Ime', 'Opis recepta', 'Uporabnik',
        'Datum','ID recepta', 'Priložnost', 'Priprava', 'Sezona',
        'Vrsta jedi', 'Čas priprave', 'Sestavine', 'Postopek']

#poskusimo z beautifulsoup
with open(csv_filename, 'w', encoding='utf-8') as csvfile:
    pisalec_receptov = csv.writer(csvfile,delimiter=',')
    pisalec_receptov.writerow(head)


    pages = []

    #for i in range(1,513):
     #   url = recepti_frontpage_url + str(i)
     #   pages.append(url)

    for i in range(1,21964):
        url = recepti_frontpage_url + str(i)
        pages.append(url)


    for item in pages:
        page = requests.get(item)
        if page.ok and page.url != 'https://www.kulinarika.net/napaka/?error=1':
            #print(' ')
            soup = BeautifulSoup(page.text, 'html.parser')
            if soup.find('h1', itemprop="name"):
                ime = soup.find('h1', itemprop="name").text.strip()
            #print(ime)

            if soup.find ('p', itemprop="description"):
                opis = soup.find ('p', itemprop="description").text.strip()
            #print(opis)

            if soup.find('span', itemprop='author'):
                avtor = soup.find('span', itemprop='author').text.strip()
            #print(avtor)

            if soup.find('span', itemprop='datePublished'):
                datum = soup.find('span', itemprop='datePublished').text.strip()
            #print(datum)

            ID1 = soup.find('span', string=re.compile("ID recepta: (\d+)")).text.strip()
            ID = int(re.search(r'\d+', ID1).group())
            #print(ID)

            if soup.find('span', string=re.compile("priložnost: .+")):
                pril = soup.find('span', string=re.compile("priložnost: .+")).text.strip()
                priloznost = re.search(r': (.*)', pril).group(1)
                #print(priloznost)
            else:
                priloznost = None
            

            if soup.find('span', string=re.compile("priprava: .+")):
                prip = soup.find('span', string=re.compile("priprava: .+")).text.strip()
                nacin = re.search(r': (.*)', prip).group(1)
                #print(nacin)
            else:
                nacin = None

            if soup.find('span', string=re.compile("sezona: .+")):
                sez = soup.find('span', string=re.compile("sezona: .+")).text.strip()
                sezona = re.search(r': (.*)', sez).group(1)
                #print(sezona)
            else:
                sezona = None

            if soup.find('span', string=re.compile("vrsta jedi: .+")):
                vr = soup.find('span', string=re.compile("vrsta jedi: .+")).text.strip()
                vrsta = re.search(r': (.*)', vr).group(1)
                #print(vrsta)
            else:
                vrsta = None

            if soup.find('span', class_='cas'):
                cas = soup.find('span', class_='cas').text.strip()
            #print(cas)

            if soup.find('p', itemprop="recipeInstructions"):
                priprava = ''
                p = soup.find_all('p', itemprop="recipeInstructions")
                for el in p:
                    priprava += el.text.strip()
            #print(priprava)

            s = soup.find_all('p', itemprop="recipeIngredient")
            ses = ''
            for el in s:
                ses += el.text.strip() + ' ' #popravi
            #print(ses)

            pisalec_receptov.writerow([ime, opis, avtor, datum, ID, priloznost, nacin, sezona, vrsta,cas,priprava, ses])

        else:
            webpage_text = "Unable"

csvfile.close()
