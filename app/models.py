"""

===========
Data Models
===========

This module contains the model-level logic, built on SQLAlchemy.

"""

from app import database
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Table, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, backref


class Base(object):
    """This is a customized version of SQLAlchemy's Base object.

    It serves to abstract away some of the SQL language and logic to add more
    of a object-oriented style to the models. The language used still mimics
    SQLAlchemy, to avoid confusion.  It also has default configurations that
    apply to all models.

    """

    # Instantiate class variable for environment. Default to dev
    environment = 'dev'

    @declared_attr
    def __tablename__(cls):
        """Define the table name.

        By default, it is the pluraized lower case version of the class name

        """

        # Set table name to be lower case of class name
        return cls.__name__.lower()

    # Define the primary key
    id = Column(Integer, primary_key=True)

    def save(self):
        """Commits this model instance to the database.

        TODO: should return either True or False depending on its success.
        TODO: manage sequential saves better.

        """
        database[Base.environment].add(self)
        database[Base.environment].commit()

    @classmethod
    def get(cls, id):
        """Look up a single instance based on its primary key.

        The method name is borrowed from Django.

        TODO: should throw an error if not found.

        Args:
          id (int): the primary key of the record.

        Returns:
          An instance of the model, if the record is found.

          Raises an error if not found.

        """
        return database[Base.environment].query(cls).filter(cls.id==id).first()

    @classmethod
    def all(cls):
        """Get all records for this model.

        Returns:
          Query object containing all records in the table for this model.

        """
        return database[Base.environment].query(cls)

    # Criteria-based look-up; see SQLAlchemy docs for use
    @classmethod
    def filter(cls, criteria):
        """Query this model's table based on a criteria.

        See the ORM documentation for SQLAlchemy for the different operators
        that can be used in the criteria parameter.

        Args:
          criteria: an SQLAlchemy-style criteria.

        Returns:
          Query object containing the matching records.

        """
        return database[Base.environment].query(cls).filter(criteria)

# Set the above Base class as the default model.
Base = declarative_base(cls=Base)

"""
######
Models
######
"""

class Unit(Base):
    """A model representing a unit (or segment) of text.

    This can be either a full document, a section or chapter of a document,
    an act in a play, or anything that is made of sentences.

    Units are hierarchical; one unit can contain many children units.

    Attributes:
      unit_type (str): the unit type (document, section, etc.).
      number (int): a sequencing number (e.g. 2 for chapter 2).
      parent_id (int): a link to the parent unit.

    Relationships:
      belongs to: parent (Unit)
      has many: children (Unit), sentences, properties

    TODO: implement relationships

    """

    unit_type = Column(String(64), index = True)
    number = Column(Integer, index = True)
    parent_id = Column(Integer, ForeignKey('unit.id'))

    # Relationships

    children = relationship("Unit")

    sentences = relationship("Sentence", backref=backref("unit"))

    properties = relationship("Property", backref=backref("unit"))

    def __init__(self, document=None):
        """Constructor for unit.

        Has a default empty constructor if called without parameters
        """

        if document:
            """Initialize a top-level document unit from a document file.

            Expects a dictionary that has the following entries:
            - properties (dict): the metadata of the document
            - subunits (dict): the structure of the subunits
            - sentences (list): a list of sentences, in order
            - words (set): the set of all words (or tokens)

            This is tentative.

            """

            self.unit_type = "document"
            self.number = 0

            for name, value in document["properties"].items():
                prop = Property()
                prop.name = name
                prop.value = value

                prop.save()
                self.properties.append(prop)

            for sentence_tuple in document["sentences"]:
                words = sentence_tuple[1]
                sentence_text = sentence_tuple[0]

                sentence = Sentence()
                sentence.text = sentence_text

                for word_str in words:
                    word = Word()
                    word.word = word_str
                    word.save()

                    sentence.words.append(word)

                sentence.save()
                self.sentences.append(sentence)

            # TODO: initialize subunits

        self.save

    @property
    def parent(self):
        """Method for getting a unit's parent.

        This method exists because in the current set up, it has been tricky to
        define the parent as a relationship.
        """

        return Unit.get(self.parent_id)

    def __repr__(self):
        """Return a representation of a unit, which is its type followed by its
        ordering number
        """

        return " ".join([self.unit_type, str(self.number)])

class Sentence(Base):
    """A model representing a sentence.

    The sentence model is treated like "leaf" units. It has a link to its
    parent unit. Sentences contain words (the model), and also stores its
    own raw text, for use in search results.

    Attributes:
      unit_id: a link to the unit containing the sentence.
      text: the raw text of the sentence.

    Relationships:
      belongs to: unit
      has many: words

    NOTE: should test sentence reconstruction using the actual word model.

    """

    unit_id = Column(Integer, ForeignKey('unit.id'))
    text = Column(Text, index = True)

    words = relationship("Word",
        secondary="word_in_sentence",
        backref="sentences"
    )

    def __repr__(self):
        return "<Sentence: " + self.text + ">"

class Word(Base):
    """A model representing a word.

    Words are the most basic building blocks of everything.

    Attributes:
      word (str): the word

    Relationships:
      has many: sentences

    """

    word = Column(String, index = True)

    def __repr__(self):
        return "<Word: " + self.word + ">"

class Property(Base):
    """A model representing a property of a unit.

    Metadata about units are stored as properties, which have a link to the
    unit it belongs to. Any form of metadata can be assigned to a unit, making
    them extensible and flexible.

    Attributes:
      unit_id: the primary key of the unit it belongs to
      name: the name of the property
      value: the value of the property

    Relationships:
      belongs to: unit

    """

    # Schema
    unit_id = Column(Integer, ForeignKey('unit.id'))
    name = Column(String, index = True)
    value = Column(String, index = True)

    def __repr__(self):
        return "<Property: " + self.name + ">"

"""
##################
Association Tables
##################
"""

# Many-to-many table between words and sentences
word_in_sentence = Table("word_in_sentence", Base.metadata,
    Column('word_id', Integer, ForeignKey('word.id')),
    Column('sentence_id', Integer, ForeignKey('sentence.id'))
)