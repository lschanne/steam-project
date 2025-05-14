import datetime
from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    create_engine,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.mysql import FLOAT, LONGTEXT
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session,
)
from typing_extensions import Annotated

DATABASE = "steam_project"
HOST = "localhost"
USER = "user"

bigint = Annotated[int, "bigint"]

class Base(DeclarativeBase):
    type_annotation_map = {
        str: LONGTEXT(),
        bigint: BigInteger(),
    } 

class Game(Base):
    __tablename__ = "games"

    appid: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    description_snippet = Column("description_snippet", LONGTEXT(), nullable=True)
    release_date = Column("release_date", Date(), nullable=True)
    coming_soon: Mapped[bool]
    price = Column("price", FLOAT(scale=2), nullable=True)
    description = Column("description", LONGTEXT(), nullable=True)
    all_positive_review_pct = Column("all_positive_review_pct", BigInteger(), nullable=True)
    total_num_reviews = Column("total_num_reviews", BigInteger(), nullable=True)
    recent_positive_review_pct = Column("recent_positive_review_pct", BigInteger(), nullable=True)
    recent_num_reviews = Column("recent_num_reviews", BigInteger(), nullable=True)
    
    def __repr__(self):
        return f"Game(appid={self.appid!r}, name={self.name!r})"

class Company(Base):
    """
    There is a lot of overlap between developers and publishers in gaming. Not
    exactly sure what to call the union of the two.
    """
    __tablename__ = "companies"

    company_id: Mapped[int] = mapped_column(primary_key=True)
    company: Mapped[str]
    is_developer: Mapped[bool]
    is_publisher: Mapped[bool]

    def __repr__(self):
        return f"Company(company_id={self.company_id!r}, company={self.company!r})"

class Developer(Base):
    __tablename__ = "developers"

    developer_id: Mapped[int] = mapped_column(primary_key=True)
    appid: Mapped[int] = mapped_column(ForeignKey("games.appid"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.company_id"))

    def __repr__(self):
        return f"Developer(developer_id={self.developer_id}, appid={self.appid!r}, company_id={self.company_id!r})"
 
class Publisher(Base):
    __tablename__ = "publishers"

    publisher_id: Mapped[int] = mapped_column(primary_key=True)
    appid: Mapped[int] = mapped_column(ForeignKey("games.appid"))
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.company_id"))

    def __repr__(self):
        return f"Publisher(publisher_id={self.publisher_id}, appid={self.appid!r}, company_id={self.company_id!r})"
       
class GameTagEnumeration(Base):
    __tablename__ = "game_tag_enumerations"

    game_tag_enumeration_id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str]

    def __repr__(self):
        return f"GameTagEnumeration(game_tag_enumeration_id={self.game_tag_enumeration_id!r}, tag={self.tag!r})"

class GameTag(Base):
    __tablename__ = "game_tags"

    game_tag_id: Mapped[int] = mapped_column(primary_key=True)
    appid: Mapped[int] = mapped_column(ForeignKey("games.appid"))
    game_tag_enumeration_id: Mapped[int] = mapped_column(ForeignKey("game_tag_enumerations.game_tag_enumeration_id"))

    def __repr__(self):
        return f"GameTag(game_tag_id={self.game_tag_id!r}, appid={self.appid!r}, game_tag_enumeration_id={self.game_tag_enumeration_id!r})"

class FeatureEnumeration(Base):
    __tablename__ = "feature_enumerations"

    feature_enumeration_id: Mapped[int] = mapped_column(primary_key=True)
    feature: Mapped[str]

    def __repr__(self):
        return f"FeatureEnumeration(feature_enumeration_id={self.feature_enumeration_id!r}, feature={self.feature!r})"

class GameFeature(Base):
    __tablename__ = "game_features"

    game_feature_id: Mapped[int] = mapped_column(primary_key=True)
    appid: Mapped[int] = mapped_column(ForeignKey("games.appid"))
    feature_enumeration_id: Mapped[int] = mapped_column(ForeignKey("feature_enumerations.feature_enumeration_id"))

    def __repr__(self):
        return f"GameFeature(game_feature_id={self.game_feature_id!r}, appid={self.appid!r}, feature_enumeration_id={self.feature_enumeration_id!r})"

class Author(Base):
    __tablename__ = "authors"

    author_id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str]

    def __repr__(self):
        return f"Author(author_id={self.author_id}, author={self.author!r})"

class Feedlabel(Base):
    __tablename__ = "feedlabels"

    feedlabel_id: Mapped[int] = mapped_column(primary_key=True)
    feedlabel: Mapped[str]

    def __repr__(self):
        return f"Feedlabel(feedlabel_id={self.feedlabel_id}, feedlabel={self.feedlabel!r})"

class Feedname(Base):
    __tablename__ = "feednames"

    feedname_id: Mapped[int] = mapped_column(primary_key=True)
    feedname: Mapped[str]

    def __repr__(self):
        return f"Feedname(feedname_id={self.feedname_id}, feedname={self.feedname!r})"

class Newsitem(Base):
    __tablename__ = "newsitems"

    gid: Mapped[bigint] = mapped_column(primary_key=True)
    title: Mapped[str]
    url: Mapped[str]
    is_external_url: Mapped[bool]
    author_id: Mapped[str] = mapped_column(ForeignKey("authors.author_id"), nullable=True)
    contents: Mapped[str]
    feedlabel_id: Mapped[str] = mapped_column(ForeignKey("feedlabels.feedlabel_id"), nullable=True)
    date: Mapped[datetime.date]
    feedname_id: Mapped[str] = mapped_column(ForeignKey("feednames.feedname_id"), nullable=True)
    feed_type: Mapped[int]
    appid: Mapped[int] = mapped_column(ForeignKey("games.appid"))

    def __repr__(self) -> str:
        return f"Newsitems(gid={self.gid!r}, title={self.title!r})"

class NewsitemTagEnumeration(Base):
    __tablename__ = "newsitem_tag_enumerations"

    newsitem_tag_enumeration_id: Mapped[int] = mapped_column(primary_key=True)
    tag: Mapped[str]

    def __repr__(self):
        return f"NewsitemTagEnumeration(newsitem_tag_enumeration_id={self.newsitem_tag_enumeration_id!r}, tag={self.tag!r})"

class NewsitemTags(Base):
    __tablename__ = "newsitem_tags"

    newsitem_tag_id: Mapped[int] = mapped_column(primary_key=True)
    gid: Mapped[bigint] = mapped_column(ForeignKey("newsitems.gid"))
    newsitem_tag_enumeration_id: Mapped[int] = mapped_column(ForeignKey("newsitem_tag_enumerations.newsitem_tag_enumeration_id"))

    def __repr__(self):
        return f"NewsitemTags(newsitem_tag_id={self.newsitem_tag_id!r}, gid={self.gid!r}, newsitem_tag_enumeration_id={self.newsitem_tag_enumeration_id!r})"

def get_engine(database=DATABASE):
    url = f"mysql+mysqlconnector://{USER}@{HOST}"
    if database:
        url += f"/{DATABASE}"
    return create_engine(url)

def get_session(database=DATABASE):
    return Session(get_engine(database=database))

def create_all():
    engine = get_engine(database=None)
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {DATABASE}"))
        conn.commit()
        conn.execute(text(f"CREATE DATABASE {DATABASE}"))
        conn.commit()
    Base.metadata.create_all(get_engine())
