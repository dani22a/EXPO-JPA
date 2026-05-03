# Datos adicionales y posibles preguntas (Q&A)

Material complementario para la exposicion de **Bases de Datos y Spring Data JPA**. Cubre conceptos avanzados, gotchas, y respuestas listas para preguntas que el tribunal puede tirar.

---

## 1. Relaciones entre entidades — la guia completa

### 1.1 Las 4 cardinalidades

| Cardinalidad | Anotacion | Ejemplo del proyecto |
|---|---|---|
| 1-1 | `@OneToOne` | (no usada) Cliente <-> Direccion principal |
| 1-N | `@OneToMany` | Cliente -> Cuentas |
| N-1 | `@ManyToOne` | Cuenta -> Cliente, Movimiento -> Cuenta |
| M-N | `@ManyToMany` | Cuenta <-> Producto (con tabla intermedia) |

### 1.2 Lado dueño vs lado inverso

En toda relacion bidireccional, **uno solo de los lados tiene la FK fisica** en la BD. Ese es el **lado dueño**. El otro es el **lado inverso** y lleva `mappedBy`.

- `@ManyToOne` siempre es lado dueño.
- En `@OneToMany` el dueño suele ser el lado `@ManyToOne`.
- En `@ManyToMany` cualquiera puede ser dueño; el otro lleva `mappedBy`.

**Regla de oro**: `mappedBy` apunta al **nombre del campo** del lado dueño, NO al nombre de la columna.

### 1.3 Helpers bidireccionales (por que existen)

```java
public void agregarCuenta(Cuenta cuenta) {
    cuentas.add(cuenta);
    cuenta.setCliente(this);   // mantenemos AMBOS lados sincronizados
}
```

Si solo seteas un lado, JPA persiste bien (porque mira al dueño) pero la entidad EN MEMORIA queda inconsistente. Cuando alguien lea `cliente.getCuentas()` sin recargar, le va a faltar la cuenta nueva.

### 1.4 Cascade types

| Tipo | Que hace |
|---|---|
| `PERSIST` | save() padre -> save() hijos |
| `MERGE`   | merge() padre -> merge() hijos |
| `REMOVE`  | delete() padre -> delete() hijos |
| `REFRESH` | refresh() padre -> refresh() hijos |
| `DETACH`  | detach() padre -> detach() hijos |
| `ALL`     | todos los anteriores |

**Cuidado**: `CascadeType.ALL` en `@ManyToMany` puede borrar cosas no deseadas. Usar con criterio.

### 1.5 `orphanRemoval`

```java
@OneToMany(mappedBy = "cliente", orphanRemoval = true)
private List<Cuenta> cuentas;
```

Si saco una cuenta de la lista, se BORRA de la BD. Sin `orphanRemoval`, solo se desasocia (queda con FK NULL si se permite). Util para colecciones "propiedad de" el padre.

### 1.6 Fetch: LAZY vs EAGER

| Tipo | Cuando carga | Default en |
|---|---|---|
| `LAZY` | Cuando accedes al campo | `@OneToMany`, `@ManyToMany` |
| `EAGER` | Junto con la entidad padre | `@ManyToOne`, `@OneToOne` |

**REGLA DE ORO**: `@ManyToOne(fetch = FetchType.LAZY)` SIEMPRE. Si no, cargar 100 cuentas trae 100 clientes "por las dudas" (memoria desperdiciada).

---

## 2. Indices: anotacion vs SQL manual

### 2.1 Via `@Index` (parte del esquema generado por Hibernate)

```java
@Table(
    name = "cuentas",
    indexes = {
        @Index(name = "idx_cuenta_numero", columnList = "numero_cuenta", unique = true),
        @Index(name = "idx_cuenta_cliente", columnList = "cliente_id")
    }
)
```

Hibernate los crea cuando aplica DDL. Limites:
- No se pueden hacer **indices parciales** (`WHERE`).
- No se puede elegir el tipo (`HASH`, `BRIN`, `GIN` en Postgres).
- No se puede usar **expresiones** (`LOWER(apellidos)`).

### 2.2 Via SQL manual (para indices avanzados)

Ver `src/main/resources/db/postgres-extras.sql`:

