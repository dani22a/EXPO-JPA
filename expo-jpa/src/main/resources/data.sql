-- ============================================================
-- DATOS DE PRUEBA — se cargan despues de que Hibernate cree el esquema
-- (gracias a spring.jpa.defer-datasource-initialization=true)
-- ============================================================

INSERT INTO clientes (id, nombres, apellidos, dni, email, fecha_registro) VALUES
  (1, 'Daniel',  'Solano',   '70123456', 'daniel@example.com', CURRENT_TIMESTAMP),
  (2, 'Maria',   'Lopez',    '70234567', 'maria@example.com',  CURRENT_TIMESTAMP),
  (3, 'Carlos',  'Mendoza',  '70345678', 'carlos@example.com', CURRENT_TIMESTAMP);

INSERT INTO cuentas (id, numero_cuenta, saldo, fecha_apertura, cliente_id) VALUES
  (1, '0001-0001', 1500.00, CURRENT_TIMESTAMP, 1),
  (2, '0001-0002', 8200.50, CURRENT_TIMESTAMP, 1),
  (3, '0002-0001',  300.00, CURRENT_TIMESTAMP, 2),
  (4, '0003-0001', 12500.75, CURRENT_TIMESTAMP, 3);

INSERT INTO productos (id, nombre, descripcion) VALUES
  (1, 'Tarjeta Debito',  'Tarjeta de debito Visa'),
  (2, 'Tarjeta Credito', 'Tarjeta de credito Mastercard'),
  (3, 'Banca Movil',     'Acceso a app movil');

INSERT INTO cuentas_productos (cuenta_id, producto_id) VALUES
  (1, 1), (1, 3),
  (2, 1), (2, 2), (2, 3),
  (4, 2), (4, 3);

INSERT INTO movimientos (id, monto, tipo, descripcion, fecha, cuenta_id) VALUES
  (1, 500.00,  'DEPOSITO', 'Deposito inicial',          CURRENT_TIMESTAMP, 1),
  (2, 200.00,  'RETIRO',   'Retiro cajero',             CURRENT_TIMESTAMP, 1),
  (3, 1000.00, 'DEPOSITO', 'Sueldo',                    CURRENT_TIMESTAMP, 2),
  (4, 50.00,   'PAGO_SERVICIO', 'Pago de luz',          CURRENT_TIMESTAMP, 3);

-- Sincronizamos las secuencias para que los proximos INSERT
-- generados por Hibernate no choquen con los IDs cargados manualmente
SELECT setval('clientes_id_seq',     (SELECT MAX(id) FROM clientes));
SELECT setval('cuentas_id_seq',      (SELECT MAX(id) FROM cuentas));
SELECT setval('productos_id_seq',    (SELECT MAX(id) FROM productos));
SELECT setval('movimientos_id_seq',  (SELECT MAX(id) FROM movimientos));
