package pe.edu.unitru.expo_jpa.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;
import pe.edu.unitru.expo_jpa.entities.TipoMovimiento;

import java.math.BigDecimal;

public record CrearMovimientoRequest(
    @NotNull @Positive BigDecimal monto,
    @NotNull TipoMovimiento tipo,
    @Size(max = 200) String descripcion
) {}
