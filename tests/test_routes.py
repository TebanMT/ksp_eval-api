"""
Employed API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest import TestCase
from unittest.mock import patch
from tests.factories import EmployedFactory, BeneficiaryFactory, Beneficiary
from service.common import status  # HTTP Status Codes
from service.models import db, Employed, init_db
from service.routes import app, util
from service import talisman

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)

BASE_URL = "/employe"
HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}


######################################################################
#  T E S T   C A S E S
#####################################################################
class TestEmployedService(TestCase):
    """Employed Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)
        talisman.force_https = False

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Beneficiary).delete()  # clean up the last tests
        db.session.query(Employed).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_employes(self, count):
        """Factory method to create employes in bulk"""
        employes = []
        for _ in range(count):
            employe = EmployedFactory()
            beneficiary = BeneficiaryFactory()
            data = {"employe":employe.serialize(), "beneficiary":[beneficiary.serialize()]}
            response = self.client.post(BASE_URL, json=data)
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Employed",
            )
            new_employe = response.get_json()
            employe.id = new_employe["id"]
            employes.append(employe)
        return employes

    ######################################################################
    #  EMPLOYES   T E S T   C A S E S
    ######################################################################

    def test_index(self):
        """It should get 200_OK from the Home Page"""
        response = self.client.get("/", environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-XSS-Protection': '1; mode=block',
            'X-Content-Type-Options': 'nosniff',
            'Content-Security-Policy': 'default-src \'self\' localhost',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        for key, value in headers.items():
            self.assertEqual(response.headers.get(key), value)

    def test_health(self):
        """It should be healthy"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    @patch('service.common.util.upload_img')
    def test_create_an_employe(self, mock_upload_img):
        """It should Create a new employe"""
        mock_upload_img.return_value = ""
        employe = EmployedFactory()
        beneficiary = BeneficiaryFactory(employed_id=employe.id)
        data = {"employe":employe.serialize(), "beneficiary":[beneficiary.serialize()]}
        #print(data)
        response = self.client.post(
            BASE_URL,
            json=data,
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(repr(employe),"<Employe {} id=[{}]>".format(employe.name,employe.id))

       # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_account = response.get_json()
        self.assertEqual(new_account["name"], employe.name)
        self.assertEqual(new_account["job_position"], employe.job_position)
        self.assertEqual(new_account["status"], employe.status)
        self.assertEqual(new_account["date_hire"], str(employe.date_hire))

    def test_bad_request(self):
        """It should not Create an Employe when sending the wrong data"""
        response = self.client.post(BASE_URL, json={"name": "not enough data"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create an Employe when sending the wrong media type"""
        employe = EmployedFactory()
        data = {"employe":employe.serialize(), "beneficiary":[]}
        response = self.client.post(
            BASE_URL,
            json=data,
            content_type="test/html"
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    @patch('service.common.util.upload_img')
    def test_read_an_employe(self, mock_upload_img):
        "It should read a single employe from the database"
        mock_upload_img.return_value = ""
        employe = self._create_employes(1)[0]
        route = BASE_URL+"/{}".format(employe.id)
        resp = self.client.get(route, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        employe_readed = resp.get_json()
        self.assertEqual(employe_readed['id'], employe.id)
        self.assertEqual(employe_readed["name"], employe.name)

    def test_get_employe_not_found(self):
        "It should not find an employe from the database"
        route = BASE_URL+"/{}".format(0)
        resp = self.client.get(route, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.get_json()["message"], "404 Not Found: Employe [0] not found")

    @patch('service.common.util.upload_img')
    def test_update_employe(self, mock_upload_img):
        """It should Update an existing employe"""
        # create an employe to update
        mock_upload_img.return_value = ""
        test_employe = EmployedFactory()
        data = {"employe":test_employe.serialize(), "beneficiary":[]}
        resp = self.client.post(BASE_URL, json=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the employe
        new_employe = resp.get_json()
        new_employe["name"] = "Something Known"
        resp = self.client.put(f"{BASE_URL}/{new_employe['id']}", json=new_employe)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_employe = resp.get_json()
        self.assertEqual(updated_employe["name"], "Something Known")
        self.assertEqual(updated_employe["id"], updated_employe["id"])

    @patch('service.common.util.upload_img')
    def test_update_account_not_found(self, mock_upload_img):
        "It should not update an employe"
        # create an employe to update
        mock_upload_img.return_value = ""
        test_employe = EmployedFactory()
        data = {"employe":test_employe.serialize(), "beneficiary":[]}
        resp = self.client.post(BASE_URL, json=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the employe that not exist
        new_employe = resp.get_json()
        new_employe["name"] = "Something Known"
        resp = self.client.put(f"{BASE_URL}/0", json=new_employe)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(resp.get_json()["message"], "404 Not Found: Employe [0] not found")

    @patch('service.common.util.upload_img')
    def test_list_all_accounts(self, mock_upload_img):
        """It should return all the accounts in the database"""
        mock_upload_img.return_value = ""
        self._create_employes(10)
        resp = self.client.get(f"{BASE_URL}", content_type="application/json")
        accounts = resp.get_json()
        self.assertEqual(len(accounts),10)

    def test_list_all_accounts_not_found(self):
        """It should not list any accounts"""
        resp = self.client.get(f"{BASE_URL}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    @patch('service.common.util.upload_img')
    def test_delete_an_account(self, mock_upload_img):
        """It should delete an employe"""
        # create an employe to delete
        mock_upload_img.return_value = ""
        employe = self._create_employes(1)[0]
        # verify the employe was created successfully
        resp = self.client.get(f"{BASE_URL}/{employe.id}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        # Delete the employe
        resp = self.client.delete(f"{BASE_URL}/{employe.id}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        # verify the employe was deleted by try to read the employe again
        resp = self.client.get(f"{BASE_URL}/{employe.id}", content_type="application/json")
        updated_employe = resp.get_json()
        self.assertEqual(updated_employe["status"], "false")

    def test_delete_an_account_not_found(self):
        """It should not delete an account that doesn't exist"""
        resp = self.client.delete(f"{BASE_URL}/{1}", content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.delete(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_internal_server_error(self):
        """It should response 500 for internal server errors"""
        resp = self.client.get("/error")
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_cors_security(self):
        """It should return a CORS header"""
        response = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check for the CORS header
        self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), '*')
