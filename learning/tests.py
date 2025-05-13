"""Unit tests for the Knowledge Learning application.

This module contains unit tests for user authentication, purchases,
lesson validation, and data access components.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import Utilisateur, Theme, Cursus, Lesson, Purchase, Validation, Certification
from .forms import RegistrationForm

class AuthenticationTests(TestCase):
    """Tests for user authentication functionality.

    This class tests user registration, email activation, login, and logout.
    """
    def setUp(self):
        """Set up test data for authentication tests.

        Creates a test user with an active account for use in tests.
        """
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )
        self.user.is_active = True
        self.user.save()

    def test_user_registration(self):
        """Test user registration and email activation requirement.

        Verifies that a new user can register and that the account is inactive
        until email activation.
        """
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'NewPassword123!',
            'password2': 'NewPassword123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(get_user_model().objects.filter(username='newuser').exists())
        user = get_user_model().objects.get(username='newuser')
        self.assertFalse(user.is_active)

    def test_user_email_activation(self):
        """Test user account activation via email link.

        Verifies that a user can activate their account using a valid email link.
        """
        inactive_user = get_user_model().objects.create_user(
            username='inactiveuser',
            email='inactiveuser@example.com',
            password='TestPassword123!'
        )
        inactive_user.is_active = False
        inactive_user.save()
        uid = urlsafe_base64_encode(force_bytes(inactive_user.pk))
        token = default_token_generator.make_token(inactive_user)
        response = self.client.get(reverse('activate', args=[uid, token]))
        self.assertEqual(response.status_code, 302)
        inactive_user.refresh_from_db()
        self.assertTrue(inactive_user.is_active)

    def test_login(self):
        """Test user login with valid credentials.

        Verifies that a user can log in and is authenticated after login.
        """
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        """Test user logout functionality.

        Verifies that a logged-in user can log out and is no longer authenticated.
        """
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

class PurchaseTests(TestCase):
    """Tests for purchase functionality with Stripe.

    This class tests purchasing lessons and cursus, including unauthorized access.
    """
    def setUp(self):
        """Set up test data for purchase tests.

        Creates a test user, theme, cursus, and lesson for purchase-related tests.
        """
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )
        self.user.is_active = True
        self.user.save()
        self.theme = Theme.objects.create(name='Musique', created_by='system', updated_by='system')
        self.cursus = Cursus.objects.create(
            theme=self.theme,
            name='Initiation à la guitare',
            price=50.00,
            created_by='system',
            updated_by='system'
        )
        self.lesson = Lesson.objects.create(
            cursus=self.cursus,
            title='Découverte de l’instrument',
            content='Contenu de la leçon',
            video_url='https://example.com/video',
            price=20.00,
            created_by='system',
            updated_by='system'
        )

    def test_buy_lesson(self):
        """Test lesson purchase with Stripe redirection.

        Verifies that a logged-in user can initiate a lesson purchase and is redirected to Stripe.
        """
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('buy_lesson', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Purchase.objects.exists())

    def test_buy_cursus(self):
        """Test cursus purchase with Stripe redirection.

        Verifies that a logged-in user can initiate a cursus purchase and is redirected to Stripe.
        """
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('buy_cursus', args=[self.cursus.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Purchase.objects.exists())

    def test_buy_lesson_unauthorized(self):
        """Test lesson purchase attempt by an unauthorized user.

        Verifies that an unauthenticated user is redirected to the login page.
        """
        self.client.logout()
        response = self.client.post(reverse('buy_lesson', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 302)

    def test_buy_lesson_inactive_user(self):
        """Test lesson purchase attempt by an inactive user.

        Verifies that an inactive user cannot purchase a lesson and is redirected to home.
        """
        self.user.is_active = False
        self.user.save()
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('buy_lesson', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Purchase.objects.exists())

class ValidationTests(TestCase):
    """Tests for lesson validation and certification functionality.

    This class tests the validation of lessons and the issuance of certifications.
    """
    def setUp(self):
        """Set up test data for validation tests.

        Creates a test user, theme, cursus, and lessons for validation-related tests.
        """
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )
        self.user.is_active = True
        self.user.save()
        self.theme = Theme.objects.create(name='Musique', created_by='system', updated_by='system')
        self.cursus1 = Cursus.objects.create(
            theme=self.theme,
            name='Initiation à la guitare',
            price=50.00,
            created_by='system',
            updated_by='system'
        )
        self.cursus2 = Cursus.objects.create(
            theme=self.theme,
            name='Initiation au piano',
            price=50.00,
            created_by='system',
            updated_by='system'
        )
        self.lesson1 = Lesson.objects.create(
            cursus=self.cursus1,
            title='Découverte de l’instrument',
            content='Contenu de la leçon',
            video_url='https://example.com/video',
            price=20.00,
            created_by='system',
            updated_by='system'
        )
        self.lesson2 = Lesson.objects.create(
            cursus=self.cursus1,
            title='Les accords et les gammes',
            content='Contenu de la leçon',
            video_url='https://example.com/video',
            price=20.00,
            created_by='system',
            updated_by='system'
        )
        self.lesson3 = Lesson.objects.create(
            cursus=self.cursus2,
            title='Découverte de l’instrument',
            content='Contenu de la leçon',
            video_url='https://example.com/video',
            price=20.00,
            created_by='system',
            updated_by='system'
        )
        self.lesson4 = Lesson.objects.create(
            cursus=self.cursus2,
            title='Les accords et les gammes',
            content='Contenu de la leçon',
            video_url='https://example.com/video',
            price=20.00,
            created_by='system',
            updated_by='system'
        )
        for lesson in [self.lesson1, self.lesson2, self.lesson3, self.lesson4]:
            Purchase.objects.create(
                utilisateur=self.user,
                lesson=lesson,
                amount=lesson.price,
                created_by=self.user.username,
                updated_by=self.user.username
            )

    def test_validate_lesson(self):
        """Test validation of a lesson by a user.

        Verifies that a user can validate a lesson after marking it as completed.
        """
        self.client.login(username='testuser', password='TestPassword123!')
        self.client.post(reverse('view_lesson', args=[self.lesson1.id]), {'mark_completed': 'true'})
        response = self.client.post(reverse('validate_lesson', args=[self.lesson1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Validation.objects.count(), 1)
        validation = Validation.objects.first()
        self.assertEqual(validation.utilisateur, self.user)
        self.assertEqual(validation.lesson, self.lesson1)

    def test_certification_after_validation(self):
        """Test certification issuance after validating all lessons in a theme.

        Verifies that a user earns a certification after validating all lessons in a theme.
        """
        self.client.login(username='testuser', password='TestPassword123!')
        for lesson in [self.lesson1, self.lesson2, self.lesson3, self.lesson4]:
            self.client.post(reverse('view_lesson', args=[lesson.id]), {'mark_completed': 'true'})
            self.client.post(reverse('validate_lesson', args=[lesson.id]))
        self.assertEqual(Certification.objects.count(), 1)
        certification = Certification.objects.first()
        self.assertEqual(certification.utilisateur, self.user)
        self.assertEqual(certification.theme, self.theme)

    def test_no_certification_if_theme_not_complete(self):
        """Test that no certification is issued if the theme is not fully completed.

        Verifies that a certification is not issued until all lessons in a theme are validated.
        """
        self.client.login(username='testuser', password='TestPassword123!')
        for lesson in [self.lesson1, self.lesson2]:
            self.client.post(reverse('view_lesson', args=[lesson.id]), {'mark_completed': 'true'})
            self.client.post(reverse('validate_lesson', args=[lesson.id]))
        self.assertEqual(Certification.objects.count(), 0)

class DataAccessTests(TestCase):
    """Tests for data access components.

    This class tests the creation of models in the database.
    """
    def setUp(self):
        """Set up test data for data access tests.

        Creates a test user, theme, and cursus for data access tests.
        """
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )
        self.user.is_active = True
        self.user.save()
        self.theme = Theme.objects.create(name='Musique', created_by='system', updated_by='system')
        self.cursus = Cursus.objects.create(
            theme=self.theme,
            name='Initiation à la guitare',
            price=50.00,
            created_by='system',
            updated_by='system'
        )

    def test_create_theme(self):
        """Test creation of a theme.

        Verifies that a theme can be created with the correct name.
        """
        theme = Theme.objects.create(name='Cuisine', created_by='system', updated_by='system')
        self.assertEqual(theme.name, 'Cuisine')

    def test_create_cursus(self):
        """Test creation of a cursus.

        Verifies that a cursus can be created and associated with a theme.
        """
        cursus = Cursus.objects.create(
            theme=self.theme,
            name='Initiation au piano',
            price=50.00,
            created_by='system',
            updated_by='system'
        )
        self.assertEqual(cursus.name, 'Initiation au piano')
        self.assertEqual(cursus.theme, self.theme)

    def test_create_lesson(self):
        """Test creation of a lesson.

        Verifies that a lesson can be created and associated with a cursus.
        """
        lesson = Lesson.objects.create(
            cursus=self.cursus,
            title='Test Lesson',
            content='Contenu',
            video_url='https://example.com',
            price=20.00,
            created_by='system',
            updated_by='system'
        )
        self.assertEqual(lesson.title, 'Test Lesson')
        self.assertEqual(lesson.cursus, self.cursus)

    def test_create_validation(self):
        """Test creation of a validation record.

        Verifies that a validation record can be created for a user and lesson.
        """
        lesson = Lesson.objects.create(
            cursus=self.cursus,
            title='Test Lesson',
            content='Contenu',
            video_url='https://example.com',
            price=20.00,
            created_by='system',
            updated_by='system'
        )
        validation = Validation.objects.create(
            utilisateur=self.user,
            lesson=lesson,
            created_by=self.user.username,
            updated_by=self.user.username
        )
        self.assertEqual(validation.utilisateur, self.user)
        self.assertEqual(validation.lesson, lesson)

    def test_create_certification(self):
        """Test creation of a certification record.

        Verifies that a certification record can be created for a user and theme.
        """
        certification = Certification.objects.create(
            utilisateur=self.user,
            theme=self.theme,
            created_by=self.user.username,
            updated_by=self.user.username
        )
        self.assertEqual(certification.utilisateur, self.user)
        self.assertEqual(certification.theme, self.theme)