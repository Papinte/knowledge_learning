from django.core.management.base import BaseCommand
from learning.models import Theme, Cursus, Lesson

class Command(BaseCommand):
    help = 'Populates the database with initial data for the beta version'

    def handle(self, *args, **kwargs):
        # Create Themes
        music = Theme.objects.create(name='Musique', created_by='system', updated_by='system')
        informatique = Theme.objects.create(name='Informatique', created_by='system', updated_by='system')
        jardinage = Theme.objects.create(name='Jardinage', created_by='system', updated_by='system')
        cuisine = Theme.objects.create(name='Cuisine', created_by='system', updated_by='system')

        # Create Cursuses and Lessons for Musique
        guitar_init = Cursus.objects.create(theme=music, name='Initiation à la guitare', price=50.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=guitar_init, title='Découverte de l’instrument', content='Lorem ipsum...', video_url='https://example.com/video', price=26.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=guitar_init, title='Les accords et les gammes', content='Lorem ipsum...', video_url='https://example.com/video', price=26.00, created_by='system', updated_by='system')

        piano_init = Cursus.objects.create(theme=music, name='Initiation au piano', price=50.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=piano_init, title='Découverte de l’instrument', content='Lorem ipsum...', video_url='https://example.com/video', price=26.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=piano_init, title='Les accords et les gammes', content='Lorem ipsum...', video_url='https://example.com/video', price=26.00, created_by='system', updated_by='system')

        # Create Cursuses and Lessons for Informatique
        web_dev = Cursus.objects.create(theme=informatique, name='Initiation au développement web', price=60.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=web_dev, title='Les langages Html et CSS', content='Lorem ipsum...', video_url='https://example.com/video', price=32.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=web_dev, title='Dynamiser votre site avec Javascript', content='Lorem ipsum...', video_url='https://example.com/video', price=32.00, created_by='system', updated_by='system')

        # Create Cursuses and Lessons for Jardinage
        jardinage_init = Cursus.objects.create(theme=jardinage, name='Initiation au jardinage', price=30.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=jardinage_init, title='Les outils du jardinier', content='Lorem ipsum...', video_url='https://example.com/video', price=16.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=jardinage_init, title='Jardiner avec la lune', content='Lorem ipsum...', video_url='https://example.com/video', price=16.00, created_by='system', updated_by='system')

        # Create Cursuses and Lessons for Cuisine
        cuisine_init = Cursus.objects.create(theme=cuisine, name='Initiation à la cuisine', price=44.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=cuisine_init, title='Les modes de cuisson', content='Lorem ipsum...', video_url='https://example.com/video', price=23.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=cuisine_init, title='Les saveurs', content='Lorem ipsum...', video_url='https://example.com/video', price=23.00, created_by='system', updated_by='system')

        dressage_init = Cursus.objects.create(theme=cuisine, name='Initiation à l’art du dressage culinaire', price=48.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=dressage_init, title='Mettre en œuvre le style dans l’assiette', content='Lorem ipsum...', video_url='https://example.com/video', price=26.00, created_by='system', updated_by='system')
        Lesson.objects.create(cursus=dressage_init, title='Harmoniser un repas à quatre plats', content='Lorem ipsum...', video_url='https://example.com/video', price=26.00, created_by='system', updated_by='system')

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with initial data.'))