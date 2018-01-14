from django.contrib.auth import get_user_model

import random
import string

User = get_user_model()

def generate_random_password():
    N = random.randint(7, 30)
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=N))
