package pe.edu.unitru.expo_jpa.exceptions;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

// @RestControllerAdvice: intercepta excepciones de TODOS los controllers.
// Centraliza el manejo de errores -> los controllers no necesitan try/catch.
@RestControllerAdvice
public class GlobalExceptionHandler {

    // Estructura uniforme para todas las respuestas de error.
    public record ErrorResponse(LocalDateTime timestamp, int status, String error, Object detalle) {}

    // Recurso no encontrado -> 404.
    @ExceptionHandler(RecursoNoEncontradoException.class)
    public ResponseEntity<ErrorResponse> noEncontrado(RecursoNoEncontradoException ex) {
        return build(HttpStatus.NOT_FOUND, ex.getMessage(), null);
    }

    // Regla de negocio violada -> 422.
    @ExceptionHandler(SaldoInsuficienteException.class)
    public ResponseEntity<ErrorResponse> saldoInsuficiente(SaldoInsuficienteException ex) {
        return build(HttpStatus.UNPROCESSABLE_ENTITY, ex.getMessage(), null);
    }

    // Validación de DTO (@Valid) falló -> 400 con detalle por campo.
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> validacion(MethodArgumentNotValidException ex) {
        Map<String, String> errores = new HashMap<>();
        // Recorre cada error de campo y lo convierte en { campo -> mensaje }.
        ex.getBindingResult().getFieldErrors().forEach(
            fe -> errores.put(fe.getField(), fe.getDefaultMessage())
        );
        return build(HttpStatus.BAD_REQUEST, "Validacion fallida", errores);
    }

    // Catch-all: cualquier otra excepción no contemplada -> 500.
    // En producción habría que loggear stacktrace y devolver mensaje genérico.
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorResponse> generico(Exception ex) {
        return build(HttpStatus.INTERNAL_SERVER_ERROR, ex.getMessage(), null);
    }

    // Helper: arma la respuesta uniformemente.
    private ResponseEntity<ErrorResponse> build(HttpStatus status, String msg, Object detalle) {
        return ResponseEntity.status(status).body(
            new ErrorResponse(LocalDateTime.now(), status.value(), msg, detalle)
        );
    }
}
