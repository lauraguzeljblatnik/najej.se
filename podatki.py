import requests
import os
import re
import csv

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
    with open(path, 'w') as file_out:
        file_out.write(text)
    return None







#processing data

def read_file_to_string(directory, filename):
    '''This function returns the contents of the file as string'''
    path =os.path.join(directory, filename)
    with open(path, 'r') as file_in:
        return file_in.read

def split_text_to_prod(text):
    pattern = re.compile(
                        r'<span class="trenutno">(?p<ime>.*?)</span></p>'
                        r'.?*'
                        r'<p class="podnaslov" itemprop="description">(?p<opis>.*?)</p>'
                        r'.?*'
                        
                         ,r re.DOTALL)
    listt =[]
    for pat in re.finditer(pattern, text):
        listt += [[pat.group('id'),str(pat.group('name').encode('utf-8')), pat.group('registration'), pat.group('driven_km'), pat.group('motor'), pat.group('price')]]
    return listt



def all_data(url):
    data = []
    for i in range(1,21961):
        text = download_url_to_string(url, i)
        data += split_text_to_prod(text)
    return data



def convert_to_csv(info, head, name):
    with open(ime,'w') as csvFile:
        csvFile.write(head)
        for line in info:
            csvFile.write(','.join(line) + '\n')
    csvFile.close()


head = "Ime, Opis recepta, Uporabnik, Datum, ID recepta, Priložnost, Priprava, Sezona, Vrsta jedi, Zahtevnost, Čas priprave, Ocena, Sestavine, Postopek"

#Klicanje funkcij
data = all_data(recepti_frontpage_url)
convert_to_csv(data,head,csv_filename)

