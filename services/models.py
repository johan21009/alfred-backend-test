from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    location = gis_models.PointField(geography=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-created_at']


class Driver(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('in_service', 'In Service'),
        ('offline', 'Offline'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    current_location = gis_models.PointField(geography=True, blank=True, null=True)
    rating = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_available(self):
        return self.status == 'available'


class Service(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    pickup_address = models.ForeignKey(Address, related_name='pickup_services', on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(Driver, related_name='services', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    estimated_arrival = models.DurationField(null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Service #{self.id} - {self.get_status_display()}"

    def complete_service(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        if self.driver:
            self.driver.status = 'available'
            self.driver.save()
        self.save()

    class Meta:
        ordering = ['-requested_at']