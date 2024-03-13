from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class CustomAccountManager(BaseUserManager):
    """Class for creating and managing user accounts directly."""
    def create_superuser(self, email, full_name, password, **other_fields):
        """Function to create superusers directly."""
        # Ensures the superuser has necessary permissions set.
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_moderator', True)

        # Validates superuser permissions.
        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        # Uses the create_user method to create a superuser.
        return self.create_user(email, full_name, password, **other_fields)
    
    def create_user(self, email, full_name, password, **other_fields):
        """Function to create regular users directly."""
        # Validates that an email address is provided.
        if not email:
            raise ValueError(('You must provide an email address'))
        
        # Creates a new user instance.
        email = self.normalize_email(email)
        user = self.model(email=email,
                          full_name=full_name, **other_fields)
        user.set_password(password)
        user.save()
        return user

class AllUsers(AbstractBaseUser, PermissionsMixin):
    """Class to create the required users table in the database."""
    email=models.EmailField(unique=True)
    full_name=models.CharField(max_length=255)
    is_staff=models.BooleanField(default=False) # Checks the user can access the admin panel.
    is_active=models.BooleanField(default=True) # Allows user accounts to be blocked.
    is_moderator=models.BooleanField(default=False) # Checks if the user is a moderator.
    start_at=models.DateTimeField(default=timezone.now) # Sets the time when the user made their account. 
    objects=CustomAccountManager()  # Links to Custom Account Manage Class.
    
    USERNAME_FIELD='email'  # Uses email as the unique identifier for authentication.
    REQUIRED_FIELDS=['full_name']   # Required fields other than USERNAME_FIELD and password.

    def is_user_moderator(self):
        """Function to check if the user is a moderator."""
        return self.is_moderator
    
    def get_id(self):
        """Function to return the user's id."""
        return self.id