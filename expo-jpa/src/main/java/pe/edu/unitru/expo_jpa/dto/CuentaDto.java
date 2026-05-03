package pe.edu.unitru.expo_jpa.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

// DTO de salida: aplana la entidad Cuenta + datos del cliente para no
// devolver toda la entidad anidada (que arrastraría cuentas, movimientos, etc.).
public record CuentaDto(
    Long id,
    String numeroCuenta,
    BigDecimal saldo,
    LocalDateTime fechaApertura,
    Long clienteId,
    String clienteNombreCompleto
) {}
