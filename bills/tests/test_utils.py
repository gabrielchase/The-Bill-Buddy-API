from bills.utils import handle_service_instance
from bills.models import Service

import pytest
pytestmark = pytest.mark.django_db


class TestBillsUtils:

    def test_handle_service_instance(self):
        school_service_1 = handle_service_instance('school')
        assert school_service_1.name == 'School'
        assert school_service_1.id 
        assert Service.objects.count() == 1

        school_service_2 = handle_service_instance('ScHooL')
        assert school_service_2.name == 'School'
        assert school_service_2.id == school_service_1.id 
        assert Service.objects.count() == 1

        work_service = handle_service_instance('WORK')
        assert work_service.name == 'Work'
        assert work_service.id 
        assert Service.objects.count() == 2
