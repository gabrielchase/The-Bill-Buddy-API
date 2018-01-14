from mixer.backend.django import mixer
from users.tests.utils import generate_random_password

import pytest


@pytest.fixture
def new_user_info():
    return {
        'first_name': mixer.faker.first_name(),
        'last_name': mixer.faker.last_name(),
        'email': mixer.faker.email(),
        'country': mixer.faker.country(),
        'mobile_number': mixer.faker.phone_number(),
        'password': generate_random_password()
    }

other_new_user_info = new_user_info
