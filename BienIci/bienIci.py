import os
import json
from threading import local
import time
import re

from bs4 import BeautifulSoup
from selenium import webdriver

localisation=input("Entrez la localisation : ")
projet=input("Entrez votre projet (achat/location) : ")
if(projet == 'achat'):
    prixMax=input("Entrez le prix d'achat maximum : ")
else:
    prixMax=input("Entrez le loyer maximum : ")

typedebien=input("Type de bien à louer (Appartement/maisonvilla) : ")


listLogement = []

file= open("main.html", "w")
file.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <title>Python Parsing</title>
</head>
<body>''')

def get_pages(count=1, headless=False):

    driver = webdriver.Chrome()
    pages = []

    for page_nb in range(1, count + 1):
        page_url = f"https://www.bienici.com/recherche/{projet}/{localisation}/{typedebien}?prix-max={prixMax}&page={page_nb}"
        driver.get(page_url)
        time.sleep(20)
        pages.append(driver.page_source.encode("utf-8"))
    return pages

def save_pages(pages):
    os.makedirs("data", exist_ok=True)
    for page_nb, page in enumerate(pages):
        with open(f"data/page_{page_nb}.html", "wb") as f_out:
            f_out.write(page)

def clean_surface(tag):
    text = tag.text.strip()
    match = re.search("[0-9]{2,}", text)
    return match.group()

def clean_postal_code(tag):
    text = tag.text.strip()
    match = re.search("[0-9]{5}", text)
    return match.group()

def clean_rooms(tag):
    text = tag.text.strip()
    match = re.search(" [0-9]{1}", text)
    return match.group()

def clean_city(tag):
    text = tag.text.strip()
    match = re.search("(?:^|(?:[.!?]\s))(\w+)", text)
    return match.group()

def clean_type(tag):
    text = tag.text.strip()
    match = re.search("(?:^|(?:[.!?]\s))(\w+)", text)
    return match.group()

def main():
    pages = get_pages()
    save_pages(pages)

if __name__ == "__main__":
    main()


pages_paths = os.listdir("data")
for page_path in pages_paths :
    with open(os.path.join("data", page_path), "rb") as f_in:
        page = f_in.read().decode("utf-8")

soup = BeautifulSoup(page, "html.parser")
results = soup.find_all("div", class_="detailsContainer")
file.write(f'''
<div class="card">
    <table class="table">
        <thead class="thead-dark">
            <tr>
            <th scope="col">Type de logement</th>
            <th scope="col">Loyer</th>
            <th scope="col">Surface m²</th>
            <th scope="col">Ville</th>
            <th scope="col">Code Postal</th>
            <th scope="col">Nombre de pièces</th>
            <th scope="col">Photo Annonce</th>
            </tr>
        </thead>
        <tbody>


''')
id=0
for result in results:
    id+=1

    loyer = result.find("span", class_="thePrice")
    surface = clean_surface(result.find("span", class_="generatedTitleWithHighlight"))
    localisation = clean_postal_code(result.find("div", class_="cityAndDistrict"))
    type =  clean_type(result.find("span", class_="generatedTitleWithHighlight"))
    nb_pieces =  clean_rooms(result.find("span", class_="generatedTitleWithHighlight"))
    ville = clean_city(result.find("div", class_="cityAndDistrict"))
    photo = result.find("img", class_="searchItemPhoto")
    photoImg = photo.attrs['src']

    listLogement.append({'id': id, 'type': type, 'loyer': loyer.text, 'surface': surface, "ville": ville, "localisation": localisation, "nb_pieces": nb_pieces})

    file.write(f'''

                <tr>
                    <td>{type}</td>
                    <td>{loyer.text}</td>
                    <td>{surface}</td>
                    <td>{ville}</td>
                    <td>{localisation}</td>
                    <td>{nb_pieces}</td>
                    <td><img src='{photoImg}'></td>
                </tr>

    ''')

d = {"listLogement" : listLogement}
json.dump(d, open("db.json","w"))

file.write('''

</tbody>
</table>
</div>
</body>
</html>''')