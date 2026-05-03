package pe.edu.unitru.expo_jpa.entities;

// Enum simple. Se persiste como STRING (ver @Enumerated en Movimiento).
public enum TipoMovimiento {
    DEPOSITO,                   // suma al saldo
    RETIRO,                     // resta del saldo
    TRANSFERENCIA_ENTRANTE,     // suma (la origen ya descontó)
    TRANSFERENCIA_SALIENTE,     // resta (la destino ya sumará)
    PAGO_SERVICIO               // resta (luz, agua, etc.)
}
