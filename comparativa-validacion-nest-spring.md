# Comparativa: `class-validator` y `class-transformer` (Nest) ↔ Spring/Java

> Referencia rápida para el equipo. Útil si te preguntan en el Q&A: "¿y cómo se valida o se transforma un DTO en Spring?".

En Spring, los roles que en Nest cubre un ecosistema unificado (`class-validator` + `class-transformer` + `ValidationPipe`) están **repartidos** en piezas distintas. La validación va por un lado; la transformación, por otro.

---

## 1. `class-validator` → Bean Validation (Jakarta Validation)

Equivalente casi 1 a 1. Misma filosofía: anotaciones declarativas sobre los campos del DTO.

| class-validator (Nest) | Bean Validation (Spring) |
|---|---|
| `@IsString()` | tipar el campo como `String` (Java es estático) |
| `@IsEmail()` | `@Email` |
| `@IsNotEmpty()` | `@NotBlank` (strings) / `@NotEmpty` (colecciones) |
| `@MinLength(n)` / `@MaxLength(n)` | `@Size(min=, max=)` |
| `@Min(n)` / `@Max(n)` | `@Min(n)` / `@Max(n)` |
| `@IsPositive()` | `@Positive` / `@PositiveOrZero` |
| `@Matches(/regex/)` | `@Pattern(regexp = "…")` |
| `@ValidateNested()` | `@Valid` en el campo (cascada) |
| `@IsOptional()` | no anotás — el default permite null |
| `@ValidatorConstraint` (custom) | `@Constraint` + `ConstraintValidator` |

