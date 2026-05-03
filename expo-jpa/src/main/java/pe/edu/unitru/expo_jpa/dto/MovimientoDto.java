package pe.edu.unitru.expo_jpa.dto;

import pe.edu.unitru.expo_jpa.entities.TipoMovimiento;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record MovimientoDto(
    Long id,
    BigDecimal monto,
    TipoMovimiento tipo,
    String descripcion,
    LocalDateTime fecha,
    Long cuentaId
) {}
