package pe.edu.unitru.expo_jpa.entities;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Entity
@Table(
    name = "cuentas",
    indexes = {
        // Búsqueda por número de cuenta es muy frecuente -> índice único.
        @Index(name = "idx_cuenta_numero", columnList = "numero_cuenta", unique = true),
        // FK indexada para acelerar JOINs con clientes.
        @Index(name = "idx_cuenta_cliente", columnList = "cliente_id")
    }
)
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Cuenta {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "cuentas_seq")
    @SequenceGenerator(name = "cuentas_seq", sequenceName = "cuentas_id_seq", allocationSize = 1)
    private Long id;

    @NotBlank
    @Column(name = "numero_cuenta", nullable = false, unique = true, length = 20)
    private String numeroCuenta;

    // BigDecimal para dinero (NUNCA double/float -> errores de redondeo).
    // precision=19, scale=2 -> hasta 17 dígitos enteros y 2 decimales.
    @NotNull
    @PositiveOrZero
    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal saldo;

    @Column(name = "fecha_apertura", nullable = false, updatable = false)
    private LocalDateTime fechaApertura;

    // ============================================================
    // RELACIÓN N-1: muchas cuentas pertenecen a UN cliente.
    //   - Este es el LADO DUEÑO (tiene la FK física: cliente_id).
    //   - LAZY explícito: por default @ManyToOne es EAGER, lo cual causa
    //     queries innecesarias. SIEMPRE poner LAZY a mano.
    //   - optional=false: la cuenta DEBE tener cliente (NOT NULL).
    // ============================================================
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "cliente_id", nullable = false)
    private Cliente cliente;

    // ============================================================
    // RELACIÓN 1-N: una cuenta tiene muchos movimientos.
    // mappedBy apunta al campo "cuenta" de Movimiento (lado dueño).
    // ============================================================
    @OneToMany(
        mappedBy = "cuenta",
        cascade = CascadeType.ALL,
        orphanRemoval = true,
        fetch = FetchType.LAZY
    )
    @Builder.Default
    private List<Movimiento> movimientos = new ArrayList<>();

    // ============================================================
    // RELACIÓN M-N: una cuenta puede tener varios productos
    //               y un producto puede estar en varias cuentas.
    //   - @JoinTable define la TABLA INTERMEDIA (cuentas_productos).
    //   - joinColumns: la FK de ESTE lado (cuenta_id).
    //   - inverseJoinColumns: la FK del OTRO lado (producto_id).
    //   - Set en lugar de List: evita duplicados y mejora performance.
    // ============================================================
    @ManyToMany(fetch = FetchType.LAZY)
    @JoinTable(
        name = "cuentas_productos",
        joinColumns = @JoinColumn(name = "cuenta_id"),
        inverseJoinColumns = @JoinColumn(name = "producto_id"),
        indexes = {
            @Index(name = "idx_cp_cuenta", columnList = "cuenta_id"),
            @Index(name = "idx_cp_producto", columnList = "producto_id")
        }
    )
    @Builder.Default
    private Set<Producto> productos = new HashSet<>();

    @PrePersist
    void onCreate() {
        this.fechaApertura = LocalDateTime.now();
        // Saldo por defecto cero si no se especificó.
        if (this.saldo == null) this.saldo = BigDecimal.ZERO;
    }

    // Helper bidireccional para mantener consistencia en memoria.
    public void agregarMovimiento(Movimiento mov) {
        movimientos.add(mov);
        mov.setCuenta(this);
    }
}