```sql
-- Indice parcial
CREATE INDEX idx_cuenta_saldo_alto ON cuentas (saldo) WHERE saldo > 1000;

-- Indice por expresion para LIKE 'apellido%'
CREATE INDEX idx_cliente_apellidos_lower ON clientes (LOWER(apellidos) varchar_pattern_ops);
```

En produccion estos van en migraciones (Flyway/Liquibase), NO en `data.sql`.

### 2.3 Cuando NO indexar

- Tablas chicas (< 1000 filas): el seq scan es mas rapido que usar indice.
- Columnas con baja cardinalidad (ej: booleano sex): indice no ayuda.
- Tablas de mucha escritura: cada indice ralentiza INSERT/UPDATE.

---

## 3. Stored Procedures / Functions en PostgreSQL

PostgreSQL tiene `FUNCTION` (devuelve algo) y `PROCEDURE` (no devuelve, soporta `COMMIT`/`ROLLBACK` interno desde PG 11).

### 3.1 Funcion de ejemplo (la del proyecto)

```sql
CREATE OR REPLACE FUNCTION fn_resumen_cliente(p_cliente_id BIGINT)
RETURNS TABLE (numero_cuenta VARCHAR, saldo NUMERIC, total_movimientos BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.numero_cuenta, c.saldo, COUNT(m.id)
    FROM cuentas c LEFT JOIN movimientos m ON m.cuenta_id = c.id
    WHERE c.cliente_id = p_cliente_id
    GROUP BY c.id;
END;
$$;
```

### 3.2 Llamarla desde JPA

**Opcion A — `@Query` nativo (la que usamos):**

```java
@Query(value = "SELECT * FROM fn_resumen_cliente(:id)", nativeQuery = true)
List<Object[]> resumenPorCliente(@Param("id") Long id);
```

**Opcion B — `@Procedure`:**

```java
@Procedure(name = "fn_resumen_cliente")
List<Object[]> resumenPorCliente(@Param("p_cliente_id") Long id);
```

Requiere mapear la procedure con `@NamedStoredProcedureQuery` en una entidad. Mas verboso, util para procedures con parametros OUT.

### 3.3 Cuando usar SP vs codigo Java

**A favor del SP**:
- Logica que toca muchas tablas con joins/agregaciones pesadas.
- Reduce ida-y-vuelta de red entre app y BD.
- DBA puede optimizar sin tocar la app.

**En contra**:
- Logica fragmentada entre Java y SQL (dificil de mantener).
- Tests mas complicados.
- Vendor lock-in (un SP de Postgres no corre en Oracle).

**Regla**: si lo podes hacer eficiente en JPQL, hacelo ahi. SP solo cuando el rendimiento lo justifica.

---

## 4. Transacciones y `@Transactional`

### 4.1 Lo que tenes que saber

```java
@Service
@Transactional(readOnly = true)        // default a nivel clase: solo lectura
public class CuentaService {

    @Transactional                      // sobreescribe: lectura + escritura
    public void transferir(...) { ... }
}
```

### 4.2 Propagation (los mas usados)

| Tipo | Que hace |
|---|---|
| `REQUIRED` (default) | Une la transaccion existente o crea una nueva |
| `REQUIRES_NEW` | SIEMPRE abre una nueva (suspende la actual) |
| `SUPPORTS` | Usa la existente si hay, sino corre sin transaccion |
| `MANDATORY` | Requiere que ya exista una; si no, error |
| `NESTED` | Savepoint dentro de la transaccion existente |

### 4.3 Isolation levels

| Nivel | Permite |
|---|---|
| `READ_UNCOMMITTED` | Lecturas sucias |
| `READ_COMMITTED` (default Postgres) | Solo lee datos commiteados |
| `REPEATABLE_READ` | La misma query devuelve lo mismo dentro de la TX |
| `SERIALIZABLE` | Como si las TX corrieran en serie |

### 4.4 Gotchas TIPICOS

- `@Transactional` **solo funciona en metodos publicos** llamados desde otro bean. Si lo llamas desde la misma clase (`this.metodoTx()`), Spring no aplica el proxy. RESPUESTA: refactorizar a otra clase.
- Excepciones **chequeadas no hacen rollback por default**. Solo las `RuntimeException`. Para forzar: `@Transactional(rollbackFor = Exception.class)`.
- `readOnly = true` no es solo metadata: Hibernate desactiva dirty checking (mejora performance).

---

## 5. El temido problema N+1

### 5.1 Que es

