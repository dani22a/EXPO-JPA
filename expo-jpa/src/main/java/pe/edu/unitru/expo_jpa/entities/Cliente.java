package pe.edu.unitru.expo_jpa.entities;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

// @Entity: marca la clase como entidad JPA (se mapeará a una tabla).
// @Table: define el nombre de la tabla y los índices a crear.
@Entity
@Table(
    name = "clientes",
    indexes = {
        // Índice único para acelerar búsquedas por DNI y prevenir duplicados.
        @Index(name = "idx_cliente_dni", columnList = "dni", unique = true),
        // Índice no-único para queries por email.
        @Index(name = "idx_cliente_email", columnList = "email")
    }
)
// Lombok: genera getters/setters/constructores. Evita boilerplate.
// OJO: NO usar @Data en entidades bidireccionales (rompe equals/hashCode/toString por ciclos).
@Getter @Setter
@NoArgsConstructor          // requerido por JPA: instancia entidades por reflexión
@AllArgsConstructor
@Builder
public class Cliente {

    // Clave primaria. SEQUENCE es la estrategia recomendada en PostgreSQL
    // (permite que Hibernate batchee inserts; IDENTITY lo deshabilita).
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "clientes_seq")
    @SequenceGenerator(name = "clientes_seq", sequenceName = "clientes_id_seq", allocationSize = 1)
    private Long id;

    // Validaciones Bean Validation: se aplican en controllers con @Valid.
    @NotBlank
    @Size(max = 100)
    @Column(nullable = false, length = 100)
    private String nombres;

    @NotBlank
    @Size(max = 100)
    @Column(nullable = false, length = 100)
    private String apellidos;

    // unique=true crea constraint UNIQUE en la BD (además del índice).
    @NotBlank
    @Size(min = 8, max = 8)
    @Column(nullable = false, unique = true, length = 8)
    private String dni;

    @Email
    @Column(length = 150)
    private String email;

    // updatable=false: la columna se setea en INSERT y nunca más se actualiza.
    @Column(name = "fecha_registro", nullable = false, updatable = false)
    private LocalDateTime fechaRegistro;

    // ============================================================
    // RELACIÓN 1-N: un cliente tiene muchas cuentas.
    //   - mappedBy: el LADO DUEÑO de la relación es Cuenta.cliente.
    //     (acá no hay FK física; vive en la tabla "cuentas")
    //   - cascade ALL: si guardo/borro un cliente, sus cuentas siguen.
    //   - orphanRemoval: si quito una cuenta de la lista, se BORRA.
    //   - LAZY: las cuentas no se cargan hasta que las accedas (default en colecciones).
    // ============================================================
    @OneToMany(
        mappedBy = "cliente",
        cascade = CascadeType.ALL,
        orphanRemoval = true,
        fetch = FetchType.LAZY
    )
    @Builder.Default                 // Lombok: inicializa la lista al usar Builder
    private List<Cuenta> cuentas = new ArrayList<>();

    // Callback de ciclo de vida: se ejecuta ANTES de hacer INSERT.
    @PrePersist
    void onCreate() {
        this.fechaRegistro = LocalDateTime.now();
    }

    // Helper bidireccional: mantiene SINCRONIZADOS ambos lados de la relación.
    // Sin esto, podés persistir bien pero la entidad en memoria queda inconsistente.
    public void agregarCuenta(Cuenta cuenta) {
        cuentas.add(cuenta);
        cuenta.setCliente(this);
    }

    public void quitarCuenta(Cuenta cuenta) {
        cuentas.remove(cuenta);
        cuenta.setCliente(null);
    }
}
