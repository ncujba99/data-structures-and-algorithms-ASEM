"""The database schema as Python classes. Alembic builds the migrations from them.

countries 1 ── N cities 1 ── N trains 1 ── N train_stops N ── 1 cities

PostgreSQL keeps a B+-tree for every primary key, unique constraint and index declared here;
`GET /api/indexes/` lists them.

Relationships load lazily; each query states what it needs (joinedload, selectinload), so the SQL
it sends stays plain and visible.
"""

from datetime import time

from alembic_utils.pg_extension import PGExtension
from sqlalchemy import CHAR, CheckConstraint, ForeignKey, Identity, MetaData, SmallInteger, Text, UniqueConstraint, func, select
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import DeclarativeBase, Mapped, column_property, mapped_column, relationship

# Constraint and index names follow PostgreSQL's own style (trains_pkey, cities_name_key, ...).
# The API turns these names into messages, see db.py.
NAMING_CONVENTION = {
    "pk": "%(table_name)s_pkey",
    "uq": "%(table_name)s_%(column_0_N_name)s_key",
    "fk": "%(table_name)s_%(column_0_N_name)s_fkey",
    "ix": "%(table_name)s_%(column_0_N_name)s_idx",
    "ck": "%(table_name)s_%(constraint_name)s",
}

# Gives SQL access to the pages of an index; the API reads each tree's height with it.
PAGEINSPECT = PGExtension(schema="public", signature="pageinspect")


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Country(Base):
    __tablename__ = "countries"

    # The ISO 3166 code is short, well known and never changes, so it works as a natural key.
    code: Mapped[str] = mapped_column(CHAR(2), primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)


class City(Base):
    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    # NULL = not known.
    country_code: Mapped[str | None] = mapped_column(ForeignKey(Country.code), index=True)

    country: Mapped[Country | None] = relationship()

    __table_args__ = (CheckConstraint(func.btrim(name.column) != "", name="name_not_blank"),)


class TrainStop(Base):
    """An intermediate station of a train: the many-to-many link between trains and cities, with an order."""
    __tablename__ = "train_stops"

    # Deleting a train deletes its stops in the database itself.
    train_number: Mapped[int] = mapped_column(ForeignKey("trains.number", ondelete="CASCADE"), primary_key=True)
    stop_no: Mapped[int] = mapped_column(SmallInteger, primary_key=True)     # 1, 2, ... in route order
    # A city that is a stop cannot be deleted (no ON DELETE).
    city_id: Mapped[int] = mapped_column(ForeignKey(City.id), index=True)

    city: Mapped[City] = relationship()

    __table_args__ = (
        UniqueConstraint(train_number, city_id),        # a city appears once per route
        CheckConstraint(stop_no.column > 0, name="stop_no_positive"),
    )


class Train(Base):
    """The lab's record. The number is the key field, as in the lab's tree."""
    __tablename__ = "trains"

    # PRIMARY KEY creates the B+-tree trains_pkey, ordered by number.
    number: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    # PostgreSQL does not index foreign keys by itself; index=True adds the tree for "trains to this city".
    destination_id: Mapped[int] = mapped_column(ForeignKey(City.id), index=True)
    # A range of departure times is a range of keys in this tree.
    departure: Mapped[time] = mapped_column(index=True)

    destination: Mapped[City] = relationship()
    # ordering_list numbers the stops 1, 2, ... in list order, so a route is just a list.
    stops: Mapped[list[TrainStop]] = relationship(
        order_by=TrainStop.stop_no,
        collection_class=ordering_list("stop_no", count_from=1),
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    # The cities of the stops, in order: [Бельцы, Киев].
    stop_cities: AssociationProxy[list[City]] = association_proxy(
        "stops", "city", creator=lambda city: TrainStop(city=city),
    )

    __table_args__ = (CheckConstraint(number.column.between(1, 9999), name="number_range"),)


# Counts shown in the city and country lists. Deferred: computed only when a query asks for them.
City.trains_to = column_property(
    select(func.count()).where(Train.destination_id == City.id).correlate_except(Train).scalar_subquery(),
    deferred=True, group="counts",
)
City.trains_via = column_property(
    select(func.count()).where(TrainStop.city_id == City.id).correlate_except(TrainStop).scalar_subquery(),
    deferred=True, group="counts",
)
Country.cities = column_property(
    select(func.count()).where(City.country_code == Country.code).correlate_except(City).scalar_subquery(),
    deferred=True, group="counts",
)
