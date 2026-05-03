package pe.edu.unitru.expo_jpa.exceptions;

// Excepción de regla de negocio: se intentó retirar más de lo disponible.
// Se mapea a HTTP 422 (Unprocessable Entity) en GlobalExceptionHandler.
public class SaldoInsuficienteException extends RuntimeException {
    public SaldoInsuficienteException(String mensaje) {
        super(mensaje);
    }
}