```java
List<Cliente> clientes = clienteRepo.findAll();  // 1 query
clientes.forEach(c -> System.out.println(c.getCuentas().size()));
// LAZY -> 1 query MAS por cada cliente -> N queries
// Total: N+1 queries
```

### 5.2 Soluciones

**A) `@EntityGraph`** (lo usamos en `ClienteRepository`):

```java
@EntityGraph(attributePaths = "cuentas")
@Query("SELECT c FROM Cliente c WHERE c.id = :id")
Optional<Cliente> findByIdConCuentas(@Param("id") Long id);
```

**B) `JOIN FETCH` en JPQL**:

```java
@Query("SELECT DISTINCT c FROM Cliente c LEFT JOIN FETCH c.cuentas")
List<Cliente> findAllConCuentas();
```

**C) `@BatchSize`** (Hibernate, agrupa los lazy en lotes):

```java
@OneToMany(mappedBy = "cliente")
@BatchSize(size = 20)
private List<Cuenta> cuentas;
```

### 5.3 Como detectarlo

Activar en `application.properties`:

```properties
logging.level.org.hibernate.SQL=DEBUG
spring.jpa.properties.hibernate.generate_statistics=true
```

Si ves muchas queries similares para una sola operacion HTTP, hay N+1.

---

## 6. Ciclo de vida de una entidad

```
                  persist()
   transient   ───────────►   managed
       ▲                          │
       │ new                      │ remove()
       │                          ▼
   detached   ◄──────────────  removed
              detach()/close()
```

| Estado | Significado |
|---|---|
| **transient** | Objeto recien creado con `new`, JPA no lo conoce |
| **managed** | JPA lo rastrea: cambios se persisten en commit |
| **detached** | Fue managed pero la sesion se cerro |
| **removed** | Marcado para borrar en el proximo flush |

**Implicancia**: si modificas un objeto detached, los cambios NO se persisten. Tenes que hacer `merge()` o recargarlo.

---

## 7. Validaciones (Bean Validation)

### 7.1 Anotaciones mas usadas

| Anotacion | Para que |
|---|---|
| `@NotNull` | No null |
| `@NotBlank` | No null, no vacio, no solo espacios (Strings) |
| `@NotEmpty` | No null, no vacio (collections, Strings, arrays) |
| `@Size(min, max)` | Longitud |
| `@Min`, `@Max` | Rango numerico |
| `@Positive`, `@Negative`, `@PositiveOrZero` | Signo |
| `@Email` | Formato email |
| `@Pattern(regexp = ...)` | Regex |
| `@Past`, `@Future` | Fechas |

### 7.2 Cuando se ejecutan

- En el controller: con `@Valid` en `@RequestBody`.
- En la entidad: solo si configuras `hibernate.validator.apply_to_ddl=true` (no por default).

Buena practica: validar en el DTO de entrada (records con anotaciones), NO en la entidad.

---

## 8. Consultas: cuando usar cada una

| Tipo | Cuando |
|---|---|
| **Derived** (`findByX`) | Filtros simples por 1-3 campos |
| **JPQL** (`@Query`) | Filtros complejos, joins, proyecciones |
| **Native SQL** | Window functions, CTEs, features especificos del motor |
| **Specifications** (Criteria) | Filtros dinamicos (busqueda con N filtros opcionales) |
| **QueryDSL** | Type-safety en queries dinamicas (libreria externa) |
| **Stored Procedure** | Logica pesada que vive mejor en la BD |

---

## 9. Auditoria automatica con Spring Data

Para evitar setear `fechaCreacion` y `fechaActualizacion` a mano:

```java
@EntityListeners(AuditingEntityListener.class)
public class Cliente {

    @CreatedDate
    private LocalDateTime fechaRegistro;

    @LastModifiedDate
    private LocalDateTime fechaActualizacion;

    @CreatedBy
    private String creadoPor;       // requiere AuditorAware<String>
}
```

Y en una `@Configuration`: `@EnableJpaAuditing`.

---

## 10. Migraciones de esquema (PRODUCCION)

`ddl-auto=update` esta BIEN para desarrollo. **JAMAS en produccion**. En produccion se usa:

- **Flyway** (mas simple, scripts SQL versionados: `V1__init.sql`, `V2__add_column.sql`)
- **Liquibase** (XML/YAML, mas potente, soporta rollback)

