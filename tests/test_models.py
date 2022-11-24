"""
Test cases for Employed Model

"""
import logging
import unittest
import os
from service import app
from service.models import Employed, DataValidationError, db, Beneficiary
from tests.factories import EmployedFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  Employed   M O D E L   T E S T   C A S E S
######################################################################
class TestEmployed(unittest.TestCase):
    """Test Cases for Employed Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Employed.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Beneficiary).delete() 
        db.session.query(Employed).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_employe(self):
        """It should Create an Employe and assert that it exists"""
        fake_account = EmployedFactory()
        # pylint: disable=unexpected-keyword-arg
        employe = Employed(
            name=fake_account.name,
            job_position=fake_account.job_position,
            salary=fake_account.salary,
            status=fake_account.status,
            date_hire=fake_account.date_hire,
        )
        self.assertIsNotNone(employe)
        self.assertEqual(employe.id, None)
        self.assertEqual(employe.name, fake_account.name)
        self.assertEqual(employe.job_position, fake_account.job_position)
        self.assertEqual(employe.salary, fake_account.salary)
        self.assertEqual(employe.status, fake_account.status)
        self.assertEqual(employe.date_hire, fake_account.date_hire)

    def test_add_a_employe(self):
        """It should Create an employe and add it to the database"""
        employes = Employed.all()
        self.assertEqual(employes, [])
        employe = EmployedFactory()
        employe.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(employe.id)
        employes = Employed.all()
        self.assertEqual(len(employes), 1)

    def test_read_employe(self):
        """It should Read an employe"""
        employe = Employed()
        employe.create()

        # Read it back
        found_employe = Employed.find(employe.id)
        self.assertEqual(found_employe.id, employe.id)
        self.assertEqual(found_employe.name, employe.name)
        self.assertEqual(found_employe.job_position, employe.job_position)
        self.assertEqual(found_employe.salary, employe.salary)
        self.assertEqual(found_employe.status, employe.status)
        self.assertEqual(found_employe.date_hire, employe.date_hire)

    def test_update_employe(self):
        """It should Update an employe"""
        employe = EmployedFactory(salary=100.00)
        employe.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(employe.id)
        self.assertEqual(employe.salary, 100.00)

        # Fetch it back
        employe = Employed.find(employe.id)
        employe.salary = 200.00
        employe.update()

        # Fetch it back again
        employe = Employed.find(employe.id)
        self.assertEqual(employe.salary, 200.00)

    def test_delete_an_employe(self):
        """It should Delete an employe from the database (logical deletion)"""
        employe = EmployedFactory(status="true")
        employe.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(employe.id)
        self.assertEqual(employe.status, "true")

        # Fetch it back
        employe = Employed.find(employe.id)
        employe.status = False
        employe.update()

        # Fetch it back again
        employe = Employed.find(employe.id)
        self.assertEqual(employe.status, "false")

    def test_list_all_employes(self):
        """It should List all employes in the database"""
        employes = Employed.all()
        self.assertEqual(employes, [])
        for employe in EmployedFactory.create_batch(5):
            employe.create()
        # Assert that there are not 5 accounts in the database
        employes = Employed.all()
        self.assertEqual(len(employes), 5)

    def test_serialize_an_employe(self):
        """It should Serialize an employe"""
        employe = EmployedFactory()
        serial_employe = employe.serialize()
        self.assertEqual(serial_employe["id"], employe.id)
        self.assertEqual(serial_employe["name"], employe.name)
        self.assertEqual(serial_employe["job_position"], employe.job_position)
        self.assertEqual(serial_employe["salary"], employe.salary)
        self.assertEqual(serial_employe["status"], employe.status)
        self.assertEqual(serial_employe["date_hire"], str(employe.date_hire))

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an employe with a KeyError"""
        employe = Employed()
        self.assertRaises(DataValidationError, employe.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an employe with a TypeError"""
        employe = Employed()
        self.assertRaises(DataValidationError, employe.deserialize, [])
