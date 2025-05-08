# learning/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Utilisateur(AbstractUser):
    """
    Custom user model with role and activation status.
    """
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=[('client', 'Client'), ('admin', 'Admin')], default='client')
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    # Ajouter related_name pour éviter le conflit
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='utilisateur_set',  # Nom unique pour la relation inverse
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='utilisateur_set',  # Nom unique pour la relation inverse
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def save(self, *args, **kwargs):
        if not self.created_by:
            self.created_by = self.username
        self.updated_by = self.username
        super().save(*args, **kwargs)

# Le reste du fichier reste inchangé
class Theme(models.Model):
    """
    Represents a theme of formation (e.g., Music, IT).
    """
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Cursus(models.Model):
    """
    Represents a cursus within a theme (e.g., Guitar Initiation).
    """
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.theme.name})"

class Lesson(models.Model):
    """
    Represents a lesson within a cursus.
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
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.cursus.name})"

class Purchase(models.Model):
    """
    Represents a purchase of a cursus or lesson by a user.
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
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        if self.cursus:
            return f"Purchase of {self.cursus.name} by {self.utilisateur.username}"
        return f"Purchase of {self.lesson.title} by {self.utilisateur.username}"

class Validation(models.Model):
    """
    Tracks lesson validations by users.
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    validated_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.utilisateur.username} validated {self.lesson.title}"

class Certification(models.Model):
    """
    Tracks certifications earned by users for completing a theme.
    """
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    certified_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255)
    updated_by = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.created_by:
            self.created_by = "system"
        self.updated_by = "system"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.utilisateur.username} certified in {self.theme.name}"