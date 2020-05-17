from collections import defaultdict

from app.models import City, Museum
from framework.database import SessionFactory

from bs4 import BeautifulSoup

from collections import namedtuple
import csv
import requests

CsvCity = namedtuple('City', ['name', 'country', 'country_code', 'population'])
top_museums_page_name = "List_of_most_visited_museums"

# I couldnt find a way in the Wikipedia API to parse templates (like the infobox on the right of a City page, listing demographics info) the same way you can parse sections and tables
# However the "edit" page provides a decently consistent way to extract the data since it fills up those templates with key-value pairs.
# There are a few issues to handle such as Vatican because it uses a different template due to being a special case of a city-country.
# These are the delimiters that allow locating the population key-value in the editor's text box
wikipedia_edit_population_delimiters = [
    ['population_total', '|'],
    ['population_estimate', '{'],
    ['population_urban', '('],
]


def import_data():
    session = SessionFactory()
    if session.query(Museum).count() != 0:
        raise Exception("Database already has data, please issue a delete_data command first")

    db_cities = defaultdict(dict)
    csv_cities = defaultdict(dict)

    # Most cities will come from this data source, but for those that aren't in there (it's a limited free sample, or names might not match), we will use Wikipedia scraping
    with open("app/datasets/worldcities.csv", encoding="utf8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row['population'].strip() != "":
                population_cleaned = int(row['population'].split('.')[0])  # some rows have their population ending with ".0"
                city = CsvCity(row['city'], row['country'], row['iso2'] , population_cleaned)
                csv_cities[city.name][row['country']] = city


    museums_page = requests.get(f"https://en.wikipedia.org/w/api.php?action=parse&prop=sections&page={top_museums_page_name}&format=json").json()
    top_museums_section = [x for x in museums_page['parse']['sections'] if x['anchor'] == 'List'][0]
    top_museums = requests.get(f"https://en.wikipedia.org/w/api.php?action=parse&page={top_museums_page_name}&section={top_museums_section['index']}&prop=text&format=json").json()
    top_museums_soup = BeautifulSoup(top_museums['parse']['text']['*'], 'html.parser')

    # TODO run this in parallel with threads or an event loop
    # Parse the table of Most Visited Museums, which has 4 columns: Museum Name, Country + City, Visitors per year, and Year reported
    for row in top_museums_soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 3:
            museum_name = cells[0].text.strip()
            city_name = cells[1].text.strip()
            city_link = cells[1].find_all('a')[-1].get('href').strip()
            country_name = cells[1].a.get('title')
            visitors_per_year = int(cells[2].text.replace(',', ''))
            museum_link = cells[0].a.get('href').strip()
            if 'redlink=1' in museum_link:
                museum_link = None

            # Reuse previously-created city if available
            city = db_cities.get(city_name, {}).get(country_name, None)
            if city is None:
                population = -1

                # Fetch city from local csv datasource if available
                city_from_csv = csv_cities.get(city_name, {}).get(country_name, None)
                if city_from_csv is not None:
                    population = city_from_csv.population
                else:
                    # Fetch city from Wikipedia's Edit page
                    city_html_edit = requests.get(f"https://en.wikipedia.org/w/index.php?title={city_link.replace('/wiki/', '')}&action=edit")
                    city_soup = BeautifulSoup(city_html_edit.text, 'html.parser')
                    editor_box_text = city_soup.find(id='wpTextbox1').text

                    population = parse_editor_box_text_for_population(editor_box_text, city_name)

                    # Abandonned attempt to use this API because it lacks population data for many cities
                    # city_json = requests.get(f"https://public.opendatasoft.com/api/records/1.0/search/?dataset=worldcitiespop&q=city%3D{city_name}&sort=population").json()
                    # if len(city_json['records']) == 0:
                    #     raise Exception(f"No city found with name {city_name}")
                    # population = city_json['records'][0]['fields']['population']

                # Create a Database City and track it for reuse
                city = City(name=city_name, country_name=country_name, page_link=city_link, population=population)
                session.add(city)
                db_cities[city.name][city.country_name] = city

            # Create a Database Museum
            museum = Museum(name=museum_name, page_link=museum_link, city=city, visitors_per_year=visitors_per_year)
            session.add(museum)
            print(museum)

    session.commit()


def delete_data():
    session = SessionFactory()
    session.query(Museum).delete()
    session.query(City).delete()
    session.commit()


def parse_editor_box_text_for_population(editor_box_text, city_name):
    # Seek the various delimiters that help us locate the population field, trying to parse the captured value until we find one that works.
    for delimiter_start, delimiter_end in wikipedia_edit_population_delimiters:
        if delimiter_start in editor_box_text:
            try:
                population_split = editor_box_text.split(delimiter_start)[1].split('=')[1].split(delimiter_end)[
                    0].strip().replace(',', '')
                return int(population_split)
            except:
                pass

    raise RuntimeError(f"Unable to get population for city {city_name}")
