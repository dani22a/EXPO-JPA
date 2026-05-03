// Formato de moneda PEN para vistas — el backend devuelve BigDecimal serializado como number.
const fmt = new Intl.NumberFormat('es-PE', {
  style: 'currency',
  currency: 'PEN',
  minimumFractionDigits: 2,
});

export const formatMoney = (n: number | string) => fmt.format(Number(n));

export const formatDate = (iso: string) => {
  const d = new Date(iso);
  return d.toLocaleString('es-PE', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
};
