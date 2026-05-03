package pe.edu.unitru.expo_jpa.entities;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import lombok.*;

import java.util.HashSet;
import java.util.Set;

// Entidad simple para mostrar el LADO INVERSO de la relación M-N.
@Entity
@Table(name = "productos")
@Getter @Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Producto {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "productos_seq")
    @SequenceGenerator(name = "productos_seq", sequenceName = "productos_id_seq", allocationSize = 1)
    private Long id;

    @NotBlank
    @Column(nullable = false, unique = true, length = 80)
    private String nombre;

    @Column(length = 250)
    private String descripcion;

    // LADO INVERSO de la M-N: NO lleva @JoinTable, solo mappedBy.
    // mappedBy apunta al campo "productos" en Cuenta (que es el lado dueño).
    @ManyToMany(mappedBy = "productos", fetch = FetchType.LAZY)
    @Builder.Default
    private Set<Cuenta> cuentas = new HashSet<>();
}
