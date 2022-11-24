"""
Models for Account

All of the models are stored in this module
"""
import logging
from datetime import date
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Employed.init_db(app)


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    def create(self):
        """
        Creates a Account to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Account to the database
        """
        logger.info("Updating %s", self.name)
        db.session.commit()

    def delete(self):
        """Removes a Account from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  EMPLOYED   M O D E L
######################################################################
class Employed(db.Model, PersistentBase):
    """
    Class that represents an Account
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    job_position = db.Column(db.String(64))
    salary = db.Column(db.Numeric(precision=10, scale=2))
    status =  db.Column(db.String(64))
    date_hire = db.Column(db.Date(), nullable=False, default=date.today())
    # the one-to-may relation
    beneficiary = db.relationship('Beneficiary',cascade="all,delete", backref='employed', lazy=True)

    def __repr__(self):
        return f"<Employe {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Employe into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "job_position": self.job_position,
            "salary": self.salary,
            "status": self.status,
            "date_hire": self.date_hire.isoformat(),
        }

    def deserialize(self, data):
        """
        Deserializes a Employe from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.job_position = data["job_position"]
            self.salary = data["salary"]
            self.status = data.get("status")
            date_hire = data.get("date_hire")
            if date_hire:
                self.date_hire = date.fromisoformat(date_hire)
            else:
                self.date_hire = date.today()
        except KeyError as error:
            raise DataValidationError("Invalid Employe: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Employes with the given name

        Args:
            name (string): the name of the Accounts you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)



######################################################################
#  BENEFICIARY  M O D E L
######################################################################
class Beneficiary(db.Model, PersistentBase):
    """
    Class that represents an Beneficiary
    """

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    relationship = db.Column(db.String(64))
    gender = db.Column(db.String(64))
    date_born = db.Column(db.Date(), nullable=False, default=date.today())
    employed_id = db.Column(db.Integer,  db.ForeignKey('employed.id'),nullable=False)

    def __repr__(self):
        return f"<Beneficiary {self.name} id=[{self.id}]>"

    def serialize(self):
        """Serializes a Beneficiary into a dictionary"""
        return [{
            "id": self.id,
            "name": self.name,
            "relationship": self.relationship,
            "gender": self.gender,
            "date_born": self.date_born.isoformat(),
            "employed_id": self.employed_id
        }]

    def deserialize(self, data):
        """
        Deserializes a Beneficiary from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.relationship = data["relationship"]
            self.gender = data["gender"]
            self.employed_id = data["employed_id"]
            date_born = data.get("date_born")
            if date_born:
                self.date_born = date.fromisoformat(date_born)
            else:
                self.date_born = date.today()
        except KeyError as error:
            raise DataValidationError("Invalid Beneficiary: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Account: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self