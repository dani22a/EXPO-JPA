import { FormEvent, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { clientesApi } from '../api/clientes';
import { extractError } from '../api/client';
import type { ClienteDto } from '../types';
import { Modal } from '../components/Modal';
import { useToast } from '../components/Toast';

const EMPTY: Omit<ClienteDto, 'id'> = {
  nombres: '',
  apellidos: '',
  dni: '',
  email: '',
};

export function ClientesPage() {
  const [items, setItems] = useState<ClienteDto[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<Omit<ClienteDto, 'id'>>(EMPTY);
  const [saving, setSaving] = useState(false);
  const { show } = useToast();

  const cargar = () => {
    setLoading(true);
    clientesApi
      .listar()
      .then(setItems)
      .catch(e => show(extractError(e), 'error'))
      .finally(() => setLoading(false));
  };

  useEffect(cargar, []); // eslint-disable-line react-hooks/exhaustive-deps

  const abrirNuevo = () => {
    setEditingId(null);
    setForm(EMPTY);
    setModalOpen(true);
  };

  const abrirEditar = (c: ClienteDto) => {
    setEditingId(c.id!);
    setForm({ nombres: c.nombres, apellidos: c.apellidos, dni: c.dni, email: c.email });
    setModalOpen(true);
  };

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingId == null) {
        await clientesApi.crear(form);
        show('Cliente creado');
      } else {
        await clientesApi.actualizar(editingId, form);
        show('Cliente actualizado');
      }
      setModalOpen(false);
      cargar();
    } catch (err) {
      show(extractError(err), 'error');
    } finally {
      setSaving(false);
    }
  };

  const eliminar = async (c: ClienteDto) => {
    if (!confirm(`¿Eliminar a ${c.nombres} ${c.apellidos}?`)) return;
    try {
      await clientesApi.eliminar(c.id!);
      show('Cliente eliminado');
      cargar();
    } catch (err) {
      show(extractError(err), 'error');
    }
  };

  return (
    <>
      <div className="row" style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Clientes</h2>
        <div className="spacer" />
        <button className="primary" onClick={abrirNuevo}>+ Nuevo cliente</button>
      </div>

      <div className="card">
        {loading ? (
          <div className="empty">Cargando…</div>
        ) : items.length === 0 ? (
          <div className="empty">No hay clientes. Creá el primero.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>DNI</th>
                <th>Nombres</th>
                <th>Apellidos</th>
                <th>Email</th>
                <th>Cuentas</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {items.map(c => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.dni}</td>
                  <td>{c.nombres}</td>
                  <td>{c.apellidos}</td>
                  <td>{c.email || <span style={{ color: 'var(--muted)' }}>—</span>}</td>
                  <td><Link to={`/cuentas?cliente=${c.id}`}>Ver →</Link></td>
                  <td>
                    <div className="row" style={{ gap: 6 }}>
                      <button onClick={() => abrirEditar(c)}>Editar</button>
                      <button className="danger" onClick={() => eliminar(c)}>Eliminar</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal
        open={modalOpen}
        title={editingId == null ? 'Nuevo cliente' : `Editar cliente #${editingId}`}
        onClose={() => setModalOpen(false)}
      >
        <form onSubmit={guardar}>
          <div className="form-grid">
            <label>
              Nombres
              <input
                required
                maxLength={100}
                value={form.nombres}
                onChange={e => setForm({ ...form, nombres: e.target.value })}
              />
            </label>
            <label>
              Apellidos
              <input
                required
                maxLength={100}
                value={form.apellidos}
                onChange={e => setForm({ ...form, apellidos: e.target.value })}
              />
            </label>
            <label>
              DNI (8 dígitos)
              <input
                required
                minLength={8}
                maxLength={8}
                pattern="\d{8}"
                value={form.dni}
                onChange={e => setForm({ ...form, dni: e.target.value })}
              />
            </label>
            <label>
              Email
              <input
                type="email"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
              />
            </label>
          </div>
          <div className="row" style={{ marginTop: 20, justifyContent: 'flex-end' }}>
            <button type="button" onClick={() => setModalOpen(false)}>Cancelar</button>
            <button className="primary" type="submit" disabled={saving}>
              {saving ? 'Guardando…' : 'Guardar'}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
}
