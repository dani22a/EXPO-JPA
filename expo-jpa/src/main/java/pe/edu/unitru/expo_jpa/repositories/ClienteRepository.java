package pe.edu.unitru.expo_jpa.repositories;

import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import pe.edu.unitru.expo_jpa.entities.Cliente;

import java.util.List;
import java.util.Optional;

// Spring Data genera la implementación en RUNTIME (proxy dinámico).
// JpaRepository<Entidad, TipoDelId> -> aporta save, findAll, findById, delete, etc.
public interface ClienteRepository extends JpaRepository<Cliente, Long> {

    // DERIVED QUERY: Spring parsea el nombre del método y arma la query.
    // findBy + Dni  ->  WHERE dni = ?
    Optional<Cliente> findByDni(String dni);

    // ContainingIgnoreCase  ->  WHERE LOWER(apellidos) LIKE LOWER('%fragmento%')
    List<Cliente> findByApellidosContainingIgnoreCase(String fragmento);

    // @EntityGraph: indica a JPA que cargue "cuentas" en la MISMA query
    // (evita el problema N+1 cuando vas a iterar cliente.getCuentas()).
    @EntityGraph(attributePaths = "cuentas")
    @Query("SELECT c FROM Cliente c WHERE c.id = :id")
    Optional<Cliente> findByIdConCuentas(@Param("id") Long id);
}
