from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Utilisateur, Theme, Cursus, Lesson, Purchase, Validation, Certification

class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='TestPassword123!'
        )
        self.user.is_active = True
        self.user.save()

    def test_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPassword123!'
        })
        self.assertEqual(response.status_code, 302)  # Redirection après connexion
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout(self):
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirection après déconnexion
        self.assertFalse(response.wsgi_request.user.is_authenticated)

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
        # Simuler un achat (on ne peut pas tester Stripe directement, mais on peut vérifier la création de Purchase)
        Purchase.objects.create(
            utilisateur=self.user,
            lesson=self.lesson,
            amount=self.lesson.price,
            created_by=self.user.username,
            updated_by=self.user.username
        )
        self.assertEqual(Purchase.objects.count(), 1)
        purchase = Purchase.objects.first()
        self.assertEqual(purchase.utilisateur, self.user)
        self.assertEqual(purchase.lesson, self.lesson)
        self.assertEqual(purchase.amount, 20.00)

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
        # Simuler un achat pour que l'utilisateur ait accès à la leçon
        Purchase.objects.create(
            utilisateur=self.user,
            lesson=self.lesson,
            amount=self.lesson.price,
            created_by=self.user.username,
            updated_by=self.user.username
        )

    def test_validate_lesson(self):
        self.client.login(username='testuser', password='TestPassword123!')
        response = self.client.post(reverse('validate_lesson', args=[self.lesson.id]))
        self.assertEqual(response.status_code, 302)  # Redirection après validation
        self.assertEqual(Validation.objects.count(), 1)
        validation = Validation.objects.first()
        self.assertEqual(validation.utilisateur, self.user)
        self.assertEqual(validation.lesson, self.lesson)

    def test_certification_after_validation(self):
        self.client.login(username='testuser', password='TestPassword123!')
        # Simuler que toutes les leçons du cursus sont validées (ici, une seule leçon)
        self.client.post(reverse('validate_lesson', args=[self.lesson.id]))
        self.assertEqual(Certification.objects.count(), 1)  # Une certification devrait être créée
        certification = Certification.objects.first()
        self.assertEqual(certification.utilisateur, self.user)
        self.assertEqual(certification.theme, self.theme)