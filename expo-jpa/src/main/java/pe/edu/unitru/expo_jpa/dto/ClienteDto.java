package pe.edu.unitru.expo_jpa.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

// Record (Java 14+): clase inmutable con getters automáticos.
// DTO = Data Transfer Object: lo que viaja entre capas y al cliente HTTP.
// Usar DTO en vez de la entidad evita exponer relaciones internas y errores de serialización.
public record ClienteDto(
    Long id,                                                // null al crear, presente al devolver
    @NotBlank @Size(max = 100) String nombres,              // validaciones aplicadas con @Valid
    @NotBlank @Size(max = 100) String apellidos,
    @NotBlank @Size(min = 8, max = 8) String dni,
    @Email String email
) {}
