from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Address, Driver, Service
import base64

class ServiceTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Configurate Basic Auth
        credentials = base64.b64encode('testuser:testpass123'.encode()).decode()
        self.client.credentials(HTTP_AUTHORIZATION=f'Basic {credentials}')
        
        # Create test addresses
        self.address1 = Address.objects.create(
            street="Cra. 14 #86A-15",
            city="Bogota",
            state="Bogota",
            zip_code="12345",
            country="Colombia",
            location=Point(-74.0543174, 4.6708225)  
        )

        
        self.address2 = Address.objects.create(
            street="Cra. 12 #86A-15",
            city="Bogota",
            state="Bogota",
            zip_code="12345",
            country="Colombia",
            location=Point(-74.0543174, 4.6908225) 
        )
        
        # Create test drivers
        self.driver1 = Driver.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="1234567890",
            status="available",
            address=None,
            current_location=Point(-74.0743174, 4.6408225)  
        )
        
        self.driver2 = Driver.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="0987654321",
            status="available",
            address=None,
            current_location=Point(-74.0643174, 4.6308225)  
        )

        

    def test_service_creation_with_driver_assignment(self):
        data = {
            "customer_name": "Test Customer",
            "customer_phone": "5551234567",
            "pickup_address_id": str(self.address1.id),
        }

        
        
        response = self.client.post('/api/services/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        service = Service.objects.first()
        self.assertIsNotNone(service.driver)
        self.assertEqual(service.status, 'assigned')
        
        # Check driver status was updated
        driver = Driver.objects.get(id=service.driver.id)
        self.assertEqual(driver.status, 'in_service')

    def test_service_completion(self):
        service = Service.objects.create(
            customer_name="Test Customer",
            customer_phone="5551234567",
            pickup_address=self.address1,
            driver=self.driver1,
            status="assigned"
        )
        
        response = self.client.post(f'/api/services/{service.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        service.refresh_from_db()
        self.assertEqual(service.status, 'completed')
        self.assertIsNotNone(service.completed_at)
        
        # Check driver status was updated
        self.driver1.refresh_from_db()
        self.assertEqual(self.driver1.status, 'available')

    def test_no_available_drivers(self):
        # Set all drivers to offline
        Driver.objects.update(status='offline')
        
        data = {
            "customer_name": "Test Customer",
            "customer_phone": "5551234567",
            "pickup_address_id": str(self.address1.id),
        }
        
        response = self.client.post('/api/services/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'No hay conductores disponibles cercanos')