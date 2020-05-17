from app.models import Museum
from framework.database import SessionFactory

import csv
import io


def get_data_csv():
    session = SessionFactory()
    museums = session.query(Museum).all()

    with io.StringIO() as output:
        writer = csv.writer(output, delimiter=',')
        writer.writerow(["museum_name", "visitors_per_year", "city_name", "country_name", "population"])
        for museum in museums:
            writer.writerow([museum.name, museum.visitors_per_year, museum.city.name, museum.city.country_name, museum.city.population])
        output.seek(0)
        result = output.read()

    return result