"""Models for the Knowledge Learning application."""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Utilisateur(AbstractUser):
    """Custom user model with role and audit fields.

    This model extends Django's AbstractUser to include additional fields
    for user roles, account activation, and audit tracking.

    Attributes:
        email (str): User's email address (unique).
        role (str): Role of the user ('client' or 'admin').
        is_active (bool): Whether the account is activated.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        created_by (str): Username of the creator.
        updated_by (str): Username of the last updater.
    """
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=[('client', 'Client'), ('admin', 'Admin')], default='client')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='utilisateur_set',
        blank=True,
        help_text='Groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='utilisateur_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def save(self, *args, **kwargs):
        """Set audit fields before saving the user.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.created_by:
            self.created_by = self.username
        self.updated_by = self.username
        super().save(*args, **kwargs)

class Theme(models.Model):
    """Theme model for grouping cursus.

    Represents a category or theme (e.g., Music, IT) that groups related cursus.

    Attributes:
        name (str): Name of the theme.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        created_by (str): Username of the creator.
        updated_by (str): Username of the last updater.
    """
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Set audit fields before saving the theme.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the theme."""
        return self.name

class Cursus(models.Model):
    """Cursus model within a theme.

    Represents a cursus (e.g., Guitar Initiation) that belongs to a theme.

    Attributes:
        theme (Theme): The associated theme.
        name (str): Name of the cursus.
        price (decimal): Price of the cursus.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        created_by (str): Username of the creator.
        updated_by (str): Username of the last updater.
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Set audit fields before saving the cursus.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the cursus."""
        return f"{self.name} ({self.theme.name})"

class Lesson(models.Model):
    """Lesson model within a cursus.

    Represents an individual lesson that belongs to a cursus.

    Attributes:
        cursus (Cursus): The associated cursus.
        title (str): Title of the lesson.
        content (str): Content of the lesson.
        video_url (str): URL of the lesson video.
        price (decimal): Price of the lesson.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        created_by (str): Username of the creator.
        updated_by (str): Username of the last updater.
    """
    cursus = models.ForeignKey(Cursus, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    video_url = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Set audit fields before saving the lesson.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the lesson."""
        return f"{self.title} ({self.cursus.name})"

class Purchase(models.Model):
    """Purchase model for user transactions.

    Represents a purchase of a cursus or lesson by a user.

    Attributes:
        utilisateur (Utilisateur): The user making the purchase.
        cursus (Cursus): The purchased cursus (optional).
        lesson (Lesson): The purchased lesson (optional).
        amount (decimal): Amount of the purchase.
        purchase_date (datetime): Date of the purchase.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        created_by (str): Username of the creator.
        updated_by (str): Username of the last updater.
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    cursus = models.ForeignKey(Cursus, on_delete=models.SET_NULL, null=True, blank=True)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Set audit fields before saving the purchase.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the purchase."""
        if self.cursus:
            return f"Purchase of {self.cursus.name} by {self.utilisateur.username}"
        return f"Purchase of {self.lesson.title} by {self.utilisateur.username}"

class Validation(models.Model):
    """Validation model for tracking lesson completions.

    Tracks when a user validates a lesson after marking it as completed.

    Attributes:
        utilisateur (Utilisateur): The user validating the lesson.
        lesson (Lesson): The validated lesson.
        validated_at (datetime): Date of validation.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        created_by (str): Username of the creator.
        updated_by (str): Username of the last updater.
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    validated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Set audit fields before saving the validation.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the validation."""
        return f"{self.utilisateur.username} validated {self.lesson.title}"

class Certification(models.Model):
    """Certification model for theme completion.

    Tracks certifications earned by users for completing all lessons in a theme.

    Attributes:
        utilisateur (Utilisateur): The user earning the certification.
        theme (Theme): The theme for which the certification is earned.
        certified_at (datetime): Date of certification.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
        created_by (str): Username of the creator.
        updated_by (str): Username of the last updater.
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    certified_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        """Set audit fields before saving the certification.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        """Return a string representation of the certification."""
        return f"{self.utilisateur.username} certified in {self.theme.name}"