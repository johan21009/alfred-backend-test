import requests
from django.conf import settings
from typing import Optional, Dict, Any, Tuple

class GoogleMapsService:
    """
    Servicio para interactuar con la API de Google Maps Directions
    """
    
    @staticmethod
    def get_eta_with_traffic(**kwargs) -> Optional[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """
        Obtiene el tiempo estimado de llegada (ETA) con tráfico en tiempo real
        
        Args:
            origin (str): Coordenadas "lat,lng" o dirección
            destination (str): Coordenadas "lat,lng" o dirección
            api_key (str, optional): API Key. Si no se provee, usa settings.GOOGLE_MAPS_API_KEY
            mode (str): Modo de transporte (driving, walking, bicycling, transit)
            departure_time (str): "now" o timestamp
            traffic_model (str): best_guess, pessimistic, optimistic
            alternatives (bool): True para rutas alternativas
            language (str): Código de idioma
            region (str): Código de región
            units (str): metric o imperial
            
        Returns:
            int: Tiempo estimado en segundos o None si hay error
        """
        required_params = ['origin', 'destination']
        for param in required_params:
            if param not in kwargs:
                raise ValueError(f"Falta el parámetro requerido: {param}")
        
        base_url = "https://maps.googleapis.com/maps/api/directions/json"
        
        # Usar API key de settings si no se proporciona
        api_key = kwargs.get('api_key', getattr(settings, 'GOOGLE_MAPS_API_KEY', None))
        if not api_key:
            raise ValueError("Se requiere una API key de Google Maps")
        
        params = {
            'key': api_key,
            'origin': kwargs['origin'],
            'destination': kwargs['destination'],
            'departure_time': kwargs.get('departure_time', 'now'),
            'traffic_model': kwargs.get('traffic_model', 'best_guess'),
            'mode': kwargs.get('mode', 'driving'),
            'units': kwargs.get('units', 'metric')
        }
        
        # Parámetros condicionales
        if 'language' in kwargs:
            params['language'] = kwargs['language']
        if 'region' in kwargs:
            params['region'] = kwargs['region']
        if 'alternatives' in kwargs:
            params['alternatives'] = str(kwargs['alternatives']).lower()
        
        try:
            
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'OK' or not data.get('routes'):
                return None
            
            if data['routes'] == []:
                return None

            duration_sec = data['routes'][0]['legs'][0]['duration']['value']
            
            
            return duration_sec
        
        except (requests.exceptions.RequestException, KeyError, IndexError):
            print("Error al obtener datos de Google Maps API")
            return None