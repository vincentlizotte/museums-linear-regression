import sqlalchemy as sa

from framework.database import ModelBase


class City(ModelBase):
    __tablename__ = "city"

    city_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(length=255), nullable=False)
    country_name = sa.Column(sa.String(length=255), nullable=False)
    page_link = sa.Column(sa.String(length=255), nullable=False)
    population = sa.Column(sa.Integer)

    def __repr__(self):
        return f"{self.name} {self.country_name}, population {self.population}"
