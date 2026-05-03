package pe.edu.unitru.expo_jpa.dto;

import pe.edu.unitru.expo_jpa.entities.TipoMovimiento;

import java.math.BigDecimal;
import java.time.LocalDateTime;

// DTO de salida para un movimiento (deposito, retiro, transferencia, etc.).
public record MovimientoDto(
    Long id,
    BigDecimal monto,
    TipoMovimiento tipo,
    String descripcion,
    LocalDateTime fecha,
    Long cuentaId
) {}
