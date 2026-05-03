-- ============================================================
-- SCRIPT MANUAL — ejecutar en pgAdmin/DBeaver despues de la primera arrancada
-- (NO se ejecuta automaticamente; es material de exposicion)
--
-- Muestra:
--   1. Indices creados a mano (alternativa a @Index en JPA)
--   2. Una FUNCION (equivalente a stored procedure en Postgres)
--   3. Un VIEW para reportes
--   4. Un TRIGGER de auditoria
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- 1) INDICES adicionales (los basicos ya los crea JPA via @Index)
-- ────────────────────────────────────────────────────────────

-- Indice compuesto para acelerar busquedas por cliente + saldo
CREATE INDEX IF NOT EXISTS idx_cuenta_cliente_saldo
    ON cuentas (cliente_id, saldo DESC);

-- Indice parcial: solo indexa cuentas con saldo > 1000 (mas chico, mas rapido)
CREATE INDEX IF NOT EXISTS idx_cuenta_saldo_alto
    ON cuentas (saldo)
    WHERE saldo > 1000;

-- Indice de texto sobre apellidos para LIKE 'apellido%'
CREATE INDEX IF NOT EXISTS idx_cliente_apellidos_lower
    ON clientes (LOWER(apellidos) varchar_pattern_ops);


-- ────────────────────────────────────────────────────────────
-- 2) FUNCION (stored procedure en Postgres)
-- Devuelve resumen de un cliente: cuentas, saldo total, cant. movimientos
-- Llamada desde Java en CuentaRepository.resumenPorCliente()
-- ────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION fn_resumen_cliente(p_cliente_id BIGINT)
RETURNS TABLE (
    numero_cuenta   VARCHAR,
    saldo           NUMERIC,
    total_movimientos BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.numero_cuenta,
        c.saldo,
        COUNT(m.id) AS total_movimientos
    FROM cuentas c
    LEFT JOIN movimientos m ON m.cuenta_id = c.id
    WHERE c.cliente_id = p_cliente_id
    GROUP BY c.id, c.numero_cuenta, c.saldo
    ORDER BY c.saldo DESC;
END;
$$;

-- Uso desde SQL:
--   SELECT * FROM fn_resumen_cliente(1);


-- ────────────────────────────────────────────────────────────
-- 3) VIEW: reporte de cuentas con info del titular
-- ────────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW v_cuentas_completas AS
SELECT
    c.id              AS cuenta_id,
    c.numero_cuenta,
    c.saldo,
    cl.id             AS cliente_id,
    cl.nombres || ' ' || cl.apellidos AS titular,
    cl.dni,
    (SELECT COUNT(*) FROM movimientos m WHERE m.cuenta_id = c.id) AS cant_movimientos
FROM cuentas c
JOIN clientes cl ON cl.id = c.cliente_id;

-- Uso:
--   SELECT * FROM v_cuentas_completas WHERE saldo > 1000;


-- ────────────────────────────────────────────────────────────
-- 4) TRIGGER de auditoria: registra cambios de saldo
-- ────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS auditoria_saldos (
    id           BIGSERIAL PRIMARY KEY,
    cuenta_id    BIGINT NOT NULL,
    saldo_viejo  NUMERIC(19,2),
    saldo_nuevo  NUMERIC(19,2),
    cambiado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION fn_auditar_saldo()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.saldo IS DISTINCT FROM NEW.saldo THEN
        INSERT INTO auditoria_saldos(cuenta_id, saldo_viejo, saldo_nuevo)
        VALUES (NEW.id, OLD.saldo, NEW.saldo);
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_auditar_saldo ON cuentas;
CREATE TRIGGER trg_auditar_saldo
    AFTER UPDATE ON cuentas
    FOR EACH ROW
    EXECUTE FUNCTION fn_auditar_saldo();

-- Despues de hacer un POST a /api/cuentas/1/movimientos:
--   SELECT * FROM auditoria_saldos ORDER BY cambiado_en DESC;
