# Exposición: Bases de Datos y Spring Data JPA

**Curso**: Ingeniería Web — Spring Boot
**Modalidad**: Exposición grupal introductoria
**Integrantes**: 4
**Duración total estimada**: 50 minutos de exposición + 10 minutos de Q&A

---

## La historia que vamos a contar

La exposición es UNA sola narrativa contada por 4 voces. Cada integrante toma la posta donde el anterior la dejó, y el cierre de cada bloque planta la pregunta que abre el siguiente.

**El arco narrativo**:

> Tenemos objetos en Java y tenemos tablas en una base de datos. Son dos mundos que no encajan naturalmente. JPA nace para ser el traductor entre esos dos mundos, y Spring Data JPA lo hace todavía más simple. Hoy vamos a recorrer cómo, partiendo de un proyecto vacío, terminamos teniendo una API REST que persiste datos en PostgreSQL sin escribir una sola línea de SQL.

**Hilo conductor**: una sola entidad de ejemplo, `Cuenta`, atraviesa los 4 bloques. Eso garantiza coherencia y permite que el último integrante muestre la demo final usando exactamente lo que los anteriores explicaron en teoría.

**Reglas para todo el grupo**:

1. Una sola entidad de ejemplo (`Cuenta`) — nadie inventa la propia.
2. Los integrantes 2, 3 y 4 abren su bloque con una frase del estilo *"Como contó [nombre del anterior], ahora vamos a..."*. Esto refuerza la unidad.
3. El proyecto demo se abre UNA sola vez al inicio y se va completando en vivo entre los bloques 2, 3 y 4.
4. Diapositivas con DIAGRAMAS, no párrafos. La gente lee más rápido de lo que vos hablás.

---

## Distribución de temas por integrante

### Integrante 1 — Conceptos: ¿Qué es y por qué existe JPA?

**Duración**: ~10 minutos
**Tipo**: 100% teoría, sin código en pantalla
**Objetivo**: que la audiencia entienda el PROBLEMA antes de ver la solución

**Contenido a cubrir**:

1. **El problema del object-relational impedance mismatch**
   - Los objetos en Java tienen jerarquías, herencia, listas, asociaciones.
   - Las tablas en una base de datos relacional tienen filas, columnas y claves foráneas.
   - Estos dos modelos NO encajan naturalmente.
   - Ejemplo visual: una clase `Cliente` con una `List<Pedido>` vs cómo se representa eso en SQL con dos tablas y una FK.

2. **¿Qué es un ORM?**
   - Object-Relational Mapper.
   - Es el traductor entre el modelo orientado a objetos y el modelo relacional.
   - Sin ORM tendrías que escribir manualmente todo el SQL y mapear ResultSets a objetos a mano (mostrar pseudocódigo de JDBC puro para que vean el sufrimiento que evitamos).

3. **La torre de abstracción** (diapositiva CLAVE)

   ```
   ┌─────────────────────────┐
   │   Spring Data JPA       │  ← Repositorios automáticos
   ├─────────────────────────┤
   │   JPA (especificación)  │  ← Interfaces estándar de Java (jakarta.persistence)
   ├─────────────────────────┤
   │   Hibernate             │  ← Implementación concreta de JPA (default en Spring Boot)
   ├─────────────────────────┤
   │   JDBC                  │  ← API de bajo nivel para hablar con la BD
   ├─────────────────────────┤
   │   Driver (PostgreSQL, etc.)  │  ← Conector específico de cada motor
   ├─────────────────────────┤
   │   Base de Datos         │
   └─────────────────────────┘
   ```

4. **La distinción CRÍTICA que hay que dejar clara**:
   - **JPA** es una **especificación** — solo define interfaces y reglas, no hace nada por sí sola.
   - **Hibernate** es la **implementación** que cumple con esa especificación. Spring Boot la trae por default.
   - **Spring Data JPA** es una capa de **abstracción adicional** encima, que te genera repositorios automáticamente.

5. **Ventajas y costos del ORM**
   - **A favor**: productividad enorme, código portable entre motores de BD, menos bugs de SQL escrito a mano.
   - **En contra**: capa de magia que oculta lo que pasa, riesgo de queries ineficientes (problema N+1), curva de aprendizaje.

**Frase de cierre**:
> "Ahora que sabemos QUÉ es JPA y dónde se ubica, le paso la palabra a [nombre] para ver CÓMO configuramos todo esto en un proyecto Spring Boot real."

---

