# Alfred Backend Test - API para asignacion de servicios de domicilio

![Badge](https://img.shields.io/badge/Django-REST%20Framework-green) ![Badge](https://img.shields.io/badge/PostgreSQL-Database-blue) ![Badge](https://img.shields.io/badge/Docker-Containerization-2496ED)

API construida con Django REST Framework para gestión de conductores, direcciones y servicios de entrega.

## Características principales

- Operaciones CRUD completas para:
  - Direcciones
  - Conductores 
  - Servicios

-  Asignación automática del conductor disponible más cercano
-  Gestión de estados:
  - Estados de servicio (pendiente, en curso, completado)
  - Disponibilidad de conductores (online/offline)


## Requerimientos

- Docker
- Docker Compose

## Configuración

1. Clonar repositorio:
     ```bash
     git clone https://github.com/yourusername/alfred-backend-test.git
     cd alfred-backend-test
     ```
2. Construir e iniciar contenedores:
     ```bash
     docker-compose up -d --build
     ```
3. Aplicar migraciones:
     ```bash
     docker-compose exec web python manage.py migrate
     ```
4. Realizar pruebas unitarias:
     ```bash
     docker-compose exec web python manage.py test
     ```
5. Generar datos de prueba (20 registros):
      ```bash
     docker-compose exec web python manage.py generate_test_data 20
     ```
6. Crear usuario administrador:
      ```bash
     docker-compose exec web python manage.py createsuperuser
     ```
- Panel de administración: http://localhost:8000/admin
- Endpoint API: http://localhost:8000/api/

## API Endpoints


- GET /api/addresses/ - Listar todas las direcciones

- POST /api/addresses/ - Crear nueva direccion

- GET /api/addresses/{id}/ - Recibir informacion de una direccion

- PUT /api/addresses/{id}/ - Actualizar una direccion

- DELETE /api/addresses/{id}/ - Delete an address Borrar  una direccion

- GET /api/drivers/ - Listar todos los conductores

- POST /api/drivers/ - Crear un nuevo conductor

- GET /api/drivers/{id}/ - Recibir informacion de un conductor

- PUT /api/drivers/{id}/ - Actualizar informacion de un conductor

- DELETE /api/drivers/{id}/ - Borrar un conductor

- POST /api/drivers/{id}/set_available/ - Cambiar estado de un conductor a disponible

- POST /api/drivers/{id}/set_offline/ - Cambiar estado de un conductor a no disponible

- GET /api/services/ - Listar todos los Servicios

- POST /api/services/ - Crear un nuevo servicio (Asigna automaticamente el conductor mas cercano)

- GET /api/services/{id}/ - Recibir informacion de un servicio

- PUT /api/services/{id}/ - Actualizar informacion de un servicio

- DELETE /api/services/{id}/ - Borrar un servicio

- POST /api/services/{id}/complete/ - Marcar servicio como completado

## Despliegue en la Nube (AWS)

### Resumen de Arquitectura
- **Cómputo**: Utilizar AWS ECS (Elastic Container Service) para ejecutar los contenedores Docker
- **Base de datos**: Usar Amazon RDS con PostgreSQL y la extensión PostGIS
- **Redes**: Ubicar los recursos en una VPC con grupos de seguridad apropiados
- **Balanceo de carga**: Usar Application Load Balancer para distribución de tráfico
- **Almacenamiento**: Usar EFS para almacenamiento persistente si es necesario

### Pasos
1. Crear un repositorio ECR y subir tu imagen Docker
2. Configurar una instancia RDS PostgreSQL con la extensión PostGIS
3. Crear un clúster ECS con tipo de lanzamiento Fargate
4. Configurar definiciones de tareas para tu aplicación
5. Configurar ALB y conectarlo a tu servicio ECS
6. Establecer políticas de autoescalado basadas en uso de CPU/memoria

### Consideraciones de Seguridad
- Usar roles IAM para tareas ECS en lugar de codificar credenciales
- Habilitar cifrado en reposo para RDS
- Usar grupos de seguridad para restringir acceso
- Habilitar logs de flujo de VPC para monitoreo
- Usar AWS Secrets Manager para configuración sensible

### Escalabilidad
- ECS puede escalar tareas automáticamente según la carga
- RDS puede escalarse verticalmente o habilitar réplicas de lectura
- Usar CloudFront para caché si es necesario
- Considerar usar ElastiCache para Redis si se necesita caché
