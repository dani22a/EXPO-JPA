import { api } from './client';
import type { ClienteDto } from '../types';

export const clientesApi = {
  listar: () => api.get<ClienteDto[]>('/api/clientes').then(r => r.data),
  obtener: (id: number) => api.get<ClienteDto>(`/api/clientes/${id}`).then(r => r.data),
  crear: (dto: Omit<ClienteDto, 'id'>) =>
    api.post<ClienteDto>('/api/clientes', dto).then(r => r.data),
  actualizar: (id: number, dto: Omit<ClienteDto, 'id'>) =>
    api.put<ClienteDto>(`/api/clientes/${id}`, dto).then(r => r.data),
  eliminar: (id: number) => api.delete(`/api/clientes/${id}`).then(() => undefined),
};
