import { FormEvent, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { clientesApi } from '../api/clientes';
import { cuentasApi } from '../api/cuentas';
import { extractError } from '../api/client';
import type {
  ClienteDto,
  CuentaDto,
  CrearMovimientoRequest,
  TipoMovimiento,
} from '../types';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';
import { formatDate, formatMoney } from '../utils/format';

const TIPOS: TipoMovimiento[] = [
  'DEPOSITO',
  'RETIRO',
  'TRANSFERENCIA_ENTRANTE',
  'TRANSFERENCIA_SALIENTE',
  'PAGO_SERVICIO',
];

export function CuentasPage() {
  const [params, setParams] = useSearchParams();
  const clienteIdParam = params.get('cliente');
  const clienteId = clienteIdParam ? Number(clienteIdParam) : null;

  const [clientes, setClientes] = useState<ClienteDto[]>([]);
  const [cuentas, setCuentas] = useState<CuentaDto[]>([]);
  const [page, setPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [saldoTotal, setSaldoTotal] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const [crearOpen, setCrearOpen] = useState(false);
  const [crearForm, setCrearForm] = useState({ numeroCuenta: '', saldoInicial: '0' });
  const [saving, setSaving] = useState(false);

  const [movOpen, setMovOpen] = useState(false);
  const [cuentaSel, setCuentaSel] = useState<CuentaDto | null>(null);
  const [movForm, setMovForm] = useState<{
    monto: string;
    tipo: TipoMovimiento;
    descripcion: string;
  }>({ monto: '', tipo: 'DEPOSITO', descripcion: '' });

  const { show } = useToast();

  // Cargar lista de clientes para el selector.
  useEffect(() => {
    clientesApi.listar().then(setClientes).catch(e => show(extractError(e), 'error'));
  }, [show]);

  const cargarCuentas = (cid: number, p = 0) => {
    setLoading(true);
    Promise.all([cuentasApi.porCliente(cid, p, 10), cuentasApi.saldoTotal(cid)])
      .then(([pageData, total]) => {
        setCuentas(pageData.content);
        setPage(pageData.number);
        setTotalPages(pageData.totalPages);
        setSaldoTotal(total);
      })
      .catch(e => show(extractError(e), 'error'))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    if (clienteId == null) {
      setCuentas([]);
      setSaldoTotal(null);
      return;
    }
    cargarCuentas(clienteId, 0);
  }, [clienteId]); // eslint-disable-line react-hooks/exhaustive-deps

  const cambiarCliente = (cid: string) => {
    if (!cid) {
      params.delete('cliente');
    } else {
      params.set('cliente', cid);
    }
    setParams(params);
  };

  const crearCuenta = async (e: FormEvent) => {
    e.preventDefault();
    if (clienteId == null) return;
    setSaving(true);
    try {
      await cuentasApi.crear({
        numeroCuenta: crearForm.numeroCuenta,
        saldoInicial: Number(crearForm.saldoInicial),
        clienteId,
      });
      show('Cuenta creada');
      setCrearOpen(false);
      setCrearForm({ numeroCuenta: '', saldoInicial: '0' });
      cargarCuentas(clienteId, page);
    } catch (err) {
      show(extractError(err), 'error');
    } finally {
      setSaving(false);
    }
  };

  const abrirMovimiento = (c: CuentaDto) => {
    setCuentaSel(c);
    setMovForm({ monto: '', tipo: 'DEPOSITO', descripcion: '' });
    setMovOpen(true);
  };

  const registrarMov = async (e: FormEvent) => {
    e.preventDefault();
    if (!cuentaSel || clienteId == null) return;
    setSaving(true);
    try {
      const payload: CrearMovimientoRequest = {
        monto: Number(movForm.monto),
        tipo: movForm.tipo,
        descripcion: movForm.descripcion || undefined,
      };
      await cuentasApi.registrarMovimiento(cuentaSel.id, payload);
      show('Movimiento registrado');
      setMovOpen(false);
      cargarCuentas(clienteId, page);
    } catch (err) {
      show(extractError(err), 'error');
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <h2>Cuentas</h2>

      <div className="card">
        <div className="row">
          <label style={{ flex: 1, maxWidth: 400 }}>
            <span style={{ fontSize: 13, color: 'var(--muted)' }}>Cliente</span>
            <select
              value={clienteId ?? ''}
              onChange={e => cambiarCliente(e.target.value)}
            >
              <option value="">— Seleccionar cliente —</option>
              {clientes.map(c => (
                <option key={c.id} value={c.id!}>
                  {c.nombres} {c.apellidos} (DNI {c.dni})
                </option>
              ))}
            </select>
          </label>
          <div className="spacer" />
          {clienteId != null && (
            <button className="primary" onClick={() => setCrearOpen(true)}>
              + Nueva cuenta
            </button>
          )}
        </div>
      </div>

      {clienteId == null ? (
        <div className="card empty">Elegí un cliente para ver sus cuentas.</div>
      ) : (
        <>
          <div className="row" style={{ marginBottom: 20 }}>
            <div className="kpi">
              <div className="label">Saldo total del cliente</div>
              <div className="value">
                {saldoTotal == null ? '—' : formatMoney(saldoTotal)}
              </div>
            </div>
            <div className="kpi">
              <div className="label">Cuentas en esta página</div>
              <div className="value">{cuentas.length}</div>
            </div>
          </div>

          <div className="card">
            <h3>Cuentas (orden: saldo desc)</h3>
            {loading ? (
              <div className="empty">Cargando…</div>
            ) : cuentas.length === 0 ? (
              <div className="empty">El cliente no tiene cuentas todavía.</div>
            ) : (
              <>
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Nº Cuenta</th>
                      <th>Apertura</th>
                      <th style={{ textAlign: 'right' }}>Saldo</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {cuentas.map(c => (
                      <tr key={c.id}>
                        <td>{c.id}</td>
                        <td><strong>{c.numeroCuenta}</strong></td>
                        <td>{formatDate(c.fechaApertura)}</td>
                        <td style={{ textAlign: 'right' }}>{formatMoney(c.saldo)}</td>
                        <td>
                          <button onClick={() => abrirMovimiento(c)}>
                            Registrar movimiento
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                {totalPages > 1 && (
                  <div className="row" style={{ marginTop: 12, justifyContent: 'flex-end' }}>
                    <button
                      disabled={page === 0}
                      onClick={() => cargarCuentas(clienteId, page - 1)}
                    >
                      ← Anterior
                    </button>
                    <span style={{ color: 'var(--muted)', fontSize: 13 }}>
                      Página {page + 1} de {totalPages}
                    </span>
                    <button
                      disabled={page + 1 >= totalPages}
                      onClick={() => cargarCuentas(clienteId, page + 1)}
                    >
                      Siguiente →
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </>
      )}

      <Modal
        open={crearOpen}
        title="Nueva cuenta"
        onClose={() => setCrearOpen(false)}
      >
        <form onSubmit={crearCuenta}>
          <div className="form-grid">
            <label className="full">
              Número de cuenta
              <input
                required
                value={crearForm.numeroCuenta}
                onChange={e => setCrearForm({ ...crearForm, numeroCuenta: e.target.value })}
              />
            </label>
            <label className="full">
              Saldo inicial
              <input
                required
                type="number"
                step="0.01"
                min="0"
                value={crearForm.saldoInicial}
                onChange={e => setCrearForm({ ...crearForm, saldoInicial: e.target.value })}
              />
            </label>
          </div>
          <div className="row" style={{ marginTop: 20, justifyContent: 'flex-end' }}>
            <button type="button" onClick={() => setCrearOpen(false)}>Cancelar</button>
            <button className="primary" type="submit" disabled={saving}>
              {saving ? 'Guardando…' : 'Crear'}
            </button>
          </div>
        </form>
      </Modal>

      <Modal
        open={movOpen}
        title={cuentaSel ? `Movimiento — Cuenta ${cuentaSel.numeroCuenta}` : 'Movimiento'}
        onClose={() => setMovOpen(false)}
      >
        {cuentaSel && (
          <form onSubmit={registrarMov}>
            <div style={{ marginBottom: 12, fontSize: 13, color: 'var(--muted)' }}>
              Saldo actual: <strong style={{ color: 'var(--text)' }}>
                {formatMoney(cuentaSel.saldo)}
              </strong>
            </div>
            <div className="form-grid">
              <label>
                Tipo
                <select
                  value={movForm.tipo}
                  onChange={e =>
                    setMovForm({ ...movForm, tipo: e.target.value as TipoMovimiento })
                  }
                >
                  {TIPOS.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </label>
              <label>
                Monto
                <input
                  required
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={movForm.monto}
                  onChange={e => setMovForm({ ...movForm, monto: e.target.value })}
                />
              </label>
              <label className="full">
                Descripción (opcional)
                <input
                  maxLength={200}
                  value={movForm.descripcion}
                  onChange={e => setMovForm({ ...movForm, descripcion: e.target.value })}
                />
              </label>
            </div>
            <div className="row" style={{ marginTop: 20, justifyContent: 'flex-end' }}>
              <button type="button" onClick={() => setMovOpen(false)}>Cancelar</button>
              <button className="primary" type="submit" disabled={saving}>
                {saving ? 'Guardando…' : 'Registrar'}
              </button>
            </div>
          </form>
        )}
      </Modal>
    </>
  );
}
