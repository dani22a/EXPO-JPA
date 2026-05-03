# expo-jpa-app

Frontend Vite + React + TypeScript que consume el backend Spring Boot `expo-jpa`.

## Stack

- Vite 5 + React 18 + TypeScript
- React Router 6
- Axios
- CSS plano (sin frameworks)

## Estructura

```
src/
├── api/               # axios + endpoints (clientes, cuentas)
├── components/        # Layout, Modal, Toast
├── pages/             # Dashboard, Clientes, Cuentas, Transferir
├── types/             # interfaces espejo de los DTOs Java
├── utils/             # format moneda/fecha
├── App.tsx            # router
├── main.tsx           # bootstrap
└── index.css          # tema dark
```

## Funcionalidades

- **Dashboard** — KPIs + top N cuentas con mayor saldo (`GET /api/cuentas/top`).
- **Clientes** — CRUD completo (`GET/POST/PUT/DELETE /api/clientes`).
- **Cuentas** — Selector de cliente, listado paginado por cliente, saldo total, alta de cuenta y registro de movimientos (`GET /api/cuentas/cliente/{id}`, `GET /api/cuentas/cliente/{id}/saldo-total`, `POST /api/cuentas`, `POST /api/cuentas/{id}/movimientos`).
- **Transferir** — Lookup en vivo de cuentas origen/destino y transferencia atómica (`POST /api/cuentas/transferir`).
- Manejo uniforme de errores leyendo el `GlobalExceptionHandler` del backend.

## Cómo correr

1. Levantar el backend (puerto 8080):
   ```
   cd ../expo-jpa
   ./mvnw spring-boot:run
   ```

2. Instalar dependencias y arrancar el frontend:
   ```
   cd expo-jpa-app
   npm install
   npm run dev
   ```

3. Abrir <http://localhost:5173>.

## Proxy

`vite.config.ts` reenvía `/api/**` a `http://localhost:8080`. No hay que tocar CORS en el backend.

Para producción podés setear `VITE_API_URL=https://tu-backend.com` en un `.env`.
