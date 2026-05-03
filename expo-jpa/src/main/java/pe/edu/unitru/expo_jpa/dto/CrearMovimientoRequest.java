package pe.edu.unitru.expo_jpa.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import jakarta.validation.constraints.Size;
import pe.edu.unitru.expo_jpa.entities.TipoMovimiento;

import java.math.BigDecimal;

// Payload para registrar un movimiento.
// La cuenta se pasa por URL (path variable), no en el body.
public record CrearMovimientoRequest(
    @NotNull @Positive BigDecimal monto,                 // estrictamente > 0
    @NotNull TipoMovimiento tipo,                        // enum: DEPOSITO, RETIRO...
    @Size(max = 200) String descripcion                  // opcional
) {}
