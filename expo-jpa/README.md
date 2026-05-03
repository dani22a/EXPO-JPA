# expo-jpa — Demo de la exposicion

Proyecto Spring Boot 4.0.6 + Java 17 + PostgreSQL para la exposicion de Bases de Datos y Spring Data JPA.

## Arrancar el proyecto

### Opcion A: con PostgreSQL (recomendado para la demo)

```bash
# 1. Crear la base
psql -U postgres -c "CREATE DATABASE expo_jpa;"

# 2. Ajustar credenciales en src/main/resources/application.properties si hace falta

# 3. Arrancar
./mvnw spring-boot:run
```

App en `http://localhost:8080`. Los datos de prueba (`data.sql`) se cargan solos.

Para ejecutar los **extras** (indices avanzados, funciones, triggers, vistas) que no se aplican automaticamente:

```bash
psql -U postgres -d expo_jpa -f src/main/resources/db/postgres-extras.sql
```

### Opcion B: con H2 en memoria (plan B si Postgres falla)

```bash
./mvnw spring-boot:run -Dspring-boot.run.profiles=h2
```

Consola web: `http://localhost:8080/h2-console` (URL: `jdbc:h2:mem:expo_jpa`, user `sa`, sin password).

## Endpoints principales

| Metodo | URL | Descripcion |
|--------|-----|-------------|
| GET    | `/api/clientes` | Listar clientes |
| POST   | `/api/clientes` | Crear cliente |
| GET    | `/api/clientes/{id}` | Obtener cliente |
| PUT    | `/api/clientes/{id}` | Actualizar cliente |
| DELETE | `/api/clientes/{id}` | Eliminar cliente (cascada) |
| POST   | `/api/cuentas` | Crear cuenta |
| GET    | `/api/cuentas/{id}` | Obtener cuenta |
| GET    | `/api/cuentas/cliente/{clienteId}?page=0&size=10` | Cuentas paginadas |
| GET    | `/api/cuentas/cliente/{clienteId}/saldo-total` | Suma de saldos |
| GET    | `/api/cuentas/top?limite=5` | Cuentas sobre el promedio (native query) |
| POST   | `/api/cuentas/{id}/movimientos` | Registrar deposito/retiro |
| POST   | `/api/cuentas/transferir` | Transferencia atomica |

## Estructura

```
src/main/java/pe/edu/unitru/expo_jpa/
├── ExpoJpaApplication.java
├── entities/        # @Entity con relaciones 1-N, N-1, M-N
├── repositories/    # JpaRepository + derived + JPQL + native + SP
├── services/        # @Transactional, logica de negocio
├── controllers/     # REST API
├── dto/             # Records para entrada/salida
└── exceptions/      # Manejo global con @RestControllerAdvice
```
