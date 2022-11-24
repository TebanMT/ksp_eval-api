"""
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory.fuzzy import FuzzyDate
from service.models import Employed, Beneficiary
from faker import Faker
from faker.providers import DynamicProvider

job_position_provider = DynamicProvider(
     provider_name="job_position",
     elements=["desarrollador", "HR", "CEO", "Mantenimiento", "Otro"],
)

status_provider = DynamicProvider(
     provider_name="status",
     elements=["true", "false"],
)

relationship_provider = DynamicProvider(
     provider_name="relationship",
     elements=["Padre", "Madre", "Hijo", "Amigo", "Hermano"],
)

gender_provider = DynamicProvider(
     provider_name="gender",
     elements=["Hombre", "Mujer", "No binario", "Otro"],
)
photo_provider = DynamicProvider(
     provider_name="photo",
     elements=["data:image/png;base64,iVBORw0KGgoAA"],
)


fake = Faker()
fake.add_provider(job_position_provider)
fake.add_provider(status_provider)
fake.add_provider(relationship_provider)
fake.add_provider(gender_provider)
fake.add_provider(photo_provider)


class EmployedFactory(factory.Factory):
    """Creates fake Employes"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class for factory"""
        model = Employed

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    job_position = fake.job_position()
    salary = fake.pyfloat(min_value=1000.00, max_value=1000000.00)
    status = fake.status()
    photo = fake.photo()
    date_hire = FuzzyDate(date(2008, 1, 1))

class BeneficiaryFactory(factory.Factory):
    """Creates fake Beneficiaries"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class for factory"""
        model = Beneficiary

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    relationship = fake.relationship()
    gender = fake.gender()
    date_born =  FuzzyDate(date(2008, 1, 1))
    employed_id = factory.Sequence(lambda n: n)