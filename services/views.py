from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Address, Driver, Service
from .serializers import AddressSerializer, DriverSerializer, ServiceSerializer
from .google_maps_time import GoogleMapsService
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.utils import timezone
import datetime
import math


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer

    @action(detail=True, methods=['post'])
    def set_available(self, request, pk=None):
        driver = self.get_object()
        driver.status = 'available'
        driver.save()
        return Response({'status': 'Conductor marcado como disponible'})

    @action(detail=True, methods=['post'])
    def set_offline(self, request, pk=None):
        driver = self.get_object()
        driver.status = 'offline'
        driver.save()
        return Response({'status': 'Conductor marcado como fuera de servicio'})


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        pickup_address_id = request.data.get('pickup_address_id')
        try:
            pickup_address = Address.objects.get(id=pickup_address_id)
        except Address.DoesNotExist:
            return Response(
                {"detail": "ID de direccion de recogida no existe"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
        if not pickup_address.location:
            return Response(
                {"detail": "Direccion de recogida debe tener coordenadas de localizacion"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get available drivers within 100 km (for performance) and order by distance
        available_drivers = Driver.objects.filter(
            status='available',
            current_location__distance_lte=(pickup_address.location, 100000)  # 100 km in meters
        ).annotate(
            distance=Distance('current_location', pickup_address.location)
        ).order_by('distance')[:5]  # Get top 5 closest
        
        if not available_drivers.exists():
            return Response(
                {"detail": "No hay conductores disponibles cercanos"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Assign the closest driver
        closest_driver = available_drivers.first()
        
        # Calculate estimated time of arrival (ETA) using Google Maps API
        distance_time = GoogleMapsService.get_eta_with_traffic(
            origin=f"{pickup_address.location.y},{pickup_address.location.x}",
            destination=f"{closest_driver.current_location.y},{closest_driver.current_location.x}"
                                                       
        )
        if distance_time != None:
            estimated_time = datetime.timedelta(seconds=distance_time)
        else:
            # Simple estimation: 2 minutes per km
            distance_km = closest_driver.distance.km
            estimated_time = datetime.timedelta(minutes=math.ceil(distance_km * 2))
        
        service = Service.objects.create(
            customer_name=request.data.get('customer_name'),
            customer_phone=request.data.get('customer_phone'),
            pickup_address=pickup_address,
            driver=closest_driver,
            status='assigned',
            estimated_arrival=estimated_time,
        )
        
        # Update driver status
        closest_driver.status = 'in_service'
        closest_driver.save()
        
        serializer = self.get_serializer(service)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        service = self.get_object()
        service.complete_service()
        return Response({'status': 'service completed'})