package pe.edu.unitru.expo_jpa.repositories;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import pe.edu.unitru.expo_jpa.entities.Cuenta;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

// Repositorio que muestra TODOS los estilos de query disponibles en Spring Data.
public interface CuentaRepository extends JpaRepository<Cuenta, Long> {

    // ============================================================
    // 1) DERIVED QUERIES — el nombre del método define la query
    // ============================================================
    Optional<Cuenta> findByNumeroCuenta(String numero);

    List<Cuenta> findBySaldoGreaterThan(BigDecimal monto);

    // Page<T> + Pageable: paginación automática (page, size, sort).
    Page<Cuenta> findByClienteId(Long clienteId, Pageable pageable);

    // existsBy... -> SELECT COUNT más eficiente que findBy + isPresent.
    boolean existsByNumeroCuenta(String numero);

    // ============================================================
    // 2) JPQL — trabaja con ENTIDADES y CAMPOS, no con tablas/columnas
    //    Es portable entre motores (MySQL, Postgres, Oracle...).
    // ============================================================
    @Query("""
           SELECT c FROM Cuenta c
           WHERE c.cliente.dni = :dni
             AND c.saldo >= :minimo
           ORDER BY c.saldo DESC
           """)
    List<Cuenta> buscarPorDniConSaldoMinimo(
        @Param("dni") String dni,
        @Param("minimo") BigDecimal minimo
    );

    // PROYECCIÓN: trae solo el agregado, no la entidad completa.
    // COALESCE evita NULL si el cliente no tiene cuentas.
    @Query("SELECT COALESCE(SUM(c.saldo), 0) FROM Cuenta c WHERE c.cliente.id = :clienteId")
    BigDecimal sumarSaldosDeCliente(@Param("clienteId") Long clienteId);

    // ============================================================
    // 3) UPDATE / DELETE: requieren @Modifying.
    //    El service que las invoque debe tener @Transactional.
    // ============================================================
    @Modifying
    @Query("UPDATE Cuenta c SET c.saldo = c.saldo + :monto WHERE c.id = :id")
    int incrementarSaldo(@Param("id") Long id, @Param("monto") BigDecimal monto);

    // ============================================================
    // 4) NATIVE QUERY — SQL crudo de PostgreSQL.
    //    Útil cuando JPQL no alcanza (window functions, CTEs, JSON...).
    //    Costo: pierde portabilidad entre motores.
    // ============================================================
    @Query(
        value = """
                SELECT c.* FROM cuentas c
                WHERE c.saldo > (SELECT AVG(saldo) FROM cuentas)
                ORDER BY c.saldo DESC
                LIMIT :limite
                """,
        nativeQuery = true
    )
    List<Cuenta> topCuentasPorEncimaDelPromedio(@Param("limite") int limite);

    // ============================================================
    // 5) STORED PROCEDURE — llama a la función creada en postgres-extras.sql.
    //    Object[] porque el resultado tiene varias columnas heterogéneas.
    // ============================================================
    @Query(
        value = "SELECT * FROM fn_resumen_cliente(:clienteId)",
        nativeQuery = true
    )
    List<Object[]> resumenPorCliente(@Param("clienteId") Long clienteId);
}