**Implementación de referencia:** [Hibernate Validator](https://hibernate.org/validator/) (es otra librería distinta de Hibernate ORM, aunque del mismo equipo). Spring Boot la trae automáticamente al agregar `spring-boot-starter-validation`.

**Disparador de la validación:**
- **Nest** → `ValidationPipe` global o por endpoint.
- **Spring** → `@Valid` antes del `@RequestBody` en el controller.

```java
// Spring
@PostMapping
public ClienteDto crear(@Valid @RequestBody ClienteDto dto) {
    return service.crear(dto);
}
```

```ts
// Nest equivalente
@Post()
crear(@Body() dto: ClienteDto) { ... }
// + ValidationPipe registrado globalmente o en el controller
```

---

## 2. `class-transformer` → se parte en DOS

`class-transformer` en Nest cumple dos roles distintos:

1. **JSON ↔ objeto** — pasarela HTTP.
2. **Entity ↔ DTO** — mapeo entre representaciones internas.

En Spring esos dos roles los cubren herramientas **diferentes**.

### 2.1 Rol JSON ↔ objeto → **Jackson**

Jackson es la librería de serialización que Spring Boot trae de fábrica. Hace el trabajo **automáticamente** apenas ponés `@RequestBody` o devolvés un objeto desde un controller. No llamás a nada a mano.

| class-transformer (Nest) | Jackson (Spring) |
|---|---|
| `plainToClass(User, json)` | Automático con `@RequestBody User dto` |
| `classToPlain(user)` | Automático al hacer `return user` |
| `@Expose()` | `@JsonProperty("nombre_externo")` |
| `@Exclude()` | `@JsonIgnore` |
| `@Type(() => Date)` | No hace falta — Jackson lee el tipo del campo |
| `@Transform(({ value }) => value.toUpperCase())` | `@JsonDeserialize(using = …)` / `@JsonSerialize` / `@JsonFormat` |
| Groups: `@Expose({ groups: ['admin'] })` | `@JsonView(Views.Admin.class)` |
| `instanceToPlain` con opciones | `ObjectMapper` configurado (`@JsonInclude`, etc.) |

```java
// Spring — todo automático
@PostMapping
public ClienteDto crear(@RequestBody ClienteDto dto) {
    // Jackson ya convirtió el JSON entrante a ClienteDto
    return service.crear(dto);
    // Jackson convertirá el objeto devuelto a JSON
}
```

### 2.2 Rol Entity ↔ DTO → **MapStruct** (o mapeo manual)

Esto es lo que en proyectos Nest muchas veces se resuelve con `class-transformer` + `plainToClass()`. En Java tenés tres caminos:

#### Opción A — **MapStruct** (estándar del ecosistema)

Generador de código en **tiempo de compilación**. Definís una interface con los métodos de mapeo, MapStruct genera la implementación durante el build. Sin reflexión, ultra rápido, tipado y seguro.

```java
@Mapper(componentModel = "spring")
public interface ClienteMapper {
    ClienteDto toDto(Cliente entity);
    Cliente toEntity(ClienteDto dto);
}
```

MapStruct genera la clase `ClienteMapperImpl` durante la compilación. Spring la inyecta como bean.

#### Opción B — **ModelMapper**

Basado en reflexión en runtime. Setup más simple, pero más lento y menos seguro de tipos.

```java
ClienteDto dto = modelMapper.map(cliente, ClienteDto.class);
```

#### Opción C — **Mapeo manual** (lo que usamos en este proyecto)

Para entidades chicas es perfectamente válido. Mirá `ClienteService.aDto()`:

```java
private ClienteDto aDto(Cliente c) {
    return new ClienteDto(
        c.getId(),
        c.getNombres(),
        c.getApellidos(),
        c.getDni(),
        c.getEmail()
    );
}
```

Para sistemas con 50+ DTOs, MapStruct gana por goleada (menos boilerplate, mejor performance).

---

## 3. Resumen visual

```
NestJS                          Spring/Java
═══════════════════════════════════════════════════════════
class-validator           →     Bean Validation
                                  (Hibernate Validator)

ValidationPipe            →     @Valid + @RequestBody

class-transformer         →     SE PARTE EN DOS:
  ├─ JSON ↔ objeto        →     Jackson (automático)
  └─ Entity ↔ DTO         →     MapStruct  (o manual)
```

---

## 4. En este proyecto, qué se está usando

| Responsabilidad | Herramienta | Dónde verlo en el código |
|---|---|---|
| Validación de DTOs | Bean Validation (`@NotBlank`, `@Email`, `@Size`, `@Positive`…) + `@Valid` | `dto/ClienteDto.java`, `dto/CrearCuentaRequest.java`, controllers |
| Validación de entidades | Bean Validation (refuerzo a nivel de modelo) | `entities/Cliente.java`, `entities/Cuenta.java` |
| JSON ↔ objeto | Jackson (automático con `spring-boot-starter-web`) | Sin configurar — funciona solo |
| Entity ↔ DTO | Mapeo manual con métodos `aDto()` | `services/ClienteService.java`, `services/CuentaService.java` |
| Errores de validación | `MethodArgumentNotValidException` capturada en handler global | `exceptions/GlobalExceptionHandler.java` |

---

## 5. Bibliografía

### Bean Validation
- Especificación Jakarta Bean Validation 3.0 — <https://jakarta.ee/specifications/bean-validation/3.0/>
- Hibernate Validator (impl) — <https://hibernate.org/validator/>
- Spring + `@Valid` — <https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html>

### Jackson
- Documentación oficial — <https://github.com/FasterXML/jackson-docs>
- Spring Boot + Jackson — <https://docs.spring.io/spring-boot/reference/web/servlet.html#web.servlet.spring-mvc.json>

### MapStruct y ModelMapper
- MapStruct — <https://mapstruct.org>
- ModelMapper — <http://modelmapper.org>

### Nest (referencia para las analogías)
- class-validator — <https://github.com/typestack/class-validator>
- class-transformer — <https://github.com/typestack/class-transformer>
- NestJS Validation — <https://docs.nestjs.com/techniques/validation>
- NestJS Serialization — <https://docs.nestjs.com/techniques/serialization>