### Integrante 2 — Configuración: conectando Spring Boot a una base de datos

**Duración**: ~12 minutos
**Tipo**: Teoría + demo de conexión
**Objetivo**: enseñar cómo se enchufa el proyecto a una base de datos real

**Contenido a cubrir**:

1. **Las dependencias necesarias** (mostrar el `pom.xml` del proyecto demo)
   - `spring-boot-starter-data-jpa` — trae Hibernate, JPA APIs y Spring Data.
   - `postgresql` — el driver JDBC específico de PostgreSQL.
   - Mencionar que cambiando solo el driver podríamos usar PostgreSQL, Oracle, etc. (esa es la magia de la abstracción JPA).

2. **Archivo de configuración**: `application.properties` vs `application.yml`
   - Mismo contenido, distinto formato.
   - `properties` es plano (key=value).
   - `yml` es jerárquico, más legible para configs grandes.
   - Para el curso vamos a usar `properties` porque es el default que genera Initializr.

3. **Las propiedades CLAVE** (mostrar y explicar línea por línea)

   ```properties
   # Conexión a la base de datos
   spring.datasource.url=jdbc:postgresql://localhost:5432/banco_demo
   spring.datasource.username=postgres
   spring.datasource.password=secret
   spring.datasource.driver-class-name=org.postgresql.Driver

   # Comportamiento de Hibernate
   spring.jpa.hibernate.ddl-auto=update
   spring.jpa.show-sql=true
   spring.jpa.properties.hibernate.format_sql=true
   spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect
   ```

   Explicar **qué hace cada una** y **por qué la necesitamos**.

4. **`ddl-auto`: la propiedad más mal usada del ecosistema**

   | Valor | Qué hace | Cuándo usarla |
   |-------|----------|---------------|
   | `none` | No hace nada | Producción con migraciones manuales (Flyway/Liquibase) |
   | `validate` | Valida que el esquema coincida con las entidades | Producción |
   | `update` | Modifica el esquema para reflejar cambios | Desarrollo (con cuidado) |
   | `create` | Borra y crea el esquema al arrancar | Tests, prototipos |
   | `create-drop` | Crea al arrancar, borra al apagar | Tests automatizados únicamente |

   **Advertencia EXPLÍCITA**: `create` y `create-drop` BORRAN datos. JAMÁS en producción.

5. **Profiles** (`application-dev.properties`, `application-prod.properties`)
   - Cómo separar configs por entorno.
   - Activarlos con `spring.profiles.active=dev` o variable de entorno.

6. **Demo en vivo** (5 minutos máximo)
   - Levantar PostgreSQL (Docker, instalación local o pgAdmin — el que tenga el equipo a mano).
   - Crear la base de datos vacía: `CREATE DATABASE banco_demo;` (desde psql o pgAdmin).
   - Pegar las propiedades en `application.properties`.
   - Arrancar la app con `./mvnw spring-boot:run`.
   - Mostrar en los logs cómo Spring detecta la BD y se conecta.

**Frase de cierre**:
> "Ya estamos conectados a la base de datos, pero está vacía. Ahora le paso la palabra a [nombre] para ver cómo le decimos a Spring qué tablas crear y cómo mapearlas a clases Java."

---

### Integrante 3 — Entidades: mapeando objetos a tablas

**Duración**: ~12 minutos
**Tipo**: Teoría + ejemplo de código completo
**Objetivo**: enseñar las anotaciones que convierten una clase Java en una tabla

**Contenido a cubrir**:

1. **`@Entity` y `@Table`**
   - `@Entity` marca la clase como una entidad gestionada por JPA.
   - `@Table(name = "cuentas")` permite especificar el nombre de la tabla. Si no se pone, JPA usa el nombre de la clase.
   - **Requisito olvidado por todo el mundo**: una entidad necesita un constructor sin argumentos (vacío). JPA lo necesita para instanciar objetos por reflexión.

2. **`@Id` y `@GeneratedValue`** — la clave primaria

   | Estrategia | Cómo funciona | Cuándo usar |
   |------------|---------------|-------------|
   | `IDENTITY` | Usa columnas auto-incrementales de la BD (`SERIAL` en Postgres) | Funcional pero NO recomendado en Postgres |
   | `SEQUENCE` | Usa una secuencia explícita de la BD | **Recomendado para PostgreSQL y Oracle** |
   | `AUTO` | JPA decide por vos (en Postgres elige SEQUENCE) | Cuando querés portabilidad |
   | `UUID` | Genera un UUID | Sistemas distribuidos |

   **Nota para PostgreSQL**: la estrategia recomendada es `SEQUENCE` porque permite a Hibernate hacer batching de inserts (mejor performance). `IDENTITY` funciona pero deshabilita esa optimización.

