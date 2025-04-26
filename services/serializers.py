from rest_framework import serializers
from .models import Address, Driver, Service
from django.contrib.gis.geos import Point
from django.utils import timezone


class AddressSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        if latitude and longitude:
            validated_data['location'] = Point(float(longitude), float(latitude))
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        
        if latitude and longitude:
            validated_data['location'] = Point(float(longitude), float(latitude))
        
        return super().update(instance, validated_data)


class DriverSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    address = AddressSerializer(read_only=True)
    address_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Driver
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def create(self, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        address_id = validated_data.pop('address_id', None)
        
        if latitude and longitude:
            validated_data['current_location'] = Point(float(longitude), float(latitude))
        
        driver = Driver.objects.create(**validated_data)
        
        if address_id:
            try:
                address = Address.objects.get(id=address_id)
                driver.address = address
                driver.save()
            except Address.DoesNotExist:
                pass
        
        return driver

    def update(self, instance, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        address_id = validated_data.pop('address_id', None)
        
        if latitude and longitude:
            validated_data['current_location'] = Point(float(longitude), float(latitude))
        
        if address_id:
            try:
                address = Address.objects.get(id=address_id)
                instance.address = address
            except Address.DoesNotExist:
                pass
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class ServiceSerializer(serializers.ModelSerializer):
    pickup_address = AddressSerializer(read_only=True)
    pickup_address_id = serializers.UUIDField(write_only=True)
    driver = DriverSerializer(read_only=True)
    driver_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = Service
        fields = '__all__'
        read_only_fields = ('id', 'requested_at', 'assigned_at', 'started_at', 'completed_at', 'estimated_arrival')

    def create(self, validated_data):
        pickup_address_id = validated_data.pop('pickup_address_id')
        driver_id = validated_data.pop('driver_id', None)
        
        try:
            pickup_address = Address.objects.get(id=pickup_address_id)
        except Address.DoesNotExist:
            raise serializers.ValidationError({"pickup_address_id": "Invalid address ID"})
        
        service = Service.objects.create(
            pickup_address=pickup_address,
            **validated_data
        )
        
        if driver_id:
            try:
                driver = Driver.objects.get(id=driver_id)
                service.driver = driver
                service.status = 'assigned'
                service.assigned_at = timezone.now()
                service.save()
            except Driver.DoesNotExist:
                pass
        
        return service

    def update(self, instance, validated_data):
        driver_id = validated_data.pop('driver_id', None)
        
        if driver_id:
            try:
                driver = Driver.objects.get(id=driver_id)
                instance.driver = driver
                if instance.status == 'requested':
                    instance.status = 'assigned'
                    instance.assigned_at = timezone.now()
            except Driver.DoesNotExist:
                pass
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance