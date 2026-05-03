package pe.edu.unitru.expo_jpa.exceptions;

// Excepción de dominio: un recurso solicitado por id no existe.
// Se mapea a HTTP 404 en GlobalExceptionHandler.
// RuntimeException -> hace ROLLBACK automático de la transacción.
public class RecursoNoEncontradoException extends RuntimeException {
    public RecursoNoEncontradoException(String recurso, Object id) {
        super("%s con id %s no existe".formatted(recurso, id));
    }
}
