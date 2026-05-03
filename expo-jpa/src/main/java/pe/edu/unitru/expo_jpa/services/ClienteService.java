package pe.edu.unitru.expo_jpa.services;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pe.edu.unitru.expo_jpa.dto.ClienteDto;
import pe.edu.unitru.expo_jpa.entities.Cliente;
import pe.edu.unitru.expo_jpa.exceptions.RecursoNoEncontradoException;
import pe.edu.unitru.expo_jpa.repositories.ClienteRepository;

import java.util.List;

// @Service: marca la clase como bean de la capa de negocio.
// @RequiredArgsConstructor: Lombok genera el constructor con los campos final
//                           (la inyección por constructor que ya conocemos).
// @Transactional(readOnly=true) a nivel de clase: por DEFECTO todos los métodos
//   son de solo lectura. Hibernate desactiva dirty checking -> mejor performance.
//   Los métodos que escriben sobreescriben con su propio @Transactional.
@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class ClienteService {

    private final ClienteRepository repo;

    // Lectura: usa el readOnly de la clase.
    public List<ClienteDto> listar() {
        return repo.findAll().stream().map(this::aDto).toList();
    }

    public ClienteDto obtener(Long id) {
        return aDto(buscar(id));
    }

    // Escritura: necesita transacción de lectura+escritura.
    @Transactional
    public ClienteDto crear(ClienteDto dto) {
        // Builder de Lombok: forma legible de construir entidades.
        Cliente cliente = Cliente.builder()
            .nombres(dto.nombres())
            .apellidos(dto.apellidos())
            .dni(dto.dni())
            .email(dto.email())
            .build();
        return aDto(repo.save(cliente));
    }

    @Transactional
    public ClienteDto actualizar(Long id, ClienteDto dto) {
        Cliente cliente = buscar(id);                // queda en estado MANAGED
        cliente.setNombres(dto.nombres());
        cliente.setApellidos(dto.apellidos());
        cliente.setEmail(dto.email());
        // No hace falta repo.save(): DIRTY CHECKING detecta los cambios y
        // genera el UPDATE automáticamente al hacer commit de la transacción.
        return aDto(cliente);
    }

    @Transactional
    public void eliminar(Long id) {
        Cliente cliente = buscar(id);
        // CascadeType.ALL en Cliente.cuentas borra cuentas y, en cascada,
        // los movimientos asociados (gracias a CascadeType.ALL en Cuenta.movimientos).
        repo.delete(cliente);
    }

    // Helper privado para no repetir el "or throw" en cada método.
    private Cliente buscar(Long id) {
        return repo.findById(id)
            .orElseThrow(() -> new RecursoNoEncontradoException("Cliente", id));
    }

    // Mapper manual entidad -> DTO (sin librerías externas como MapStruct).
    private ClienteDto aDto(Cliente c) {
        return new ClienteDto(c.getId(), c.getNombres(), c.getApellidos(), c.getDni(), c.getEmail());
    }
}
