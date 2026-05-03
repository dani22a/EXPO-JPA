import axios, { AxiosError } from 'axios';
import type { ApiError } from '../types';

// baseURL '' porque el proxy de Vite reenvía /api -> :8080 en dev.
// Para build de producción podrías setear VITE_API_URL.
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '',
  headers: { 'Content-Type': 'application/json' },
});

// Convierte AxiosError en mensaje legible aprovechando el GlobalExceptionHandler.
export function extractError(err: unknown): string {
  if (err instanceof AxiosError) {
    const data = err.response?.data as ApiError | undefined;
    if (data?.detalle && typeof data.detalle === 'object') {
      const campos = Object.entries(data.detalle)
        .map(([k, v]) => `${k}: ${v}`)
        .join(' · ');
      return `${data.error} → ${campos}`;
    }
    if (data?.error) return data.error;
    return err.message;
  }
  return 'Error desconocido';
}
