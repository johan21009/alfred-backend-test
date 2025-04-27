from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from faker import Faker
import random
from services.models import Address, Driver

fake = Faker('es_CO')
Faker.seed(46)
class Command(BaseCommand):
    help = 'Generates test data for addresses and drivers'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of addresses and drivers to create')

    def handle(self, *args, **options):
        count = options['count']
        
        # Create addresses
        for _ in range(count):
            lat = random.uniform(4.5, 4.6)
            lng = random.uniform(-74.1, -74.2)
            
            address = Address.objects.create(
                street=fake.street_address(),
                city=fake.city(),
                state=fake.department(),
                zip_code=fake.postcode(),
                country='Colombia',
                location=Point(lng, lat)
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} addresses'))
        
        # Create drivers
        addresses = list(Address.objects.all())
        
        for _ in range(count):
            address = random.choice(addresses)
            lat = address.location.y + random.uniform(-0.1, 0.1)
            lng = address.location.x + random.uniform(-0.1, 0.1)
            
            driver = Driver.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone=fake.phone_number(),
                status=random.choice(['available', 'available', 'available', 'offline']),
                address=address,
                current_location=Point(lng, lat),
                rating=round(random.uniform(3.0, 5.0), 1)
            )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} drivers'))