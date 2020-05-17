import sqlalchemy as sa
from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship

from framework.database import ModelBase


class Museum(ModelBase):
    __tablename__ = "museum"

    museum_id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(length=255), nullable=False)
    page_link = sa.Column(sa.String(length=255))
    city_id = sa.Column(sa.Integer, sa.ForeignKey('city.city_id', name='FK_museum_city'), nullable=False)
    visitors_per_year = sa.Column(sa.Integer)

    city = relationship('City')

    def __repr__(self):
        return f"{self.name} in {self.city}, with {self.visitors_per_year} visitors per year"

Index("museum_index_city_id", Museum.city_id)