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


#getting data from the web

def download_url_to_string(url, i):
    '''This funtion takes a url as argument and tries to download
          it using requests. Upon success, it returns the page
          contents as string'''
    url += str(i)
    webpage = requests.get(url)
    if webpage.ok:
        webpage_text = webpage.text
    else:
        webpage_text = "Unable"
    return webpage_text

def save_string_to_file(text, directory, filename):
    '''This function writes "text" to file "filename" located in directory
       "directory". IF ""rrrrf" is the empty string, use the
       current directory.'''
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None







#processing data

def read_file_to_string(directory, filename):
    '''This function returns the contents of the file as string'''
    path =os.path.join(directory, filename)
    with open(path, 'r') as file_in:
        return file_in.read

#KAJ JE TREBA POPRAVIT:
    # ne najde opisa - update: ker ga ni!, a ga dava ven?
    #ime in avtorja rudi grdo dobi, kaj je s temi b-ji :(
    #če neke stvari ni, potem je problem! npr priložnost, opis,...
    #kakšno je to kodiranje to, nič ne dela :(
    
    
    


def split_text_to_prod(text):
    pattern = re.compile(
                        r'<span class="trenutno">(?P<ime>.*?)</span></p>'
                        r'.*?'
##                        r'<p class="podnaslov" itemprop="description">(?P<opis>.*?)</p>'
##                        r'.*?'
                        r'<span itemprop=.author.>(?P<avtor>.*?)</span>'
                        r'.*?'
                        r'<span class=.after1. itemprop=.datePublished.>(?P<datum>.*?)</span>'
                        r'.*?'
                        r'<span class=.after1.>ID recepta: (?P<ID>.*?)</span>'
                        r'.*?'
##                        r'<span class=.after1.>priložnost:(?P<priložnost>.*?)</span>'
##                        r'.*?'
##                        r'<span class=.after1.>priprava:(?P<priprava>.*?)</span>'
##                        r'.*?'
##                        r'<span class=.after1.>sezona:(?P<sezona>.*?)</span>'
##                        r'.*?'
##                        r'<span class=.after1.>vrsta jedi:(?P<vrsta>.*?)</span>'
##                        r'.*?'
##                        r'<span class=.cas.>(?P<čas>.*?)</span>'
##                        r'.*?'
                        r'<p class="cf" itemprop="recipeIngredient"><span class="label"></span><span class="label-value">(?P<sestavine>.*?)</div>'
                        r'.*?'
                        r'<div id="receptPostopek"><h2>Postopek</h2>(?P<postopek>.*?)</div>'
                        ,re.DOTALL)
    listt =[]
    for pat in re.finditer(pattern, text):
        listt += [[ pat.group('ID'),
                   str(pat.group('ime').encode('utf-8')),
##                   str(pat.group('opis').encode('utf-8')),
                   str(pat.group('avtor').encode('utf-8')),
                   str(pat.group('datum').encode('utf-8')),
##                   str(pat.group('priložnost').encode('utf-8')),
##                   str(pat.group('priprava').encode('utf-8')),
##                   str(pat.group('sezona').encode('utf-8')),
##                   str(pat.group('vrsta').encode('utf-8')),
##                   str(pat.group('čas').encode('utf-8')),
                   str(pat.group('sestavine').encode('utf-8')),
                   str(pat.group('postopek').encode('utf-8'))
            ]]
    return listt



def all_data(url):
    data = []
    for i in range(1,10):
        text = download_url_to_string(url, i)
        data += split_text_to_prod(text)
    return data


def convert_to_csv(info, head, name):
    with open(name,'w') as csvFile:
        csvFile.write(head)
        for line in info:
            csvFile.write(','.join(line) + '\n')
    csvFile.close()


head = "Ime, Opis recepta, Uporabnik, Datum, ID recepta, Priložnost, Priprava, Sezona, Vrsta jedi, Čas priprave, Sestavine, Postopek"

#Klicanje funkcij
#text = download_url_to_string(recepti_frontpage_url, 1)
#print(text)
#save_string_to_file(text, recepti_directory, frontpage_filename)
#data = all_data(recepti_frontpage_url)
#print(data)
#convert_to_csv(data,head,csv_filename)
 
#poskusimo z beautifulsoup
f = csv.writer(open(csv_filename, 'w'))
f.writerow(head)

pages = []

for i in range(1,5):
    url = recepti_frontpage_url + str(i)
    pages.append(url)

for i in range(20689,20692):
    url = recepti_frontpage_url + str(i)
    pages.append(url)


for item in pages:
    page = requests.get(item)
    if page.ok:
        soup = BeautifulSoup(page.text, 'html.parser')
        if soup.find('h1', itemprop="name"):
            ime = soup.find('h1', itemprop="name").text.strip()
        print(ime)
        if soup.find ('p', itemprop="description"):
            opis = soup.find ('p', itemprop="description").text.strip()
        print(opis)
        if soup.find('span', itemprop='author'):
            avtor = soup.find('span', itemprop='author').text.strip()
        print(avtor)
        if soup.find('span', itemprop='datePublished'):
            datum = soup.find('span', itemprop='datePublished').text.strip()
        print(datum)
        
        
        
        
        #f.writerow([podatki]) #v podatke daš stvari kot so v head, pomagaj si z
                                    #https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-with-beautiful-soup-and-python-3

    else:
        webpage_text = "Unable"

