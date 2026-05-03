# Comandos curl — listos para copiar y pegar

Versión terminal de la colección Postman. Útil si querés mostrar el flujo desde la consola en la demo o si Postman da problemas el día D.

> **Base URL**: `http://localhost:8080` (cambiar si la app corre en otro puerto)
>
> **Tip Windows PowerShell**: `curl` está aliasado a `Invoke-WebRequest`. Usar `curl.exe` o instalar el `curl` real, o usar Git Bash. Si no, copiar los comandos y reescribir en formato `Invoke-RestMethod`.

---

## 1. Clientes

### Listar todos
```bash
curl -X GET http://localhost:8080/api/clientes
```

### Obtener por ID
```bash
curl -X GET http://localhost:8080/api/clientes/1
```

### Crear cliente
```bash
curl -X POST http://localhost:8080/api/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "Lucia",
    "apellidos": "Ramirez",
    "dni": "70999888",
    "email": "lucia@example.com"
  }'
```

### Actualizar cliente
```bash
curl -X PUT http://localhost:8080/api/clientes/1 \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "Daniel",
    "apellidos": "Solano Vega",
    "dni": "70123456",
    "email": "daniel.nuevo@example.com"
  }'
```

### Eliminar (cascada borra cuentas y movimientos)
```bash
curl -X DELETE http://localhost:8080/api/clientes/3
```

### Validación fallida — devuelve 400 con detalle por campo
```bash
curl -X POST http://localhost:8080/api/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nombres": "",
    "apellidos": "Test",
    "dni": "123",
    "email": "no-es-email"
  }'
```

---

## 2. Cuentas

### Obtener por ID
```bash
curl -X GET http://localhost:8080/api/cuentas/1
```

### Listar cuentas de un cliente con paginación y orden
```bash
curl -X GET "http://localhost:8080/api/cuentas/cliente/1?page=0&size=10&sort=saldo,desc"
```

### Saldo total de un cliente (JPQL con SUM)
```bash
curl -X GET http://localhost:8080/api/cuentas/cliente/1/saldo-total
```

### Top N cuentas sobre el promedio (NATIVE QUERY)
```bash
curl -X GET "http://localhost:8080/api/cuentas/top?limite=3"
```

### Crear cuenta
```bash
curl -X POST http://localhost:8080/api/cuentas \
  -H "Content-Type: application/json" \
  -d '{
    "numeroCuenta": "0001-9999",
    "saldoInicial": 5000.00,
    "clienteId": 1
  }'
```

---

## 3. Movimientos

### DEPOSITO (suma al saldo)
```bash
curl -X POST http://localhost:8080/api/cuentas/1/movimientos \
  -H "Content-Type: application/json" \
  -d '{
    "monto": 500.00,
    "tipo": "DEPOSITO",
    "descripcion": "Deposito en ventanilla"
  }'
```

### RETIRO (resta del saldo)
```bash
curl -X POST http://localhost:8080/api/cuentas/1/movimientos \
  -H "Content-Type: application/json" \
  -d '{
    "monto": 200.00,
    "tipo": "RETIRO",
    "descripcion": "Retiro por cajero"
  }'
```

### PAGO_SERVICIO
```bash
curl -X POST http://localhost:8080/api/cuentas/2/movimientos \
  -H "Content-Type: application/json" \
  -d '{
    "monto": 80.00,
    "tipo": "PAGO_SERVICIO",
    "descripcion": "Pago de internet"
  }'
```

### RETIRO con saldo insuficiente — devuelve 422
```bash
curl -X POST http://localhost:8080/api/cuentas/3/movimientos \
  -H "Content-Type: application/json" \
  -d '{
    "monto": 999999.00,
    "tipo": "RETIRO",
    "descripcion": "Intento que debe fallar"
  }'
```

---

## 4. Transferencias atómicas

### Transferir entre cuentas (toda la operación es 1 transacción)
```bash
curl -X POST http://localhost:8080/api/cuentas/transferir \
  -H "Content-Type: application/json" \
  -d '{
    "origenId": 2,
    "destinoId": 3,
    "monto": 300.00
  }'
```

### Transferencia inválida (misma cuenta)
```bash
curl -X POST http://localhost:8080/api/cuentas/transferir \
  -H "Content-Type: application/json" \
  -d '{
    "origenId": 1,
    "destinoId": 1,
    "monto": 100.00
  }'
```

---

## 5. Casos de error útiles para mostrar el manejo de excepciones

### 404 — recurso no encontrado
```bash
curl -X GET http://localhost:8080/api/clientes/9999
```

### Conflicto — número de cuenta duplicado
```bash
curl -X POST http://localhost:8080/api/cuentas \
  -H "Content-Type: application/json" \
  -d '{
    "numeroCuenta": "0001-0001",
    "saldoInicial": 100.00,
    "clienteId": 1
  }'
```

---

## Flujo recomendado para la demo en vivo

Ejecutar **en este orden** para que la audiencia vea el ciclo completo:

1. **Listar clientes** → ya hay 3 cargados desde `data.sql`
2. **Crear cliente Lucia** → mostrar el INSERT en consola de Hibernate
3. **Crear cuenta para Lucia** → mostrar el INSERT con la FK al nuevo cliente
4. **Listar cuentas paginadas del cliente 1** → mostrar el SQL con LIMIT y ORDER BY
5. **DEPOSITO en cuenta 1** → mostrar UPDATE del saldo + INSERT del movimiento
6. **Saldo total del cliente 1** → mostrar SELECT SUM (proyección JPQL)
7. **Top cuentas sobre el promedio** → mostrar la NATIVE QUERY
8. **Transferir cuenta 2 → cuenta 3** → resaltar que TODO ocurre en una transacción
9. **RETIRO con saldo insuficiente** → mostrar el GlobalExceptionHandler en acción (422)
10. **Validación inválida en POST cliente** → mostrar respuesta 400 con detalle por campo
11. **(Si activaron `db/postgres-extras.sql`)**: ir a pgAdmin y ejecutar:
    ```sql
    SELECT * FROM auditoria_saldos ORDER BY cambiado_en DESC;
    SELECT * FROM v_cuentas_completas;
    SELECT * FROM fn_resumen_cliente(1);
    ```
    Para mostrar trigger, vista y función SP funcionando.

---

## Cómo importar en Postman

1. Abrir Postman
2. **File → Import** (o Ctrl+O)
3. Arrastrar el archivo `expo-jpa.postman_collection.json`
4. La colección aparece en el sidebar con los 5 grupos
5. Verificar que la variable `{{baseUrl}}` apunta a `http://localhost:8080` (Variables → Edit)

## Cómo importar en Insomnia

1. **Application → Preferences → Data → Import Data → From File**
2. Seleccionar el mismo `expo-jpa.postman_collection.json` (Insomnia entiende el formato Postman v2.1)

## Cómo importar en Bruno (alternativa open-source)

Bruno también soporta importar Postman v2.1: `Collections → Import Collection → Postman Collection`.
