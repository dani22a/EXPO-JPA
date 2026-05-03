package pe.edu.unitru.expo_jpa.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;

import java.math.BigDecimal;

public record CrearCuentaRequest(
    @NotBlank String numeroCuenta,
    @NotNull @PositiveOrZero BigDecimal saldoInicial,
    @NotNull Long clienteId
) {}
