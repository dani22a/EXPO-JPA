package pe.edu.unitru.expo_jpa.controllers;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import pe.edu.unitru.expo_jpa.dto.ClienteDto;
import pe.edu.unitru.expo_jpa.services.ClienteService;

import java.util.List;

// @RestController = @Controller + @ResponseBody (devuelve JSON, no vistas).
// @RequestMapping define el prefijo común de todos los endpoints.
@RestController
@RequestMapping("/api/clientes")
@RequiredArgsConstructor
public class ClienteController {

    private final ClienteService service;

    // GET /api/clientes
    @GetMapping
    public List<ClienteDto> listar() {
        return service.listar();
    }

    // GET /api/clientes/{id}  -> @PathVariable extrae el id de la URL.
    @GetMapping("/{id}")
    public ClienteDto obtener(@PathVariable Long id) {
        return service.obtener(id);
    }

    // POST /api/clientes  -> 201 Created.
    // @Valid dispara las validaciones del DTO (@NotBlank, @Email, etc.).
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public ClienteDto crear(@Valid @RequestBody ClienteDto dto) {
        return service.crear(dto);
    }

    // PUT /api/clientes/{id}  -> reemplazo del recurso.
    @PutMapping("/{id}")
    public ClienteDto actualizar(@PathVariable Long id, @Valid @RequestBody ClienteDto dto) {
        return service.actualizar(id, dto);
    }

    // DELETE /api/clientes/{id}  -> 204 No Content (sin body).
    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void eliminar(@PathVariable Long id) {
        service.eliminar(id);
    }
}
