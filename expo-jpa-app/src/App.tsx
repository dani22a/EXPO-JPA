import { Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { ToastProvider } from './components/Toast';
import { DashboardPage } from './pages/DashboardPage';
import { ClientesPage } from './pages/ClientesPage';
import { CuentasPage } from './pages/CuentasPage';
import { TransferirPage } from './pages/TransferirPage';

export default function App() {
  return (
    <ToastProvider>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="clientes" element={<ClientesPage />} />
          <Route path="cuentas" element={<CuentasPage />} />
          <Route path="transferir" element={<TransferirPage />} />
        </Route>
      </Routes>
    </ToastProvider>
  );
}
