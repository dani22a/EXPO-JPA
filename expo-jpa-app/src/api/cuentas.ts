import { api } from './client';
import type {
  CuentaDto,
  CrearCuentaRequest,
  CrearMovimientoRequest,
  MovimientoDto,
  SpringPage,
  TransferenciaRequest,
} from '../types';

export const cuentasApi = {
  obtener: (id: number) => api.get<CuentaDto>(`/api/cuentas/${id}`).then(r => r.data),

  porCliente: (clienteId: number, page = 0, size = 10) =>
    api
      .get<SpringPage<CuentaDto>>(`/api/cuentas/cliente/${clienteId}`, {
        params: { page, size, sort: 'saldo,desc' },
      })
      .then(r => r.data),

  saldoTotal: (clienteId: number) =>
    api
      .get<{ saldoTotal: number }>(`/api/cuentas/cliente/${clienteId}/saldo-total`)
      .then(r => r.data.saldoTotal),

  top: (limite = 5) =>
    api.get<CuentaDto[]>('/api/cuentas/top', { params: { limite } }).then(r => r.data),

  crear: (req: CrearCuentaRequest) =>
    api.post<CuentaDto>('/api/cuentas', req).then(r => r.data),

  registrarMovimiento: (cuentaId: number, req: CrearMovimientoRequest) =>
    api
      .post<MovimientoDto>(`/api/cuentas/${cuentaId}/movimientos`, req)
      .then(r => r.data),

  transferir: (req: TransferenciaRequest) =>
    api.post<void>('/api/cuentas/transferir', req).then(() => undefined),
};
