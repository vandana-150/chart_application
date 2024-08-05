from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, make_password(password), **extra_fields)


class MyValidator(UnicodeUsernameValidator):
    """
    Custom username validator to accept spaces in the username
    """

    regex = r"^[\w.@+\- ]+$"


class User(AbstractUser):
    """
    Custom user model that extends Django's built-in `AbstractUser` model.

    Fields:
        username (CharField): Unique username field with a max length of 64 characters.
        email (EmailField): Unique email field with a max length of 320 characters.
        created_at (DateTimeField): DateTime field when the object is created.
        updated_at (DateTimeField): DateTime field that automatically updates on save.

    Uses a custom manager called `CustomUserManager`.

    The `__str__()` method returns the username of the user instance.

    The `USERNAME_FIELD` is set to "email", making email the unique identifier for authentication.
    The `REQUIRED_FIELDS` is set to ["username"], making username a required field during user creation.
    """

    username_validator = MyValidator()
    username = models.CharField(
        ("username"),
        max_length=64,
        help_text=(
            "Required. 64 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
    )
    email = models.EmailField(unique=True, null=True, max_length=320)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(User, self).save(*args, **kwargs)


class Group(models.Model):
    host =models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    participants = models.ManyToManyField(User,related_name='participants',blank=True)
    updated = models.DateTimeField(auto_now=True)#will be updated always when ever there is a change
    created = models.DateTimeField(auto_now_add=True)#now_add will only be created at the time of creation

    class Meta:
        ordering =['-updated','-created']#-makes the order desc of those fields

    
    def __str__(self):
        return self.name


class Message(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    updated = models.DateTimeField(auto_now=True)#will be updated always when ever there is a change
    created = models.DateTimeField(auto_now_add=True)#now_add will only be created at the time of creation
    # likes = models.ManyToManyField(User, related_name='liked_messages', blank=True)

    class Meta:
        ordering =['-updated','-created']#-makes the order desc of those fields

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
