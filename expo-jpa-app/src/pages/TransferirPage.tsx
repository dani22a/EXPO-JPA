import { FormEvent, useEffect, useState } from 'react';
import { cuentasApi } from '../api/cuentas';
import { extractError } from '../api/client';
import type { CuentaDto } from '../types';
import { useToast } from '../components/Toast';
import { formatMoney } from '../utils/format';

export function TransferirPage() {
  const [origenId, setOrigenId] = useState('');
  const [destinoId, setDestinoId] = useState('');
  const [monto, setMonto] = useState('');
  const [origen, setOrigen] = useState<CuentaDto | null>(null);
  const [destino, setDestino] = useState<CuentaDto | null>(null);
  const [saving, setSaving] = useState(false);
  const { show } = useToast();

  // Lookup en vivo cuando se ingresa un ID válido.
  const buscar = async (id: string, set: (c: CuentaDto | null) => void) => {
    if (!id || isNaN(Number(id))) {
      set(null);
      return;
    }
    try {
      const c = await cuentasApi.obtener(Number(id));
      set(c);
    } catch {
      set(null);
    }
  };

  useEffect(() => {
    const t = setTimeout(() => buscar(origenId, setOrigen), 300);
    return () => clearTimeout(t);
  }, [origenId]);

  useEffect(() => {
    const t = setTimeout(() => buscar(destinoId, setDestino), 300);
    return () => clearTimeout(t);
  }, [destinoId]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (origenId === destinoId) {
      show('Origen y destino no pueden ser la misma cuenta', 'error');
      return;
    }
    setSaving(true);
    try {
      await cuentasApi.transferir({
        origenId: Number(origenId),
        destinoId: Number(destinoId),
        monto: Number(monto),
      });
      show(`Transferencia de ${formatMoney(monto)} realizada`);
      setMonto('');
      // refrescar saldos
      buscar(origenId, setOrigen);
      buscar(destinoId, setDestino);
    } catch (err) {
      show(extractError(err), 'error');
    } finally {
      setSaving(false);
    }
  };

  const renderCuenta = (c: CuentaDto | null, idStr: string) => {
    if (!idStr) return null;
    if (!c) return <div className="error-msg">Cuenta no encontrada</div>;
    return (
      <div style={{ marginTop: 6, fontSize: 13 }}>
        <div>{c.clienteNombreCompleto}</div>
        <div style={{ color: 'var(--muted)' }}>
          Cuenta {c.numeroCuenta} · Saldo {formatMoney(c.saldo)}
        </div>
      </div>
    );
  };

  return (
    <>
      <h2>Transferir entre cuentas</h2>

      <div className="card" style={{ maxWidth: 640 }}>
        <form onSubmit={submit}>
          <div className="form-grid">
            <label>
              ID Cuenta Origen
              <input
                required
                type="number"
                min="1"
                value={origenId}
                onChange={e => setOrigenId(e.target.value)}
              />
              {renderCuenta(origen, origenId)}
            </label>
            <label>
              ID Cuenta Destino
              <input
                required
                type="number"
                min="1"
                value={destinoId}
                onChange={e => setDestinoId(e.target.value)}
              />
              {renderCuenta(destino, destinoId)}
            </label>
            <label className="full">
              Monto
              <input
                required
                type="number"
                step="0.01"
                min="0.01"
                value={monto}
                onChange={e => setMonto(e.target.value)}
              />
            </label>
          </div>
          <div className="row" style={{ marginTop: 20, justifyContent: 'flex-end' }}>
            <button
              className="primary"
              type="submit"
              disabled={saving || !origen || !destino}
            >
              {saving ? 'Procesando…' : 'Transferir'}
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