3. **`@Column`** — controlar el mapeo de cada campo
   - `name`: nombre de la columna.
   - `nullable`: si admite NULL.
   - `length`: longitud máxima (para Strings).
   - `unique`: restricción de unicidad.
   - `precision` y `scale`: para `BigDecimal`.

4. **Mapeo de tipos básicos**
   - `String` → `VARCHAR`
   - `Integer` / `Long` → `INT` / `BIGINT`
   - `BigDecimal` → `DECIMAL`
   - `LocalDate` / `LocalDateTime` → `DATE` / `TIMESTAMP`
   - `Boolean` → `BIT` o `TINYINT(1)`
   - Para enums: `@Enumerated(EnumType.STRING)` (NUNCA `ORDINAL`, lo explicás brevemente).

5. **Ejemplo completo** (la entidad que va a usar el integrante 4 en la demo)

   ```java
   package com.example.demo.entities;

   import jakarta.persistence.*;
   import java.math.BigDecimal;
   import java.time.LocalDateTime;

   @Entity
   @Table(name = "cuentas")
   public class Cuenta {

       @Id
       @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "cuentas_seq")
       @SequenceGenerator(name = "cuentas_seq", sequenceName = "cuentas_id_seq", allocationSize = 1)
       private Long id;

       @Column(nullable = false, length = 100)
       private String titular;

       @Column(nullable = false, unique = true, length = 20)
       private String numeroCuenta;

       @Column(nullable = false, precision = 19, scale = 2)
       private BigDecimal saldo;

       @Column(name = "fecha_apertura", nullable = false)
       private LocalDateTime fechaApertura;

       // Constructor vacío REQUERIDO por JPA
       public Cuenta() {}

       // Getters, setters, toString...
   }
   ```

6. **Mención breve de relaciones** (sin profundizar — es introductorio)
   - `@OneToMany` — un cliente tiene muchas cuentas.
   - `@ManyToOne` — muchas cuentas pertenecen a un cliente.
   - `@ManyToMany` — alumnos y cursos.
   - "Esto lo verán en detalle más adelante en el curso."

7. **Ciclo de vida de una entidad** (concepto importante simplificado)

   ```
   transient ──save()──> managed ──detach()──> detached
                            │
                          remove()
                            ↓
                         removed
   ```

   Explicar brevemente:
   - **transient**: objeto recién creado, JPA no lo conoce.
   - **managed**: JPA lo está rastreando, los cambios se persisten automáticamente.
   - **detached**: JPA lo conoció pero ya no lo rastrea.
   - **removed**: marcado para borrarse.

   "Esto explica por qué a veces los cambios no se persisten — el objeto está detached y nadie lo está rastreando."

**Frase de cierre**:
> "Tenemos la tabla y la clase Java. Ahora la pregunta es: ¿cómo guardamos y recuperamos datos sin escribir SQL? Para eso, [nombre] cierra con los repositorios y la demo final."

---

### Integrante 4 — Repositorios y demo CRUD completa

**Duración**: ~15 minutos
**Tipo**: Teoría mínima + demo en vivo (la cereza del postre)
**Objetivo**: cerrar con la magia de Spring Data y el laboratorio funcional que pide la consigna

**Contenido a cubrir**:

1. **Jerarquía de interfaces de Spring Data** (diapositiva)

   ```
   Repository  (marker interface)
        ↓
   CrudRepository<T, ID>          ← save, findById, findAll, delete, count
        ↓
   PagingAndSortingRepository    ← + paginación y ordenamiento
        ↓
   JpaRepository<T, ID>          ← + flush, saveAndFlush, deleteInBatch (lo más usado)
   ```

2. **El truco mágico** (el momento "wow" de la exposición)

   Solo definís una **interface**, sin implementarla:

   ```java
   package com.example.demo.repositories;

   import com.example.demo.entities.Cuenta;
   import org.springframework.data.jpa.repository.JpaRepository;

   public interface CuentaRepository extends JpaRepository<Cuenta, Long> {
   }
   ```

   Y con eso ya tenés gratis: `save()`, `findById()`, `findAll()`, `deleteById()`, `count()`, `existsById()`, paginación, etc.

   **NO escribimos ninguna implementación.** Spring genera el bean en runtime usando proxies dinámicos.

