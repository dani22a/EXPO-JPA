// Tipos espejo de los DTOs del backend Spring Boot.
// Cualquier cambio en los DTOs Java debería reflejarse acá.

export interface ClienteDto {
  id: number | null;
  nombres: string;
  apellidos: string;
  dni: string;
  email: string;
}

export interface CuentaDto {
  id: number;
  numeroCuenta: string;
  saldo: number;
  fechaApertura: string; // ISO LocalDateTime
  clienteId: number;
  clienteNombreCompleto: string;
}

export interface CrearCuentaRequest {
  numeroCuenta: string;
  saldoInicial: number;
  clienteId: number;
}

export type TipoMovimiento =
  | 'DEPOSITO'
  | 'RETIRO'
  | 'TRANSFERENCIA_ENTRANTE'
  | 'TRANSFERENCIA_SALIENTE'
  | 'PAGO_SERVICIO';

export interface MovimientoDto {
  id: number;
  monto: number;
  tipo: TipoMovimiento;
  descripcion: string | null;
  fecha: string;
  cuentaId: number;
}

export interface CrearMovimientoRequest {
  monto: number;
  tipo: TipoMovimiento;
  descripcion?: string;
}

export interface TransferenciaRequest {
  origenId: number;
  destinoId: number;
  monto: number;
}

// Página de Spring Data
export interface SpringPage<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  number: number;
  size: number;
  first: boolean;
  last: boolean;
}

// Estructura del GlobalExceptionHandler
export interface ApiError {
  timestamp: string;
  status: number;
  error: string;
  detalle?: Record<string, string> | null;
}
