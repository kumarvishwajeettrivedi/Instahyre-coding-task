import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Place, Review
from faker import Faker

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with random data'

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        self.stdout.write('Creating Users...')
        users = []
        for _ in range(10):
            phone = fake.unique.phone_number()[:15] # Truncate to fit max_length
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={'name': fake.name(), 'password': 'password'}
            )
            if created:
                user.set_password('password')
                user.save()
            users.append(user)

        self.stdout.write('Creating Places...')
        places = []
        for _ in range(20):
            place, created = Place.objects.get_or_create(
                name=fake.company(),
                address=fake.address()
            )
            places.append(place)

        self.stdout.write('Creating Reviews...')
        for _ in range(50):
            place = random.choice(places)
            user = random.choice(users)
            Review.objects.create(
                place=place,
                user=user,
                rating=random.randint(1, 5),
                text=fake.text()
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated database'))