3. **Query methods derivados** (lo más vistoso para la demo)

   Spring parsea el NOMBRE del método y genera la query.

   ```java
   public interface CuentaRepository extends JpaRepository<Cuenta, Long> {

       List<Cuenta> findByTitular(String titular);

       List<Cuenta> findBySaldoGreaterThan(BigDecimal monto);

       Optional<Cuenta> findByNumeroCuenta(String numeroCuenta);

       List<Cuenta> findByTitularAndSaldoGreaterThan(String titular, BigDecimal monto);

       List<Cuenta> findByTitularOrderBySaldoDesc(String titular);
   }
   ```

   En la demo, mostrar cómo cambia el SQL en consola con cada método sin tocar nada más.

4. **`@Query` con JPQL** para casos más complejos

   ```java
   @Query("SELECT c FROM Cuenta c WHERE c.saldo > :monto AND c.titular LIKE %:nombre%")
   List<Cuenta> buscarRicosPorNombre(
       @Param("monto") BigDecimal monto,
       @Param("nombre") String nombre
   );
   ```

   Explicar que JPQL trabaja con ENTIDADES y CAMPOS, no con tablas y columnas. Es más portable que SQL nativo.

5. **DEMO EN VIVO COMPLETA** (8 minutos — el corazón del bloque)

   Tener el proyecto YA abierto con la entidad y el repositorio listos. Solo agregar el controller en vivo:

   ```java
   @RestController
   @RequestMapping("/api/cuentas")
   public class CuentaController {

       private final CuentaRepository repo;

       public CuentaController(CuentaRepository repo) {
           this.repo = repo;
       }

       @PostMapping
       public Cuenta crear(@RequestBody Cuenta cuenta) {
           return repo.save(cuenta);
       }

       @GetMapping
       public List<Cuenta> listar() {
           return repo.findAll();
       }

       @GetMapping("/{id}")
       public Cuenta obtener(@PathVariable Long id) {
           return repo.findById(id).orElseThrow();
       }

       @PutMapping("/{id}")
       public Cuenta actualizar(@PathVariable Long id, @RequestBody Cuenta cambios) {
           Cuenta cuenta = repo.findById(id).orElseThrow();
           cuenta.setSaldo(cambios.getSaldo());
           return repo.save(cuenta);
       }

       @DeleteMapping("/{id}")
       public void borrar(@PathVariable Long id) {
           repo.deleteById(id);
       }
   }
   ```

   **Pasos de la demo** (en orden, con Postman o Insomnia preparado):
   1. POST a `/api/cuentas` → crear una cuenta. **Mostrar en consola la query INSERT que generó Hibernate.**
   2. POST otra cuenta más.
   3. GET a `/api/cuentas` → listar todas. **Mostrar el SELECT.**
   4. GET a `/api/cuentas/1` → obtener una.
   5. PUT a `/api/cuentas/1` → actualizar saldo. **Mostrar el UPDATE.**
   6. DELETE a `/api/cuentas/1` → borrar.
   7. Ir a pgAdmin (o DBeaver) y mostrar la tabla con los datos reales.

6. **Cierre de toda la exposición** (1-2 minutos)

   Recap final con la torre de abstracción del integrante 1:
   - Definimos una clase con anotaciones JPA.
   - Spring Data nos generó el repositorio.
   - Hibernate tradujo nuestras llamadas Java a SQL.
   - El driver de PostgreSQL ejecutó ese SQL en la base.
   - **Y nosotros no escribimos UNA línea de SQL.**

   Cerrar con qué viene después en el curso:
   - Relaciones entre entidades.
   - Transacciones (`@Transactional`).
   - Queries nativas y proyecciones.
   - Validación con Bean Validation.
   - Testing de repositorios con `@DataJpaTest`.

**Frase de cierre del grupo completo**:
> "Y eso es Spring Data JPA en su esencia. Gracias, ¿alguna pregunta?"

---

## Tabla resumen general

| # | Integrante | Bloque | Tipo | Tiempo |
|---|------------|--------|------|--------|
| 1 | — | Conceptos: ORM, JPA, Hibernate, Spring Data | 100% teoría | ~10 min |
| 2 | — | Configuración: starters, properties, datasource, ddl-auto | Teoría + demo de conexión | ~12 min |
| 3 | — | Entidades: anotaciones, mapeo, ciclo de vida | Teoría + ejemplo de código | ~12 min |
| 4 | — | Repositorios + DEMO CRUD completa | Mínima teoría + LAB en vivo | ~15 min |
| | | **Total** | | **~50 min + Q&A** |

