# accounts/models.py (or accounts/managers.py)
from django.contrib.auth.models import AbstractUser, UserManager # Import UserManager
from django.db import models

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

# --- Your CustomUser Model ---
class CustomUser(AbstractUser):
    username = None # This effectively removes the username field
    email = models.EmailField(unique=True, null=False, blank=False)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True,default="profile_images/placeholder.jpg")
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] # These fields will be prompted when creating a superuser

    # Assign your custom manager to the objects attribute
    objects = CustomUserManager() # <--- THIS IS THE KEY CHANGE

    def __str__(self):
        return self.email