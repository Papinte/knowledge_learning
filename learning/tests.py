from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import Utilisateur, Theme, Cursus, Lesson, Purchase, Validation, Certification
from .forms import RegistrationForm

# Test user authentication
class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )
        self.user.is_active = True
        self.user.save()

    def test_user_registration(self):
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
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

# Test purchase functionality
class PurchaseTests(TestCase):
    def setUp(self):
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
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('buy_lesson', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Purchase.objects.exists())

    def test_buy_cursus(self):
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('buy_cursus', args=[self.cursus.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Purchase.objects.exists())

    def test_buy_lesson_unauthorized(self):
        self.client.logout()
        response = self.client.post(reverse('buy_lesson', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 302)

    def test_buy_lesson_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('buy_lesson', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Purchase.objects.exists())

# Test validation functionality
class ValidationTests(TestCase):
    def setUp(self):
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
        self.client.login(username='testuser', password='TestPassword123!')
        self.client.post(reverse('view_lesson', args=[self.lesson1.id]), {'mark_completed': 'true'})
        response = self.client.post(reverse('validate_lesson', args=[self.lesson1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Validation.objects.count(), 1)
        validation = Validation.objects.first()
        self.assertEqual(validation.utilisateur, self.user)
        self.assertEqual(validation.lesson, self.lesson1)

    def test_certification_after_validation(self):
        self.client.login(username='testuser', password='TestPassword123!')
        for lesson in [self.lesson1, self.lesson2, self.lesson3, self.lesson4]:
            self.client.post(reverse('view_lesson', args=[lesson.id]), {'mark_completed': 'true'})
            self.client.post(reverse('validate_lesson', args=[lesson.id]))
        self.assertEqual(Certification.objects.count(), 1)
        certification = Certification.objects.first()
        self.assertEqual(certification.utilisateur, self.user)
        self.assertEqual(certification.theme, self.theme)

    def test_no_certification_if_theme_not_complete(self):
        self.client.login(username='testuser', password='TestPassword123!')
        for lesson in [self.lesson1, self.lesson2]:
            self.client.post(reverse('view_lesson', args=[lesson.id]), {'mark_completed': 'true'})
            self.client.post(reverse('validate_lesson', args=[lesson.id]))
        self.assertEqual(Certification.objects.count(), 0)

# Test data access components
class DataAccessTests(TestCase):
    def setUp(self):
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
        theme = Theme.objects.create(name='Cuisine', created_by='system', updated_by='system')
        self.assertEqual(theme.name, 'Cuisine')

    def test_create_cursus(self):
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
        certification = Certification.objects.create(
            utilisateur=self.user,
            theme=self.theme,
            created_by=self.user.username,
            updated_by=self.user.username
        )
        self.assertEqual(certification.utilisateur, self.user)
        self.assertEqual(certification.theme, self.theme)