package pe.edu.unitru.expo_jpa.dto;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record CuentaDto(
    Long id,
    String numeroCuenta,
    BigDecimal saldo,
    LocalDateTime fechaApertura,
    Long clienteId,
    String clienteNombreCompleto
) {}
