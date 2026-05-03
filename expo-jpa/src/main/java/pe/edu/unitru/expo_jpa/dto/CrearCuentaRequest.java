package pe.edu.unitru.expo_jpa.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

import java.math.BigDecimal;

// DTO de ENTRADA específico para crear cuenta.
// Separar entrada y salida es una buena práctica: la entrada no necesita "id" ni "fechaApertura".
public record CrearCuentaRequest(
    @NotBlank String numeroCuenta,
    @NotNull @PositiveOrZero BigDecimal saldoInicial,    // permite 0
    @NotNull Long clienteId
) {}