Spring Boot autoconfigura ambos solo agregando la dependencia. La spec `ddl-auto` se pone en `validate` y Hibernate verifica que el esquema coincida con las entidades.

---

## 11. Testing

### 11.1 `@DataJpaTest` — solo capa JPA

```java
@DataJpaTest
class CuentaRepositoryTest {

    @Autowired CuentaRepository repo;

    @Test
    void encuentraPorNumero() {
        Cuenta c = Cuenta.builder().numeroCuenta("0001").saldo(BigDecimal.TEN).build();
        repo.save(c);
        assertThat(repo.findByNumeroCuenta("0001")).isPresent();
    }
}
```

Por default usa H2 en memoria, transaccion auto-rollback al final del test. Rapido.

### 11.2 `@SpringBootTest` — contexto completo

Para tests de integracion. Mas lento. Combinar con **Testcontainers** para usar Postgres real:

```java
@Container
static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");
```

---

## 12. Errores tipicos y sus causas

| Error | Causa probable | Solucion |
|---|---|---|
| `LazyInitializationException` | Acceder a relacion lazy fuera de la TX | `@Transactional` o `JOIN FETCH` |
| `StackOverflowError` en `toString()` | Lombok `@Data` en entidades bidireccionales | Usar `@Getter @Setter`, NO `@Data` ni `@ToString` |
| `IllegalArgumentException: not an entity` | Olvidaste `@Entity` o no esta en el package scan | Anotar y verificar package |
| `could not initialize proxy — no Session` | Igual que LazyInit | Idem |
| `detached entity passed to persist` | Hiciste `save()` con un objeto que ya tenia ID y otra sesion lo manejaba | Usar `merge()` o recargar |
| `MultipleBagFetchException` | Dos `JOIN FETCH` sobre `List` distintos en la misma query | Cambiar uno a `Set` o partir en dos queries |
| `non-unique discovered for select` | Ambiguedad en JPQL | Usar alias explicitos |

---

## 13. Que hace Spring Data por debajo (para preguntas avanzadas)

Cuando declaras:

```java
public interface CuentaRepository extends JpaRepository<Cuenta, Long> {}
```

Al arrancar la app:

1. Spring escanea las interfaces en paquetes que extienden `Repository`.
2. Por cada una, crea un **proxy dinamico** (`JdkDynamicAopProxy` o CGLIB).
3. El proxy delega los metodos heredados (`save`, `findAll`...) a `SimpleJpaRepository`.
4. Para metodos derivados (`findByX`), parsea el nombre con `PartTree` y construye una `CriteriaQuery`.
5. Para `@Query`, parsea el JPQL y lo cachea.
6. Inyecta el proxy como bean cuando alguien pide `CuentaRepository`.

**No hay clase fisica `CuentaRepositoryImpl`.** Todo es runtime.

---

## 14. JPA vs Hibernate vs Spring Data — DIFERENCIAS

Pregunta clasica de tribunal:

| | Que es | Quien lo creo | Ejemplo |
|---|---|---|---|
| **JPA** | Especificacion (interfaces) | Java Community Process (JSR 338) | `EntityManager`, `@Entity` |
| **Hibernate** | Implementacion concreta de JPA + extras | Red Hat | `Session` (extiende `EntityManager`), `@Type` |
| **Spring Data JPA** | Capa de abstraccion sobre JPA (no implementa JPA) | Spring | `JpaRepository`, derived queries |

**Analogia**: JPA es como JDBC (interfaz), Hibernate es como el driver de MySQL (implementacion), Spring Data JPA es como JdbcTemplate (helper que reduce boilerplate).

---

## 15. Performance — checklist rapido

- [ ] Todos los `@ManyToOne` y `@OneToOne` con `fetch = FetchType.LAZY`.
- [ ] No usar `@Data` de Lombok en entidades bidireccionales (ciclos en `equals`/`toString`).
- [ ] `equals()` y `hashCode()` basados en business key, NO en `id` (que es null antes de persist).
- [ ] Usar `@EntityGraph` o `JOIN FETCH` para evitar N+1.
- [ ] Paginacion con `Pageable` siempre que devuelvas listas potencialmente grandes.
- [ ] `@Transactional(readOnly = true)` en services de solo lectura.
- [ ] `allocationSize` en `@SequenceGenerator` mayor a 1 cuando insertas mucho (50 es razonable para `Movimiento`).
- [ ] Indices en columnas usadas en WHERE, JOIN, ORDER BY.
- [ ] `show-sql=true` en dev, FALSE en prod.