---

## Errores comunes que el grupo debe MENCIONAR (aunque no profundicen)

Mostrar dominio del tema implica mencionar las trampas, no solo lo bonito:

- **Olvidar el constructor sin argumentos en `@Entity`** → JPA explota al instanciar.
- **`ddl-auto=create` en producción** → adiós datos.
- **Problema N+1** → cargar N entidades dispara N+1 queries por relaciones lazy mal manejadas.
- **`LazyInitializationException`** → acceder a una relación lazy fuera de la sesión.
- **Usar `@Enumerated(EnumType.ORDINAL)`** → si reordenás el enum, los datos se corrompen. SIEMPRE `STRING`.
- **Confundir JPA con Hibernate** → JPA es la espec, Hibernate es la implementación.

---

## Recomendaciones finales para el grupo

1. **Ensayar al menos 2 veces completos**, cronometrando cada bloque.
2. **El integrante 4 NO arranca de cero la demo** — tener el proyecto compilado y PostgreSQL corriendo desde antes.
3. **Tener un plan B** si PostgreSQL falla en la demo: una base H2 en memoria preconfigurada como fallback.
4. **Postman o Insomnia con la colección de requests YA armada**. Nada de tipear URLs en vivo.
5. **Slides limpias**: máximo 5 bullets por diapositiva, una idea principal por slide.
6. **Diagrama de la torre de abstracción** debe aparecer al menos 2 veces: al inicio (integrante 1) y al cierre (integrante 4).

---

## Anexo: Dependencias para Spring Initializr

Para generar el proyecto demo desde [start.spring.io](https://start.spring.io), usar esta configuración:

### Configuración del proyecto

| Campo | Valor |
|-------|-------|
| **Project** | Maven |
| **Language** | Java |
| **Spring Boot** | 3.5.x (versión estable más reciente — recomendada para el curso) |
| **Group** | com.example |
| **Artifact** | demo-jpa |
| **Name** | demo-jpa |
| **Description** | Demo JPA para exposición |
| **Package name** | com.example.demojpa |
| **Packaging** | Jar |
| **Java** | 17 (o 21 si el equipo lo tiene instalado) |

### Dependencias a marcar

| Dependencia | Identificador en Initializr | Por qué la necesitamos |
|-------------|------------------------------|------------------------|
| **Spring Web** | `web` | Para crear el controller REST de la demo |
| **Spring Data JPA** | `data-jpa` | El protagonista — trae Hibernate y JPA APIs |
| **PostgreSQL Driver** | `postgresql` | Driver JDBC específico para conectar a PostgreSQL |
| **Validation** | `validation` | Bean Validation (`@NotNull`, `@Size`, etc.) — útil para mostrar profesionalismo |
| **Lombok** | `lombok` | Para evitar boilerplate de getters/setters/constructores |
| **Spring Boot DevTools** | `devtools` | Hot reload — la app se reinicia sola al cambiar código |

### Dependencia opcional (recomendada como plan B)

| Dependencia | Identificador | Por qué |
|-------------|---------------|---------|
| **H2 Database** | `h2` | Base en memoria — fallback si PostgreSQL falla en la demo |

Si se agrega H2, configurar un perfil `application-h2.properties` con:

```properties
spring.datasource.url=jdbc:h2:mem:demo
spring.datasource.driver-class-name=org.h2.Driver
spring.datasource.username=sa
spring.datasource.password=
spring.jpa.database-platform=org.hibernate.dialect.H2Dialect
spring.h2.console.enabled=true
```

Y se activa con `--spring.profiles.active=h2` al arrancar.

### URL directa para generar el proyecto

```
https://start.spring.io/#!type=maven-project&language=java&packaging=jar&jvmVersion=17&groupId=com.example&artifactId=demo-jpa&name=demo-jpa&description=Demo%20JPA%20para%20exposicion&packageName=com.example.demojpa&dependencies=web,data-jpa,postgresql,validation,lombok,devtools
```

### Estructura de paquetes recomendada para el demo

```
com.example.demojpa
├── DemoJpaApplication.java
├── entities
│   └── Cuenta.java
├── repositories
│   └── CuentaRepository.java
└── controllers
    └── CuentaController.java
```

Esta estructura por capas es la que el integrante 4 va a usar en la demo y refleja la arquitectura clásica que se enseña en el resto del curso.
