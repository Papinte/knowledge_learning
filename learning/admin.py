from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Theme, Cursus, Lesson, Purchase, Validation, Certification

# Register custom user model
admin.site.register(Utilisateur, UserAdmin)

# Admin configuration for Theme
@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'created_by', 'updated_by')
    search_fields = ('name',)

# Admin configuration for Cursus
@admin.register(Cursus)
class CursusAdmin(admin.ModelAdmin):
    list_display = ('name', 'theme', 'price', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('theme',)
    search_fields = ('name',)

# Admin configuration for Lesson
@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'cursus', 'price', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('cursus',)
    search_fields = ('title',)

# Admin configuration for Purchase
@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'cursus', 'lesson', 'amount', 'purchase_date', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('utilisateur', 'cursus', 'lesson')
    search_fields = ('utilisateur__username',)

# Admin configuration for Validation
@admin.register(Validation)
class ValidationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'lesson', 'validated_at', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('utilisateur', 'lesson')
    search_fields = ('utilisateur__username', 'lesson__title')

# Admin configuration for Certification
@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'theme', 'certified_at', 'created_at', 'updated_at', 'created_by', 'updated_by')
    list_filter = ('utilisateur', 'theme')
    search_fields = ('utilisateur__username', 'theme__name')