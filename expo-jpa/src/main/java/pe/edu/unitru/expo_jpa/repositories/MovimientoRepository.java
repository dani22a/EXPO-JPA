package pe.edu.unitru.expo_jpa.repositories;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import pe.edu.unitru.expo_jpa.entities.Movimiento;
import pe.edu.unitru.expo_jpa.entities.TipoMovimiento;

import java.time.LocalDateTime;
import java.util.List;

public interface MovimientoRepository extends JpaRepository<Movimiento, Long> {

    // Derived query con paginación y ORDER BY embebido en el nombre.
    Page<Movimiento> findByCuentaIdOrderByFechaDesc(Long cuentaId, Pageable pageable);

    // Filtro combinado: cuenta + tipo de movimiento.
    List<Movimiento> findByCuentaIdAndTipo(Long cuentaId, TipoMovimiento tipo);

    // JPQL con BETWEEN para filtrar movimientos en un rango de fechas.
    @Query("""
           SELECT m FROM Movimiento m
           WHERE m.cuenta.id = :cuentaId
             AND m.fecha BETWEEN :desde AND :hasta
           """)
    List<Movimiento> entreFechas(
        @Param("cuentaId") Long cuentaId,
        @Param("desde") LocalDateTime desde,
        @Param("hasta") LocalDateTime hasta
    );
}
