package pe.edu.unitru.expo_jpa.entities;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(
    name = "movimientos",
    indexes = {
        // Índice compuesto: optimiza "movimientos de una cuenta ordenados por fecha".
        @Index(name = "idx_mov_cuenta_fecha", columnList = "cuenta_id, fecha DESC"),
        // Índice para filtros por tipo (DEPOSITO, RETIRO, etc.).
        @Index(name = "idx_mov_tipo", columnList = "tipo")
    }
)
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Movimiento {

    // allocationSize=50: Hibernate reserva 50 IDs por vez.
    // Útil cuando insertás muchos movimientos seguidos -> menos roundtrips a la BD.
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "movimientos_seq")
    @SequenceGenerator(name = "movimientos_seq", sequenceName = "movimientos_id_seq", allocationSize = 50)
    private Long id;

    @NotNull
    @Positive                  // > 0; @PositiveOrZero permitiría 0
    @Column(nullable = false, precision = 19, scale = 2)
    private BigDecimal monto;

    // EnumType.STRING: guarda "DEPOSITO" en la BD.
    // NUNCA usar ORDINAL: si reordenás el enum, los datos viejos se corrompen.
    @NotNull
    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 30)
    private TipoMovimiento tipo;

    @Column(length = 200)
    private String descripcion;

    @Column(nullable = false, updatable = false)
    private LocalDateTime fecha;

    // Lado dueño de la relación N-1 con Cuenta (la FK cuenta_id vive aquí).
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "cuenta_id", nullable = false)
    private Cuenta cuenta;

    // Setea la fecha automáticamente antes de persistir.
    @PrePersist
    void onCreate() {
        this.fecha = LocalDateTime.now();
    }
}
