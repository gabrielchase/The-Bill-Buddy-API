from rest_framework_jwt.settings import api_settings
from django.contrib.auth import get_user_model

import random
import string

User = get_user_model()

def generate_random_password():
    N = random.randint(7, 30)
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=N))

def get_jwt_header(email):
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    
    user = User.objects.get(email=email)    
    
    if user:
        payload = jwt_payload_handler(user)
        return 'JWT {}'.format(jwt_encode_handler(payload))
    else:
        return False
