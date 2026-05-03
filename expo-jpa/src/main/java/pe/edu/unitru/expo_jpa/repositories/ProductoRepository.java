package pe.edu.unitru.expo_jpa.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import pe.edu.unitru.expo_jpa.entities.Producto;

import java.util.Optional;

// Repositorio mínimo. JpaRepository ya trae todo el CRUD básico.
public interface ProductoRepository extends JpaRepository<Producto, Long> {

    // Derived query simple.
    Optional<Producto> findByNombre(String nombre);
}
