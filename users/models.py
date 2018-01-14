from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractUser,)


class UserManager(BaseUserManager):

    def create_user(self, first_name, last_name, email, country=None, mobile_number=None, password=None):

        if not email:
            raise ValueError('Users must register an email address')

        if self.model.objects.filter(email=email).first():
            raise ValueError('Email address is already taken')

        new_user = self.model(
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        new_user.set_password(password)
        new_user.set_username()
        new_user.save(using=self._db)

        new_user_details = Details.objects.create(
            user=new_user,
            country=country,
            mobile_number=mobile_number
        )
        new_user_details.save()

        return new_user


class User(AbstractUser):

    email = models.EmailField(max_length=255, unique=True, null=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # removes email from REQUIRED_FIELDS

    def get_full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.username

    def set_username(self):
        instances = User.objects.filter(first_name=self.first_name, last_name=self.last_name).count()
        
        if instances:
            self.username =  '{}{}-{}'.format(self.first_name, self.last_name, instances+1)
        else:
            self.username =  '{}{}'.format(self.first_name, self.last_name)
        
        self.save()

    def __str__(self):
        return self.email


class Details(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    mobile_number = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return str(self.user)