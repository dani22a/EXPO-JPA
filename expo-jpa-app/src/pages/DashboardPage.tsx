import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { cuentasApi } from '../api/cuentas';
import { clientesApi } from '../api/clientes';
import { extractError } from '../api/client';
import type { CuentaDto, ClienteDto } from '../types';
import { formatMoney } from '../utils/format';
import { useToast } from '../components/Toast';

export function DashboardPage() {
  const [topCuentas, setTopCuentas] = useState<CuentaDto[]>([]);
  const [clientes, setClientes] = useState<ClienteDto[]>([]);
  const [limite, setLimite] = useState(5);
  const [loading, setLoading] = useState(true);
  const { show } = useToast();

  useEffect(() => {
    setLoading(true);
    Promise.all([cuentasApi.top(limite), clientesApi.listar()])
      .then(([t, c]) => {
        setTopCuentas(t);
        setClientes(c);
      })
      .catch(e => show(extractError(e), 'error'))
      .finally(() => setLoading(false));
  }, [limite, show]);

  const totalSistema = topCuentas.reduce((acc, c) => acc + Number(c.saldo), 0);

  return (
    <>
      <h2>Dashboard</h2>

      <div className="row" style={{ marginBottom: 20 }}>
        <div className="kpi">
          <div className="label">Clientes registrados</div>
          <div className="value">{clientes.length}</div>
        </div>
        <div className="kpi">
          <div className="label">Top {limite} — saldo acumulado</div>
          <div className="value">{formatMoney(totalSistema)}</div>
        </div>
        <div className="kpi">
          <div className="label">Cuentas en TOP</div>
          <div className="value">{topCuentas.length}</div>
        </div>
      </div>

      <div className="card">
        <div className="row" style={{ marginBottom: 12 }}>
          <h3 style={{ margin: 0 }}>Top cuentas con mayor saldo</h3>
          <div className="spacer" />
          <label style={{ color: 'var(--muted)', fontSize: 13 }}>Límite:</label>
          <select
            value={limite}
            onChange={e => setLimite(Number(e.target.value))}
            style={{ width: 80 }}
          >
            <option value={3}>3</option>
            <option value={5}>5</option>
            <option value={10}>10</option>
            <option value={20}>20</option>
          </select>
        </div>

        {loading ? (
          <div className="empty">Cargando…</div>
        ) : topCuentas.length === 0 ? (
          <div className="empty">No hay cuentas todavía.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Nº Cuenta</th>
                <th>Cliente</th>
                <th style={{ textAlign: 'right' }}>Saldo</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {topCuentas.map((c, i) => (
                <tr key={c.id}>
                  <td>{i + 1}</td>
                  <td><strong>{c.numeroCuenta}</strong></td>
                  <td>{c.clienteNombreCompleto}</td>
                  <td style={{ textAlign: 'right' }}>{formatMoney(c.saldo)}</td>
                  <td>
                    <Link to={`/cuentas?cliente=${c.clienteId}`}>Ver cuentas →</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
