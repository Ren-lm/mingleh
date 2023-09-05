from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,AbstractUser
from django.db import models
import uuid
import logging

# The code I wrote starts here

# Setting up the logger for this module
logger = logging.getLogger(__name__)

# Custom user manager for creating and managing custom user instances
class CustomUserManager(BaseUserManager):
    # Method to create and save a regular user
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.username = user.email.split('@')[0]
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Method to create and save a superuser (admin user)
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Custom user model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(max_length=500, blank=True)
    hobbies = models.TextField(max_length=500, blank=True)
    education = models.TextField(max_length=300, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    username = models.CharField(max_length=30, unique=True)
    friends = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return self.username

# Model to represent a status update of a user
class StatusUpdate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]

# Model to represent a post created by a user
class Post(models.Model):
    content = models.TextField(max_length=500)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}"

# Model to represent a friend request between users
class FriendRequest(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='friend_request_from', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='friend_request_to', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

# Model to represent a chat/message between two users
class Chat(models.Model):
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_from')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='chat_to')
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.from_user} to {self.to_user} at {self.create_at}"

# The code I wrote ends here
