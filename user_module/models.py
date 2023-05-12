from django.contrib.auth import password_validation
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser



CHOICES_IN_GENDER = [
    ("Male", "Male"),
    ("Female", "Female"),
    ("Unspecified", "Unspecified"),
]

CHOICES_IN_ROLE = [
    ("Admin", "Admin"),
    ("Manager", "Manager"),
    ("Customer", "Customer"),
    ("Cleaner", "Cleaner"),
]

CHOICES_IN_LANGUAGE = [
    ("English", "English"),
    ("French", "French"),
]

CHOICES_IN_COUNTRY = [
    ("United States", "United States"),
    ("Canada", "Canada"),
    ("Other", "Other"),
]

CHOICES_IN_STATUS = [("Active", "Active"), ("Inactive", "Inactive")]


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        :param email: email
        :param password: password
        :param age: age
        :param gender
        :param extra_fields: extra fields
        :return: user
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        UserProfile.objects.create(
            user=user,
            role="Admin",
            first_name="Admin",
            last_name="/",
        )
        return user

    def create_user(self, email, password, **extra_fields):
        """
        Creates and saves a user with the given email and password.
        :param email: email
        :param password: password
        :param extra_fields: extra fields
        :return: user
        """
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields) -> object:
        """
        Creates and saves a superuser with the given email and password.
        :param email: email
        :param password: password
        :param extra_fields: extra fields
        :return: superuser
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    User model for the application with email as the unique identifier instead of username and
    other fields like age.

    """

    use_for_related_fields = True
    username = None
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    access_dashboard = models.BooleanField(default=True)
    booking_account = models.BooleanField(default=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    objects = UserManager()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.password is not None:
            password_validation.password_changed(self.password, self)
            self.password = None


class UserProfile(models.Model):
    """
    User profile model for the application to store the profile data of the user.
    """

    use_for_related_fields = True
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    color = models.CharField(max_length=50, default="#800020")
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="user_in_profile",
        null=True,
        blank=True,
    )
    role = models.CharField(max_length=10, choices=CHOICES_IN_ROLE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(
        max_length=30, choices=CHOICES_IN_GENDER, default="Unspecified"
    )
    language = models.CharField(
        max_length=100, choices=CHOICES_IN_LANGUAGE, default="English"
    )
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(
        max_length=50, choices=CHOICES_IN_COUNTRY, default="United States"
    )
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures", null=True, blank=True
    )
    time_zone = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(
        max_length=100, choices=CHOICES_IN_STATUS, default="Active"
    )
    document = models.FileField(upload_to="cleaner_doc", null=True, blank=True)
    booking_profile = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class VerificationCode(models.Model):
    code = models.CharField(max_length=30)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_in_code')
    is_active = models.BooleanField(default=True)


REVIEW_TYPE = [
    ("Service", "Service"),
    ("Cleaner", "Cleaner")
]


class UserReview(models.Model):
    from booking.models import Service
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_in_review')
    cleaner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cleaner_in_review', null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_in_review', null=True, blank=True)
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
