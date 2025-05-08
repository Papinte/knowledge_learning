# learning/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group  # Importer User et Group depuis auth.models
from .models import Utilisateur, Theme, Cursus, Lesson, Purchase, Validation, Certification

# Enregistrer le modèle Utilisateur personnalisé
admin.site.register(Utilisateur, UserAdmin)

# Enregistrer les autres modèles
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('name',)

@admin.register(Cursus)
class CursusAdmin(admin.ModelAdmin):
    list_display = ('name', 'theme', 'price', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('theme',)
    search_fields = ('name',)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'cursus', 'price', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('cursus',)
    search_fields = ('title',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'cursus', 'lesson', 'amount', 'purchase_date', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('utilisateur', 'cursus', 'lesson')
    search_fields = ('utilisateur__username',)

@admin.register(Validation)
class ValidationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'lesson', 'validated_at', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('utilisateur', 'lesson')
    search_fields = ('utilisateur__username', 'lesson__title')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'theme', 'certified_at', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('utilisateur', 'theme')
    search_fields = ('utilisateur__username', 'theme__name')

# Supprimer ou commenter ces lignes car User et Group ne sont pas enregistrés
# admin.site.unregister(User)
# admin.site.unregister(Group)