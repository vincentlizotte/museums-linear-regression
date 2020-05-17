from app.models import City, Museum
from framework.database import SessionFactory

import requests
from bs4 import BeautifulSoup


def import_data():
    session = SessionFactory()
    if session.query(Museum).count() != 0:
        raise Exception("Database already has data, please issue a delete_data command first")

    cities = {}
    cheating_populations = {
        "Saint Petersburg": 5351935,
        "Madrid": 3223334,
        "Moscow": 12506468,
        "Xi'an": 7135000,
        "Chengdu": 11940500,
        "Melbourne": 5078193,
        "Houston": 2325502,
        "Edinburgh": 488050
    }

    page_name = "List_of_most_visited_museums"
    museums_page = requests.get(f"https://en.wikipedia.org/w/api.php?action=parse&prop=sections&page={page_name}&format=json").json()
    top_museums_section = [x for x in museums_page['parse']['sections'] if x['anchor'] == 'List'][0]

    top_museums = requests.get(f"https://en.wikipedia.org/w/api.php?action=parse&page={page_name}&section={top_museums_section['index']}&prop=text&format=json").json()

    top_museums_soup = BeautifulSoup(top_museums['parse']['text']['*'], 'html.parser')

    # TODO run this in parallel with threads or an event loop, join on the results
    for row in top_museums_soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 3:
            name = cells[0].text.strip()
            city_name = cells[1].text.strip()
            city_link = cells[1].find_all('a')[-1].get('href').strip()
            visitors_per_year = int(cells[2].text.replace(',', ''))
            museum_link = cells[0].a.get('href').strip()
            if 'redlink=1' in museum_link:
                museum_link = None

            city = cities.get(city_name)
            if city is None:
                # I couldnt find a way in the Wikipedia API to parse templates (like the infobox on the right in a cities page, listing demographics info) the same way you can parse sections and tables
                # However the "edit" page provides a surprisingly consistent way to extract the data since it fills up those templates with key-value pairs.
                # The only issue is Vatican because it uses a different template due to being a special case of a city-country
                city_html_edit = requests.get(f"https://en.wikipedia.org/w/index.php?title={city_link.replace('/wiki/', '')}&action=edit")
                city_soup = BeautifulSoup(city_html_edit.text, 'html.parser')
                editor_box = city_soup.find(id='wpTextbox1').text
                population = 0
                try:
                    population_total_split = editor_box.split('population_total')[1].split('=')[1].split('|')[0].strip().replace(',', '')
                    population = int(population_total_split)
                except Exception:
                    try:
                        population_estimate_split = editor_box.split('population_estimate')[1].split('=')[1].split('{')[0].strip().replace(',', '')
                        population = int(population_estimate_split)
                    except Exception as ex:
                        print(f'Unable to get population for {city_name}: {ex}. Used the cheating hardcoded list for now')
                        population = cheating_populations[city_name]

                # Abandonned attempt to use this API because it lacks population data for many cities
                # city_json = requests.get(f"https://public.opendatasoft.com/api/records/1.0/search/?dataset=worldcitiespop&q=city%3D{city_name}&sort=population").json()
                # if len(city_json['records']) == 0:
                #     raise Exception(f"No city found with name {city_name}")
                # population = city_json['records'][0]['fields']['population']

                city = City(name=city_name, page_link=city_link, population=population)
                session.add(city)
                cities[city.name] = city

            museum = Museum(name=name, page_link=museum_link, city=city, visitors_per_year=visitors_per_year)
            session.add(museum)
            print(museum)

    session.commit()


def delete_data():
    session = SessionFactory()
    session.query(Museum).delete()
    session.query(City).delete()
    session.commit()