---

## 16. Posibles preguntas del tribunal (con respuesta corta)

**P: ¿Por que `@Entity` necesita constructor sin argumentos?**
R: JPA usa **reflexion** para instanciar entidades al cargarlas desde la BD. Reflexion necesita un constructor sin args para crear el objeto y despues setear los campos.

**P: ¿Que pasa si pongo `@Enumerated` sin especificar?**
R: Default es `ORDINAL` (guarda el indice numerico). MUY peligroso: si reordenas el enum, los datos viejos se corrompen. SIEMPRE `@Enumerated(EnumType.STRING)`.

**P: ¿Diferencia entre `save()` y `persist()`?**
R: `persist()` es de JPA, devuelve void, falla si la entidad ya existe. `save()` es de Spring Data: si tiene ID y existe hace `merge`, si no, hace `persist`. `save()` es mas tolerante.

**P: ¿Que es flush?**
R: `flush()` sincroniza la primera fila del cache de Hibernate (Persistence Context) con la BD. Las queries SQL se mandan, pero la transaccion NO se commitea. El commit ocurre al final de la `@Transactional`.

**P: ¿Y first-level cache?**
R: Es el cache que mantiene el `EntityManager` durante una sesion (= transaccion). Si pedis dos veces la misma entidad por id en la misma TX, la segunda no toca la BD.

**P: ¿Diferencia entre JPQL y SQL?**
R: JPQL trabaja con **entidades y campos** (`SELECT c FROM Cuenta c WHERE c.cliente.dni = :dni`). SQL trabaja con **tablas y columnas**. JPQL es portable entre motores; SQL no.

**P: ¿Que es Cascade en JPA?**
R: Politica que decide si las operaciones (persist, remove, etc.) se propagan a las entidades relacionadas. `CascadeType.ALL` propaga todas. Cuidado con `REMOVE` en `@ManyToMany`.

**P: ¿Por que prefieren `SEQUENCE` en Postgres y no `IDENTITY`?**
R: `IDENTITY` deshabilita el batch insert de Hibernate (necesita ir y volver con cada insert para conseguir el ID). `SEQUENCE` permite reservar IDs en bloques (`allocationSize`) y batchear N inserts juntos.

**P: ¿Que hace `@Transactional(readOnly = true)` realmente?**
R: 1) Hibernate desactiva el dirty checking (no compara entidades para detectar cambios). 2) Algunos drivers/drivers de pool envian la flag al motor para que pueda optimizar. 3) Documenta intencion al lector.

**P: ¿Como manejas concurrencia (dos usuarios actualizando la misma cuenta)?**
R: Dos opciones:
- **Optimistic locking**: campo `@Version` en la entidad. Si dos TX modifican, la segunda falla con `OptimisticLockException`.
- **Pessimistic locking**: `@Lock(LockModeType.PESSIMISTIC_WRITE)` en el query. Bloquea la fila hasta el commit.

**P: ¿Que es DTO Projection?**
R: Devolver solo los campos necesarios desde el repo, sin cargar la entidad completa. Mas eficiente para listas:

```java
public interface CuentaResumen {
    String getNumeroCuenta();
    BigDecimal getSaldo();
}
List<CuentaResumen> findByClienteId(Long id);
```

**P: ¿Como evitan inyeccion SQL?**
R: Spring Data y JPA usan **PreparedStatements** con parametros bindeados (`:param`). Nunca concatenamos strings en queries. Incluso en `nativeQuery = true`, los `:param` se bindean.

---

## 17. Recursos para profundizar

- **Spring Data JPA reference**: https://docs.spring.io/spring-data/jpa/reference/
- **Vlad Mihalcea — High-Performance Java Persistence** (libro de cabecera para JPA performance)
- **Hibernate User Guide**: https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html
- **Baeldung JPA series**: https://www.baeldung.com/persistence-with-spring-series

---

## 18. Frase final para cerrar la exposicion

> "Spring Data JPA no es magia: es una abstraccion que se sostiene sobre JPA, que se sostiene sobre Hibernate, que se sostiene sobre JDBC. Cada capa resuelve un problema concreto. Conocer las capas de abajo es lo que permite usar bien la de arriba."
