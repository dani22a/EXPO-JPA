# -*- coding: utf-8 -*-
"""
Genera INFORME_TEORICO.docx para la exposicion de Spring Boot + JPA.
No requiere dependencias externas: solo zipfile + xml de la stdlib.
"""
import os
import zipfile
from xml.sax.saxutils import escape as _esc

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "INFORME_TEORICO.docx")

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)


def esc(s):
    """Escape XML especial. Permite \n explicitos via <w:br/>."""
    return _esc(s).replace('"', '&quot;').replace("'", '&apos;')


# ---------------------------------------------------------------------------
# Helpers para construir XML OOXML
# ---------------------------------------------------------------------------

def run(text, *, bold=False, italic=False, mono=False, color=None, size=None):
    """Un run = trozo de texto con formato uniforme."""
    rpr_parts = []
    if bold:
        rpr_parts.append('<w:b/>')
    if italic:
        rpr_parts.append('<w:i/>')
    if mono:
        rpr_parts.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>')
    if color:
        rpr_parts.append(f'<w:color w:val="{color}"/>')
    if size:
        # w:sz es half-points
        rpr_parts.append(f'<w:sz w:val="{size*2}"/>')
    rpr = f'<w:rPr>{"".join(rpr_parts)}</w:rPr>' if rpr_parts else ''
    # preservar espacios al inicio/fin
    return f'<w:r>{rpr}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def heading(text, level=1):
    style = {1: 'Heading1', 2: 'Heading2', 3: 'Heading3'}.get(level, 'Heading1')
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
        f'{run(text, bold=True)}</w:p>'
    )


def title(text):
    return (
        '<w:p><w:pPr><w:pStyle w:val="Title"/><w:jc w:val="center"/></w:pPr>'
        f'{run(text, bold=True)}</w:p>'
    )


def subtitle(text):
    return (
        '<w:p><w:pPr><w:jc w:val="center"/></w:pPr>'
        f'{run(text, italic=True, color="555555")}</w:p>'
    )


def para(*runs_xml, indent=0, align=None):
    pPr = []
    if indent:
        pPr.append(f'<w:ind w:left="{indent}"/>')
    if align:
        pPr.append(f'<w:jc w:val="{align}"/>')
    pPr_xml = f'<w:pPr>{"".join(pPr)}</w:pPr>' if pPr else ''
    body = ''.join(runs_xml)
    return f'<w:p>{pPr_xml}{body}</w:p>'


def p(text, **kw):
    """Atajo: parrafo de un solo run."""
    return para(run(text, **kw))


def bullet(text, level=0):
    """Lista con vinetas. numId=1 esta declarado en numbering.xml."""
    return (
        '<w:p><w:pPr><w:pStyle w:val="ListBullet"/>'
        f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="1"/></w:numPr>'
        '</w:pPr>'
        f'{run(text)}</w:p>'
    )


def bullet_runs(*runs_xml, level=0):
    return (
        '<w:p><w:pPr><w:pStyle w:val="ListBullet"/>'
        f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="1"/></w:numPr>'
        '</w:pPr>'
        + ''.join(runs_xml) + '</w:p>'
    )


def code_block(text):
    """Bloque de codigo: monospace + sombreado + sin justificar."""
    lines = text.split('\n')
    paras = []
    for line in lines:
        paras.append(
            '<w:p><w:pPr><w:pStyle w:val="Code"/></w:pPr>'
            f'{run(line, mono=True)}</w:p>'
        )
    return ''.join(paras)


def quote_block(text):
    """Cita destacada."""
    return (
        '<w:p><w:pPr><w:pStyle w:val="Quote"/></w:pPr>'
        f'{run(text, italic=True)}</w:p>'
    )


def table(headers, rows, col_widths=None):
    """Tabla simple. col_widths en twips (1cm ~ 567)."""
    n = len(headers)
    if not col_widths:
        col_widths = [int(9000 / n)] * n  # ~16cm de ancho total

    grid = '<w:tblGrid>' + ''.join(
        f'<w:gridCol w:w="{w}"/>' for w in col_widths
    ) + '</w:tblGrid>'

    def cell(content, *, header=False, w=2000):
        shading = (
            '<w:shd w:val="clear" w:color="auto" w:fill="2E74B5"/>' if header else ''
        )
        runs_xml = run(content, bold=header, color="FFFFFF" if header else None)
        return (
            f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shading}</w:tcPr>'
            f'<w:p>{runs_xml}</w:p></w:tc>'
        )

    head_row = '<w:tr>' + ''.join(
        cell(h, header=True, w=col_widths[i]) for i, h in enumerate(headers)
    ) + '</w:tr>'

    body_rows = []
    for r in rows:
        body_rows.append('<w:tr>' + ''.join(
            cell(str(c), w=col_widths[i]) for i, c in enumerate(r)
        ) + '</w:tr>')

    tbl_pr = (
        '<w:tblPr>'
        '<w:tblW w:w="9000" w:type="dxa"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:left w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:right w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '</w:tblBorders>'
        '</w:tblPr>'
    )
    return f'<w:tbl>{tbl_pr}{grid}{head_row}{"".join(body_rows)}</w:tbl>' + p('')


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


# ---------------------------------------------------------------------------
# Estilos del documento
# ---------------------------------------------------------------------------

STYLES_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
        <w:sz w:val="22"/>
        <w:lang w:val="es-PE"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:before="60" w:after="120" w:line="300" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:pPr><w:spacing w:before="360" w:after="240"/></w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="56"/><w:color w:val="1F4E79"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:next w:val="Normal"/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="360" w:after="180"/>
      <w:outlineLvl w:val="0"/>
    </w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="36"/><w:color w:val="1F4E79"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:next w:val="Normal"/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="280" w:after="140"/>
      <w:outlineLvl w:val="1"/>
    </w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="28"/><w:color w:val="2E74B5"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:next w:val="Normal"/>
    <w:pPr>
      <w:keepNext/>
      <w:spacing w:before="200" w:after="100"/>
      <w:outlineLvl w:val="2"/>
    </w:pPr>
    <w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="24"/><w:color w:val="2E74B5"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListBullet">
    <w:name w:val="List Bullet"/>
    <w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Code">
    <w:name w:val="Code"/>
    <w:pPr>
      <w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>
      <w:spacing w:before="0" w:after="0" w:line="260" w:lineRule="auto"/>
      <w:ind w:left="200"/>
    </w:pPr>
    <w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="20"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Quote">
    <w:name w:val="Quote"/>
    <w:pPr>
      <w:ind w:left="600" w:right="600"/>
      <w:spacing w:before="120" w:after="120"/>
    </w:pPr>
    <w:rPr><w:i/><w:color w:val="555555"/></w:rPr>
  </w:style>
</w:styles>
'''

NUMBERING_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0">
    <w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr><w:rPr><w:rFonts w:ascii="Symbol" w:hAnsi="Symbol"/></w:rPr></w:lvl>
    <w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="◦"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="1440" w:hanging="360"/></w:pPr></w:lvl>
  </w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>
'''

CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>
'''

PKG_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
'''

DOC_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>
'''

# ---------------------------------------------------------------------------
# CONTENIDO DEL DOCUMENTO
# ---------------------------------------------------------------------------

blocks = []
B = blocks.append

# ============================ PORTADA ============================
B(p(''))
B(p(''))
B(p(''))
B(title('Sistema Bancario con Spring Boot y JPA'))
B(subtitle('Informe teórico — Parte 1 de la exposición'))
B(p(''))
B(p(''))
B(para(
    run('Curso: ', bold=True),
    run('Ingeniería Web'),
))
B(para(
    run('Tema: ', bold=True),
    run('Spring Boot + Spring Data JPA + PostgreSQL — capa teórica'),
))
B(para(
    run('Proyecto: ', bold=True),
    run('expo-jpa (backend Java) + expo-jpa-app (frontend React/Vite)'),
))
B(p(''))
B(p('Resumen', bold=True))
B(p(
    'Este informe sustenta la parte teórica del proyecto. Explica los conceptos '
    'que articulan la solución: el contenedor de Spring Boot, el modelo de persistencia '
    'JPA/Hibernate, la organización en capas, las transacciones, la validación, el '
    'manejo global de errores y la exposición REST. Cada bloque incluye una '
    'comparación con NestJS para que la audiencia traduzca lo nuevo a un marco '
    'que ya conoce.'
))
B(p(
    'Cada afirmación técnica está respaldada por documentación oficial '
    '(Spring Framework, Spring Boot, Spring Data JPA, Jakarta Persistence, Hibernate '
    'User Guide). Las URLs se listan en la sección de bibliografía al final.'
))
B(page_break())

# ============================ INDICE ============================
B(heading('Contenido', 1))
contenido = [
    '1. Introducción: ¿qué es Spring Boot y por qué Java?',
    '2. Arquitectura del proyecto: capas y responsabilidades',
    '3. El núcleo: contenedor IoC, beans y estereotipos',
    '4. Configuración: application.properties y autoconfiguración',
    '5. Persistencia: JPA, Jakarta Persistence e Hibernate',
    '6. Modelado de entidades',
    '7. Relaciones entre entidades (1-N, N-1, M-N)',
    '8. Spring Data JPA y los repositorios',
    '9. Estilos de consulta: derivadas, JPQL y nativas',
    '10. Capa de servicios y transacciones (@Transactional)',
    '11. Capa web: controladores REST',
    '12. Validación con Bean Validation',
    '13. Manejo global de errores',
    '14. DTOs: por qué no devolvemos entidades',
    '15. Comparativa NestJS ↔ Spring (tabla resumen)',
    '16. Bibliografía',
]
for it in contenido:
    B(bullet(it))
B(page_break())

# ============================ 1. INTRODUCCION ============================
B(heading('1. Introducción: ¿qué es Spring Boot y por qué Java?', 1))

B(heading('1.1 Spring Framework y Spring Boot', 2))
B(p(
    'Spring Framework es el framework de aplicación más usado en el ecosistema Java. '
    'Se basa en dos ideas clave: inversión de control (IoC) e inyección de dependencias (DI). '
    'En lugar de que las clases creen sus propias dependencias, un contenedor las construye, '
    'las conecta y las administra.'
))
B(p(
    'Spring Boot es una capa por encima de Spring Framework que reduce drásticamente la '
    'configuración inicial: trae “starters” (paquetes preconfigurados), un servidor '
    'embebido (Tomcat por defecto) y un mecanismo de autoconfiguración que detecta qué '
    'librerías están en el classpath y arma piezas razonables sin que escribamos XML.'
))

B(heading('1.2 Equivalencia mental con NestJS', 2))
B(p(
    'Quienes vienen de NestJS reconocerán el patrón: Nest también es un framework opinado, '
    'con un contenedor IoC propio, módulos, providers y decoradores que organizan la '
    'aplicación. La principal diferencia es de plataforma:'
))
B(bullet('NestJS corre sobre Node.js y suele apoyarse en Express o Fastify por debajo.'))
B(bullet('Spring Boot corre sobre la JVM y trae Tomcat embebido por defecto.'))
B(p(
    'En el día a día, las analogías son casi 1 a 1: lo que en Nest se llama '
    '“provider con @Injectable()” en Spring se llama “bean con @Service” o '
    '“@Component”. Donde Nest usa decoradores (@Controller, @Get), Spring usa '
    'anotaciones (@RestController, @GetMapping). Donde Nest usa class-validator '
    '+ ValidationPipe, Spring usa Bean Validation + @Valid.'
))

B(heading('1.3 ¿Qué resuelve este proyecto?', 2))
B(p(
    'El proyecto modela un sistema bancario simplificado con cuatro entidades principales: '
    'Cliente, Cuenta, Movimiento y Producto. Las operaciones expuestas son CRUD de clientes, '
    'apertura de cuentas, registro de movimientos (depósito, retiro, transferencias, pagos), '
    'consultas paginadas, agregaciones (saldo total por cliente) y transferencias atómicas '
    'entre cuentas. Sirve para mostrar, en código real, todos los conceptos que vamos a '
    'enumerar a continuación.'
))
B(page_break())

# ============================ 2. ARQUITECTURA ============================
B(heading('2. Arquitectura del proyecto: capas y responsabilidades', 1))

B(p(
    'El backend está organizado en cuatro capas. Cada capa tiene una responsabilidad '
    'estrecha y se comunica solo con la siguiente. Esta separación es estándar en '
    'aplicaciones Spring y se conoce como “arquitectura en capas”.'
))

B(heading('Diagrama lógico', 2))
B(code_block(
    "  Cliente HTTP (frontend React/Vite)\n"
    "          ↓  JSON\n"
    "  ┌─────────────────────────────┐\n"
    "  │  Controller (capa Web)      │  → @RestController, @GetMapping...\n"
    "  └─────────────────────────────┘\n"
    "          ↓  DTO\n"
    "  ┌─────────────────────────────┐\n"
    "  │  Service  (capa de negocio) │  → @Service, @Transactional\n"
    "  └─────────────────────────────┘\n"
    "          ↓  Entidad\n"
    "  ┌─────────────────────────────┐\n"
    "  │  Repository (capa de datos) │  → JpaRepository, @Query\n"
    "  └─────────────────────────────┘\n"
    "          ↓  SQL\n"
    "  ┌─────────────────────────────┐\n"
    "  │  Hibernate (ORM)            │\n"
    "  └─────────────────────────────┘\n"
    "          ↓\n"
    "       PostgreSQL"
))

B(heading('Responsabilidades por capa', 2))
B(bullet_runs(
    run('Controller: ', bold=True),
    run(
        'recibe la petición HTTP, valida el cuerpo, delega al servicio y traduce la '
        'respuesta a JSON. Nunca debe contener reglas de negocio ni acceder a la BD.'
    ),
))
B(bullet_runs(
    run('Service: ', bold=True),
    run(
        'orquesta la operación, aplica reglas de negocio (por ejemplo: ¿hay saldo?), '
        'inicia y delimita la transacción.'
    ),
))
B(bullet_runs(
    run('Repository: ', bold=True),
    run(
        'expone consultas y operaciones de persistencia. Es la frontera con la base '
        'de datos. Spring Data genera la implementación en tiempo de ejecución.'
    ),
))
B(bullet_runs(
    run('Entity: ', bold=True),
    run(
        'representa un registro de la BD como objeto Java. Lleva las anotaciones JPA '
        'que indican cómo mapearlo a tablas y columnas.'
    ),
))

B(heading('Comparación con NestJS', 2))
B(p(
    'En Nest la organización equivalente sería: Controller → Service → Repository '
    '(TypeORM/Prisma) → Entity. Es exactamente la misma estructura, solo que cada '
    'capa se decora con @Controller, @Injectable() y @Entity respectivamente. '
    'La filosofía de “separar HTTP de la lógica de negocio y la lógica de negocio '
    'del acceso a datos” es idéntica.'
))
B(page_break())

# ============================ 3. CONTENEDOR IOC ============================
B(heading('3. El núcleo: contenedor IoC, beans y estereotipos', 1))

B(heading('3.1 Inversión de control y beans', 2))
B(p(
    'El contenedor de Spring administra objetos llamados beans. Cuando una clase '
    'declara una dependencia (por ejemplo, un servicio que necesita un repositorio), '
    'no la instancia con new: el contenedor la inyecta. Eso permite cambiar '
    'implementaciones, escribir tests con mocks y mantener bajo el acoplamiento.'
))

B(quote_block(
    '“Dependency injection is an inversion of control (IoC) technique wherein you '
    'delegate instantiation of dependencies to the IoC container.” — Documentación '
    'de NestJS (Providers).'
))
B(p(
    'La definición de Spring es exactamente la misma. Lo que cambia es la sintaxis.'
))

B(heading('3.2 La anotación @SpringBootApplication', 2))
B(p(
    'Es la anotación que se pone en la clase principal. Su trabajo es activar tres '
    'comportamientos a la vez:'
))
B(bullet_runs(
    run('@Configuration', mono=True, bold=True),
    run(' — declara que la clase puede definir beans (técnicamente Spring Boot '
        'la envuelve en @SpringBootConfiguration, una especialización).'),
))
B(bullet_runs(
    run('@EnableAutoConfiguration', mono=True, bold=True),
    run(' — activa la autoconfiguración: Spring inspecciona qué hay en el classpath '
        '(JPA, Postgres, web…) y configura beans razonables.'),
))
B(bullet_runs(
    run('@ComponentScan', mono=True, bold=True),
    run(' — escanea el paquete actual y subpaquetes buscando clases anotadas '
        '(@Service, @Repository, @Controller…) para registrarlas como beans.'),
))
B(p(
    'Por eso, con una sola anotación arrancamos toda la maquinaria. En el proyecto, '
    'la clase ExpoJpaApplication tiene 6 líneas y eso basta.'
))

B(code_block(
    "@SpringBootApplication\n"
    "public class ExpoJpaApplication {\n"
    "    public static void main(String[] args) {\n"
    "        SpringApplication.run(ExpoJpaApplication.class, args);\n"
    "    }\n"
    "}"
))

B(heading('3.3 Estereotipos: @Component, @Service, @Repository, @Controller', 2))
B(p(
    'Todas estas anotaciones marcan una clase como bean. La diferencia es semántica: '
    'comunican el rol que cumple esa clase y, en algunos casos, agregan comportamiento.'
))

B(table(
    ['Anotación', 'Capa', 'Equivalente en Nest'],
    [
        ['@Component', 'Genérico', 'Provider con @Injectable()'],
        ['@Service', 'Negocio (lógica)', '@Injectable() en .service.ts'],
        ['@Repository', 'Acceso a datos', 'Repositorio TypeORM/Prisma'],
        ['@Controller', 'Web (vistas/MVC)', '@Controller (devolviendo HTML)'],
        ['@RestController', 'Web (REST)', '@Controller (devolviendo JSON)'],
    ],
    col_widths=[2400, 3000, 3600],
))

B(p(
    '@Service, @Repository y @Controller son especializaciones de @Component. '
    'Se prefieren porque, además de declarar el bean, dejan clarísimo qué papel '
    'cumple la clase. @Repository, en particular, también traduce excepciones '
    'específicas de la BD a la jerarquía estándar de Spring.'
))
B(p(
    '@RestController es atajo de @Controller + @ResponseBody: indica que TODOS los '
    'métodos devuelven el cuerpo serializado a JSON, no el nombre de una vista. '
    'Es lo equivalente a un controller de Nest puro: el valor de retorno del método '
    'va al body del response, no se renderiza ningún template.'
))

B(heading('3.4 Inyección por constructor (la forma correcta)', 2))
B(p(
    'Hay tres formas técnicas de inyectar dependencias: por campo (con @Autowired), '
    'por setter o por constructor. La documentación oficial de Spring recomienda '
    'la inyección por constructor.'
))

B(quote_block(
    '“The Spring team generally advocates constructor injection, as it lets you '
    'implement application components as immutable objects and ensures that required '
    'dependencies are not null.” — Spring Framework Reference.'
))

B(p(
    'En el proyecto usamos Lombok para evitar escribir el constructor a mano: '
    '@RequiredArgsConstructor genera automáticamente el constructor con todos los '
    'campos final. Es exactamente lo mismo que en Nest, donde los providers se '
    'inyectan a través del constructor:'
))

B(code_block(
    "// Spring (Java)\n"
    "@Service\n"
    "@RequiredArgsConstructor\n"
    "public class ClienteService {\n"
    "    private final ClienteRepository repo;  // inyección por constructor\n"
    "}\n"
    "\n"
    "// Nest (TypeScript) — análogo directo\n"
    "@Injectable()\n"
    "export class ClienteService {\n"
    "    constructor(private readonly repo: ClienteRepository) {}\n"
    "}"
))
B(page_break())

# ============================ 4. CONFIGURACION ============================
B(heading('4. Configuración: application.properties y autoconfiguración', 1))

B(p(
    'En Spring Boot la configuración vive en src/main/resources/application.properties '
    '(también puede ser .yml). Esa convención cumple el mismo rol que en Nest cumple '
    'ConfigModule + un .env, solo que aquí está integrada al framework de fábrica.'
))

B(heading('4.1 Lo que configuramos en el proyecto', 2))
B(code_block(
    "# Conexión a PostgreSQL\n"
    "spring.datasource.url=jdbc:postgresql://localhost:5432/expo_jpa\n"
    "spring.datasource.username=postgres\n"
    "spring.datasource.password=********\n"
    "spring.datasource.driver-class-name=org.postgresql.Driver\n"
    "\n"
    "# Hibernate\n"
    "spring.jpa.hibernate.ddl-auto=create-drop\n"
    "spring.jpa.show-sql=true\n"
    "spring.jpa.properties.hibernate.format_sql=true\n"
    "spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.PostgreSQLDialect\n"
    "\n"
    "# Carga de data.sql después de que Hibernate cree el schema\n"
    "spring.jpa.defer-datasource-initialization=true\n"
    "spring.sql.init.mode=always\n"
    "\n"
    "# Puerto del servidor\n"
    "server.port=8080"
))

B(heading('4.2 La propiedad clave: ddl-auto', 2))
B(p(
    'spring.jpa.hibernate.ddl-auto define qué hace Hibernate con el esquema cuando '
    'arranca la aplicación. Hay cinco valores. Conviene memorizarlos:'
))
B(bullet_runs(
    run('none', mono=True, bold=True),
    run(' — no toca la BD. Es lo correcto en producción (el esquema lo gestionan '
        'herramientas dedicadas como Flyway o Liquibase).'),
))
B(bullet_runs(
    run('validate', mono=True, bold=True),
    run(' — arranca solo si el esquema actual coincide con las entidades; si no, '
        'falla.'),
))
B(bullet_runs(
    run('update', mono=True, bold=True),
    run(' — agrega columnas/tablas faltantes. Útil en desarrollo.'),
))
B(bullet_runs(
    run('create', mono=True, bold=True),
    run(' — borra y crea TODO al arrancar.'),
))
B(bullet_runs(
    run('create-drop', mono=True, bold=True),
    run(' — crea al arrancar y borra al apagar (lo que usamos para la demo).'),
))

B(heading('4.3 Autoconfiguración: la magia explicada', 2))
B(p(
    'Cuando Spring Boot ve en el classpath spring-boot-starter-data-jpa y un driver '
    'JDBC, automáticamente: configura un DataSource, configura Hibernate como '
    'proveedor JPA, registra un EntityManager y un PlatformTransactionManager, '
    'arranca Spring Data JPA. Ninguna de esas piezas la declaramos a mano.'
))

B(quote_block(
    '“The spring-boot-starter-data-jpa POM provides … Hibernate: One of the most '
    'popular JPA implementations. Spring Data JPA … Spring ORM.” — Spring Boot Reference, '
    'sección JPA and Spring Data JPA.'
))
B(page_break())

# ============================ 5. PERSISTENCIA: JPA ============================
B(heading('5. Persistencia: JPA, Jakarta Persistence e Hibernate', 1))

B(heading('5.1 JPA, Hibernate y Jakarta: las piezas', 2))
B(p(
    'JPA (Java Persistence API) es una especificación: define las anotaciones (@Entity, '
    '@Table, @Id, @OneToMany…) y los contratos (EntityManager, Query…) que debe ofrecer '
    'cualquier implementación. La especificación, en sí, no se ejecuta.'
))
B(p(
    'Hibernate es la implementación de JPA más usada. Es la que efectivamente traduce '
    'objetos a SQL y viceversa. Spring Boot la incluye por defecto cuando se agrega '
    'el starter de JPA.'
))
B(p(
    'Cuando Java EE pasó de Oracle a la Eclipse Foundation, se renombró a Jakarta EE. '
    'Por eso ahora las anotaciones viven en el paquete jakarta.persistence (antes '
    'javax.persistence). El cambio es de namespace, los conceptos siguen siendo los mismos.'
))

B(heading('5.2 ¿Qué es un ORM y por qué lo usamos?', 2))
B(p(
    'ORM (Object-Relational Mapping) es la técnica de traducir entre dos modelos: '
    'el orientado a objetos del lenguaje y el relacional de la base de datos. '
    'En Nest, TypeORM y Prisma cumplen ese rol. En Java, Hibernate.'
))
B(p(
    'La promesa del ORM es: trabajamos con objetos y dejamos que el ORM genere el SQL. '
    'En la práctica conviene saber qué SQL produce y, sobre todo, los puntos donde puede '
    'tirar abajo la performance (ver el problema N+1 más adelante).'
))

B(heading('5.3 Estados del ciclo de vida de una entidad', 2))
B(p(
    'JPA define cuatro estados en los que puede estar un objeto Entity. Entender '
    'esto es clave para comprender por qué a veces no llamamos a save().'
))

B(table(
    ['Estado', 'Significado'],
    [
        ['NEW (Transient)',
         'Objeto recién creado con new, sin ID, no asociado al EntityManager.'],
        ['MANAGED (Persistent)',
         'El objeto está en el "persistence context"; cualquier cambio será detectado.'],
        ['DETACHED',
         'Estuvo MANAGED, pero la transacción terminó; ya no se sincroniza.'],
        ['REMOVED',
         'Se llamó a remove(): se borrará en el flush de la transacción.'],
    ],
    col_widths=[2200, 6800],
))

B(heading('5.4 Dirty checking: por qué actualizar sin llamar a save()', 2))
B(p(
    'Mientras una entidad está en estado MANAGED y la transacción está abierta, '
    'Hibernate detecta automáticamente cualquier cambio en sus campos. Al hacer '
    'commit, genera el UPDATE correspondiente. A esto se le llama dirty checking '
    '(detección de cambios) y es una de las funcionalidades más potentes —y '
    'desconocidas— de JPA.'
))
B(p(
    'En el servicio del proyecto, fijate cómo actualizamos un cliente:'
))
B(code_block(
    "@Transactional\n"
    "public ClienteDto actualizar(Long id, ClienteDto dto) {\n"
    "    Cliente cliente = buscar(id);    // queda en estado MANAGED\n"
    "    cliente.setNombres(dto.nombres());\n"
    "    cliente.setApellidos(dto.apellidos());\n"
    "    cliente.setEmail(dto.email());\n"
    "    // SIN repo.save(): dirty checking detecta los cambios y\n"
    "    // emite el UPDATE al hacer commit de la transacción.\n"
    "    return aDto(cliente);\n"
    "}"
))
B(p(
    'En Nest con TypeORM, el equivalente sería tener que llamar a save() o update() '
    'explícitamente. JPA lo ofrece automático mientras la transacción esté abierta.'
))
B(page_break())

# ============================ 6. ENTIDADES ============================
B(heading('6. Modelado de entidades', 1))

B(p(
    'Una entidad es una clase Java que JPA mapea a una tabla. Se anota con @Entity '
    'y, opcionalmente, con @Table para personalizar nombre, índices y restricciones.'
))

B(heading('6.1 Anatomía de la entidad Cliente', 2))
B(code_block(
    "@Entity\n"
    "@Table(name = \"clientes\", indexes = {\n"
    "    @Index(name = \"idx_cliente_dni\", columnList = \"dni\", unique = true),\n"
    "    @Index(name = \"idx_cliente_email\", columnList = \"email\")\n"
    "})\n"
    "@Getter @Setter\n"
    "@NoArgsConstructor @AllArgsConstructor @Builder\n"
    "public class Cliente {\n"
    "\n"
    "    @Id\n"
    "    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = \"clientes_seq\")\n"
    "    @SequenceGenerator(name = \"clientes_seq\", sequenceName = \"clientes_id_seq\",\n"
    "                       allocationSize = 1)\n"
    "    private Long id;\n"
    "\n"
    "    @NotBlank @Size(max = 100)\n"
    "    @Column(nullable = false, length = 100)\n"
    "    private String nombres;\n"
    "    // ... más campos\n"
    "}"
))

B(heading('6.2 Estrategias de generación de ID', 2))
B(p(
    'Cuando ponemos @GeneratedValue le decimos a JPA que delegue la creación del ID. '
    'Hay cuatro estrategias. La que usamos —y la recomendada en PostgreSQL— es SEQUENCE.'
))
B(bullet_runs(
    run('IDENTITY', mono=True, bold=True),
    run(' — usa una columna auto-incremental (BIGSERIAL en Postgres). '
        'Problema: deshabilita los inserts en lote de Hibernate.'),
))
B(bullet_runs(
    run('SEQUENCE', mono=True, bold=True),
    run(' — usa una secuencia de la BD. Hibernate puede pre-pedir un rango de IDs '
        '(allocationSize) y batchear los inserts. Es la mejor opción en Postgres.'),
))
B(bullet_runs(
    run('TABLE', mono=True, bold=True),
    run(' — emula una secuencia con una tabla. Lento; evitar.'),
))
B(bullet_runs(
    run('AUTO', mono=True, bold=True),
    run(' — Hibernate elige según el dialecto. Aceptable, pero el comportamiento '
        'depende de detalles internos.'),
))

B(p(
    'En Movimiento usamos allocationSize = 50: cada vez que necesitamos IDs, '
    'Hibernate reserva 50 de una. Si el endpoint registra muchos movimientos seguidos '
    '(por ejemplo, una transferencia masiva), reduce a la mitad los roundtrips a la BD.'
))

B(heading('6.3 Tipos: por qué BigDecimal y no double', 2))
B(p(
    'Para representar dinero NUNCA se usa float ni double. Son tipos de punto '
    'flotante binario: no representan exactamente decimales como 0.1 o 19.99. Después '
    'de unas pocas operaciones aparecen errores de redondeo de céntimos. La '
    'documentación oficial de Java lo dice explícitamente:'
))

B(quote_block(
    '“new BigDecimal(0.1) … is actually equal to 0.1000000000000000055511151231257827…” '
    '— Javadoc de java.math.BigDecimal.'
))

B(p(
    'BigDecimal es un tipo de precisión arbitraria que sí representa decimales '
    'exactos. En las columnas usamos precision = 19 y scale = 2: hasta 17 dígitos '
    'enteros y 2 decimales (suficiente para soles, dólares, etc.).'
))

B(heading('6.4 Enums: @Enumerated(EnumType.STRING)', 2))
B(p(
    'Un enum se puede guardar de dos formas en la BD: como número (ORDINAL, default) '
    'o como cadena (STRING). La documentación oficial y la experiencia coinciden en '
    'usar STRING:'
))
B(bullet('Si guardás ORDINAL y mañana reordenás los valores del enum, los datos viejos '
         'quedan corruptos: el "0" sigue queriendo decir DEPOSITO, pero ahora apunta a otra cosa.'))
B(bullet('STRING guarda "DEPOSITO" como texto: legible, robusto a reordenamientos.'))

B(heading('6.5 Callbacks de ciclo de vida: @PrePersist', 2))
B(p(
    'JPA permite engancharse a momentos clave del ciclo de vida con anotaciones '
    'como @PrePersist (antes de INSERT), @PreUpdate, @PostLoad… En el proyecto las '
    'usamos para setear automáticamente fechas:'
))
B(code_block(
    "@PrePersist\n"
    "void onCreate() {\n"
    "    this.fechaRegistro = LocalDateTime.now();\n"
    "}"
))

B(heading('6.6 Lombok y la advertencia con @Data', 2))
B(p(
    'Lombok es una librería que genera código repetitivo en tiempo de compilación: '
    'getters, setters, constructores, equals/hashCode, toString. Nos ahorra mucho '
    'boilerplate.'
))
B(p(
    'Pero hay una regla: NO se debe usar @Data en entidades JPA con relaciones '
    'bidireccionales. ¿Por qué?'
))
B(bullet(
    'El equals/hashCode generado por @Data usa todos los campos. Eso rompe el '
    'contrato cuando el ID es asignado por la BD: el hash del objeto cambia entre '
    'antes y después de persistir. Una entidad puede "desaparecer" de un HashSet.'
))
B(bullet(
    'El toString generado recorre todos los campos, incluidas las colecciones de la '
    'relación inversa, lo que dispara LazyInitializationException o, peor, una '
    'recursión infinita.'
))
B(p(
    'Por eso en este proyecto usamos @Getter @Setter @NoArgsConstructor explícitos '
    'y armamos equals/hashCode manualmente cuando hace falta. Esta es una de esas '
    'lecciones que cuestan caras de aprender.'
))
B(page_break())

# ============================ 7. RELACIONES ============================
B(heading('7. Relaciones entre entidades (1-N, N-1, M-N)', 1))

B(p(
    'En el proyecto modelamos las tres relaciones clásicas:'
))
B(bullet('Cliente 1—N Cuenta (un cliente tiene muchas cuentas).'))
B(bullet('Cuenta 1—N Movimiento (una cuenta tiene muchos movimientos).'))
B(bullet('Cuenta M—N Producto (una cuenta tiene varios productos y viceversa).'))

B(heading('7.1 Lado dueño y mappedBy', 2))
B(p(
    'En toda relación bidireccional hay un "lado dueño" que efectivamente lleva la '
    'clave foránea, y un "lado inverso" que solo refleja la relación. La regla:'
))
B(bullet('El lado dueño es el que tiene @JoinColumn (o @JoinTable en M-N).'))
B(bullet('El lado inverso usa mappedBy = "campoDelDueño".'))

B(p(
    'En la relación Cliente—Cuenta, la FK cliente_id vive en la tabla cuentas. Por '
    'lo tanto, Cuenta es la dueña; Cliente es el lado inverso y declara '
    'mappedBy = "cliente". Si te equivocás de lado, JPA crea una tabla intermedia '
    'innecesaria.'
))

B(heading('7.2 FetchType: LAZY vs EAGER', 2))
B(p(
    'Cada relación se carga de la BD de dos formas: ahora (EAGER) o cuando la pida '
    '(LAZY). Los defaults definidos por la especificación Jakarta Persistence son:'
))
B(table(
    ['Relación', 'Default oficial', 'Recomendación'],
    [
        ['@OneToOne', 'EAGER', 'Cambiar a LAZY explícitamente'],
        ['@ManyToOne', 'EAGER', 'Cambiar a LAZY explícitamente'],
        ['@OneToMany', 'LAZY', 'Mantener LAZY'],
        ['@ManyToMany', 'LAZY', 'Mantener LAZY'],
    ],
    col_widths=[2400, 2400, 4200],
))
B(p(
    'En el proyecto siempre marcamos fetch = FetchType.LAZY de manera explícita, '
    'incluso donde ya es el default. Es defensivo y deja la intención clara.'
))

B(heading('7.3 El problema N+1 y @EntityGraph', 2))
B(p(
    'Imaginá que listamos 100 clientes y, para cada uno, accedemos a sus cuentas. '
    'Con LAZY, JPA emite 1 query para traer los clientes y otras 100 queries (una '
    'por cliente) para traer sus cuentas. Eso son 101 queries para una operación que '
    'debería ser 1 con un JOIN. Es el problema N+1.'
))
B(p(
    'La solución oficial es @EntityGraph: una pista a JPA para que cargue ciertas '
    'relaciones en la misma query. Mirá ClienteRepository:'
))
B(code_block(
    "@EntityGraph(attributePaths = \"cuentas\")\n"
    "@Query(\"SELECT c FROM Cliente c WHERE c.id = :id\")\n"
    "Optional<Cliente> findByIdConCuentas(@Param(\"id\") Long id);"
))
B(p(
    'Con esto, cuentas se trae junto con el cliente en un solo SELECT con LEFT JOIN.'
))

B(heading('7.4 Cascade y orphanRemoval', 2))
B(p(
    'CascadeType propaga operaciones a las entidades relacionadas. Los valores definidos '
    'en Jakarta Persistence son: PERSIST, MERGE, REMOVE, REFRESH, DETACH y ALL '
    '(que equivale a los cinco anteriores).'
))
B(p(
    'orphanRemoval = true es distinto a CascadeType.REMOVE: dispara DELETE cuando '
    'sacás un hijo de la colección del padre (no solo cuando se borra el padre). '
    'Útil para manejar colecciones donde los hijos no tienen vida fuera del padre.'
))

B(heading('7.5 Relación M-N: la tabla intermedia', 2))
B(p(
    'En una relación muchos-a-muchos hace falta una tabla puente. Con @JoinTable se '
    'la describimos a JPA:'
))
B(code_block(
    "@ManyToMany(fetch = FetchType.LAZY)\n"
    "@JoinTable(\n"
    "    name = \"cuentas_productos\",\n"
    "    joinColumns = @JoinColumn(name = \"cuenta_id\"),\n"
    "    inverseJoinColumns = @JoinColumn(name = \"producto_id\")\n"
    ")\n"
    "private Set<Producto> productos = new HashSet<>();"
))
B(p(
    'En el lado inverso (Producto) solo va @ManyToMany(mappedBy = "productos"). Set '
    'en lugar de List evita duplicados y mejora la performance del contains().'
))
B(page_break())

# ============================ 8. SPRING DATA JPA ============================
B(heading('8. Spring Data JPA y los repositorios', 1))

B(heading('8.1 ¿Qué es JpaRepository?', 2))
B(p(
    'Spring Data JPA nos permite crear repositorios sin escribir su implementación. '
    'Solo declaramos una interface que extienda JpaRepository<Entidad, TipoDelId> y '
    'Spring genera la implementación en tiempo de ejecución (proxy dinámico).'
))
B(quote_block(
    '“Those interfaces extend CrudRepository and expose the capabilities of the '
    'underlying persistence technology in addition to the rather generic persistence '
    'technology-agnostic interfaces such as CrudRepository.” — Spring Data Commons.'
))

B(p(
    'JpaRepository nos da gratis: save, saveAll, findById, findAll, count, delete, '
    'deleteAll, existsById, flush, saveAndFlush, etc. La equivalencia en Nest sería '
    'el repositorio de TypeORM, que también provee find, findOne, save, delete sin '
    'escribir SQL a mano.'
))

B(heading('8.2 Tres niveles de "consulta gratis"', 2))
B(bullet('CRUD básico — viene de fábrica al extender JpaRepository.'))
B(bullet('Derived queries — métodos cuyo nombre describe la query.'))
B(bullet('Consultas explícitas con @Query — JPQL o SQL nativo.'))

B(heading('8.3 Derived queries: el nombre del método ES la query', 2))
B(p(
    'Spring parsea el nombre del método y arma la consulta. Algunos ejemplos del proyecto:'
))

B(table(
    ['Método', 'SQL aproximado'],
    [
        ['findByDni(String)', 'SELECT * FROM clientes WHERE dni = ?'],
        ['findByApellidosContainingIgnoreCase(s)', 'WHERE LOWER(apellidos) LIKE LOWER(\'%s%\')'],
        ['existsByNumeroCuenta(String)', 'SELECT COUNT(*) > 0 ... WHERE numero_cuenta = ?'],
        ['findBySaldoGreaterThan(BigDecimal)', 'WHERE saldo > ?'],
        ['findByCuentaIdOrderByFechaDesc(...)', 'WHERE cuenta_id = ? ORDER BY fecha DESC'],
    ],
    col_widths=[4400, 4600],
))

B(p(
    'Las palabras clave reconocidas (subjects y predicates) están documentadas en la '
    'guía oficial de Spring Data: findBy, readBy, getBy, queryBy, existsBy, countBy, '
    'deleteBy, etc. Más modificadores como Distinct, First<n>, Top<n>, Containing, '
    'StartingWith, IgnoreCase, OrderBy, etc.'
))

B(heading('8.4 Paginación: Pageable y Page<T>', 2))
B(p(
    'Cuando un endpoint puede devolver muchos registros, devolvemos páginas. Spring Data '
    'lo soporta nativo:'
))
B(code_block(
    "Page<Cuenta> findByClienteId(Long clienteId, Pageable pageable);\n"
    "// El controller recibe Pageable directamente:\n"
    "@GetMapping(\"/cliente/{clienteId}\")\n"
    "public Page<CuentaDto> porCliente(@PathVariable Long clienteId, Pageable pageable) {\n"
    "    return service.listarPorCliente(clienteId, pageable);\n"
    "}\n"
    "// Y el cliente HTTP lo controla con query params:\n"
    "// GET /api/cuentas/cliente/5?page=0&size=10&sort=saldo,desc"
))
B(p(
    'Page<T>.map(...) además convierte el contenido (entidades) a DTOs preservando '
    'la metadata (totalPages, totalElements, etc.).'
))
B(page_break())

# ============================ 9. CONSULTAS ============================
B(heading('9. Estilos de consulta: derivadas, JPQL y nativas', 1))

B(p(
    'En el proyecto mostramos los cuatro estilos a propósito, para que se vea cuándo '
    'conviene cada uno.'))

B(heading('9.1 JPQL (Java Persistence Query Language)', 2))
B(p(
    'JPQL es un lenguaje parecido a SQL pero que opera sobre ENTIDADES y CAMPOS Java, '
    'no sobre tablas y columnas. Es portable entre motores de BD (Postgres, MySQL, Oracle…). '
    'Hibernate lo traduce al SQL del dialecto configurado.'
))
B(code_block(
    "@Query(\"\"\"\n"
    "       SELECT c FROM Cuenta c\n"
    "       WHERE c.cliente.dni = :dni\n"
    "         AND c.saldo >= :minimo\n"
    "       ORDER BY c.saldo DESC\n"
    "       \"\"\")\n"
    "List<Cuenta> buscarPorDniConSaldoMinimo(\n"
    "    @Param(\"dni\") String dni,\n"
    "    @Param(\"minimo\") BigDecimal minimo\n"
    ");"
))

B(heading('9.2 Proyecciones', 2))
B(p(
    'Cuando solo necesitamos un agregado (SUM, COUNT, AVG…) no traemos entidades, '
    'traemos el escalar:'
))
B(code_block(
    "@Query(\"SELECT COALESCE(SUM(c.saldo), 0) FROM Cuenta c \"\n"
    "      + \"WHERE c.cliente.id = :clienteId\")\n"
    "BigDecimal sumarSaldosDeCliente(@Param(\"clienteId\") Long clienteId);"
))
B(p(
    'COALESCE protege contra NULL cuando el cliente no tiene cuentas. La consulta '
    'devuelve un BigDecimal escalar, no una colección.'
))

B(heading('9.3 UPDATE/DELETE: @Modifying', 2))
B(p(
    'Cuando una @Query no es un SELECT, hace falta marcarla con @Modifying. Sin esa '
    'anotación, Spring Data asume SELECT y la ejecución falla.'
))
B(code_block(
    "@Modifying\n"
    "@Query(\"UPDATE Cuenta c SET c.saldo = c.saldo + :monto WHERE c.id = :id\")\n"
    "int incrementarSaldo(@Param(\"id\") Long id, @Param(\"monto\") BigDecimal monto);"
))
B(p(
    'El service que invoque este método debe estar dentro de una transacción de '
    'lectura+escritura (@Transactional, sin readOnly).'
))

B(heading('9.4 Native queries: SQL crudo', 2))
B(p(
    'Cuando JPQL no alcanza —por ejemplo, queremos usar funciones específicas de '
    'Postgres como window functions, CTEs, JSON, expresiones regulares— pasamos a '
    'SQL nativo con nativeQuery = true:'
))
B(code_block(
    "@Query(value = \"\"\"\n"
    "        SELECT c.* FROM cuentas c\n"
    "        WHERE c.saldo > (SELECT AVG(saldo) FROM cuentas)\n"
    "        ORDER BY c.saldo DESC\n"
    "        LIMIT :limite\n"
    "        \"\"\", nativeQuery = true)\n"
    "List<Cuenta> topCuentasPorEncimaDelPromedio(@Param(\"limite\") int limite);"
))
B(p(
    'El costo: pierde portabilidad. Si mañana migrás a otro motor, las consultas '
    'nativas hay que reescribirlas.'
))
B(page_break())

# ============================ 10. SERVICIOS Y TX ============================
B(heading('10. Capa de servicios y transacciones (@Transactional)', 1))

B(heading('10.1 ¿Qué es una transacción?', 2))
B(p(
    'Una transacción es una unidad atómica de trabajo: o se completa entera, o no '
    'se aplica nada. Es el contrato del que dependen las operaciones financieras: '
    'una transferencia que descuenta de origen pero falla al sumar al destino DEBE '
    'revertir el descuento.'
))

B(heading('10.2 @Transactional en Spring', 2))
B(p(
    '@Transactional envuelve un método (o todos los métodos de una clase) en una '
    'transacción gestionada por Spring. Es la abstracción declarativa: en lugar de '
    'manejar begin/commit/rollback a mano, Spring lo hace por nosotros mediante '
    'un proxy.'
))
B(p(
    'Aplicado a nivel de clase con readOnly = true, marca todos los métodos como '
    'lectura por defecto. Hibernate desactiva dirty checking, lo que es más eficiente.'
))
B(code_block(
    "@Service\n"
    "@RequiredArgsConstructor\n"
    "@Transactional(readOnly = true)   // default de la clase: solo lectura\n"
    "public class ClienteService {\n"
    "\n"
    "    public List<ClienteDto> listar() { ... }   // hereda readOnly\n"
    "\n"
    "    @Transactional                              // sobrescribe: lectura+escritura\n"
    "    public ClienteDto crear(ClienteDto dto) { ... }\n"
    "}"
))

B(heading('10.3 Regla de rollback (esto sorprende mucho)', 2))
B(p(
    'Por defecto, Spring solo hace ROLLBACK ante RuntimeException o Error. '
    'Las excepciones "checked" (las que extienden Exception y deben declararse en '
    'throws) NO disparan rollback automático. La cita textual:'
))
B(quote_block(
    '“In its default configuration, the Spring Framework\'s transaction infrastructure '
    'code marks a transaction for rollback only in the case of runtime, unchecked '
    'exceptions. … Checked exceptions … do not result in a rollback in the default '
    'configuration.” — Spring Framework Reference.'
))
B(p(
    'Si querés que una excepción checked también revierta, se configura: '
    '@Transactional(rollbackFor = MiExcepcionChecked.class). En el proyecto todas '
    'nuestras excepciones de negocio extienden RuntimeException, así que se '
    'comportan como esperamos.'
))

B(heading('10.4 Atomicidad real: la transferencia', 2))
B(p(
    'El método transferir del CuentaService es un caso textbook de transacción. '
    'Llama dos veces a registrarMovimiento (resta del origen, suma al destino). '
    'Como ambas llamadas ocurren dentro del mismo @Transactional, si la segunda '
    'falla (por ejemplo, la cuenta destino no existe), también se revierte el '
    'descuento de la primera. Es lo que se espera de un sistema bancario serio.'
))
B(code_block(
    "@Transactional\n"
    "public void transferir(Long origenId, Long destinoId, BigDecimal monto) {\n"
    "    if (origenId.equals(destinoId))\n"
    "        throw new IllegalArgumentException(\"Cuenta origen = destino\");\n"
    "    registrarMovimiento(origenId,  new CrearMovimientoRequest(\n"
    "        monto, TRANSFERENCIA_SALIENTE, \"...\"));\n"
    "    registrarMovimiento(destinoId, new CrearMovimientoRequest(\n"
    "        monto, TRANSFERENCIA_ENTRANTE, \"...\"));\n"
    "    // si la segunda falla, la primera se revierte automáticamente.\n"
    "}"
))

B(heading('10.5 Comparación con Nest', 2))
B(p(
    'En NestJS con TypeORM, el equivalente más cercano son los QueryRunner o los '
    'transactional decorators de typeorm-transactional. La idea es la misma: '
    'envolver una operación de varios pasos en una unidad atómica. La ventaja de '
    'Spring es que el modelo declarativo con @Transactional es más limpio y está '
    'integrado de fábrica.'
))
B(page_break())

# ============================ 11. CONTROLLERS ============================
B(heading('11. Capa web: controladores REST', 1))

B(heading('11.1 @RestController y mapeo de rutas', 2))
B(p(
    'Un controller REST en Spring es una clase anotada con @RestController. Eso le '
    'dice a Spring: "todos los métodos devuelven JSON, serializado al body de la '
    'respuesta". @RequestMapping a nivel de clase fija el prefijo común de la URL.'
))
B(code_block(
    "@RestController\n"
    "@RequestMapping(\"/api/clientes\")\n"
    "@RequiredArgsConstructor\n"
    "public class ClienteController {\n"
    "    private final ClienteService service;\n"
    "}"
))

B(heading('11.2 Las anotaciones de los verbos HTTP', 2))
B(table(
    ['Anotación', 'Verbo HTTP', 'Equivalente en Nest'],
    [
        ['@GetMapping', 'GET', '@Get()'],
        ['@PostMapping', 'POST', '@Post()'],
        ['@PutMapping', 'PUT', '@Put()'],
        ['@PatchMapping', 'PATCH', '@Patch()'],
        ['@DeleteMapping', 'DELETE', '@Delete()'],
    ],
    col_widths=[2800, 2200, 4000],
))

B(heading('11.3 Cómo se reciben los parámetros', 2))
B(table(
    ['Anotación', 'De dónde sale', 'Ejemplo'],
    [
        ['@PathVariable', 'Segmento de la URL', '/clientes/{id}'],
        ['@RequestParam', 'Query string', '?limite=5'],
        ['@RequestBody', 'Body JSON', 'POST /clientes con body'],
        ['Pageable', 'Query string', '?page=0&size=10&sort=saldo,desc'],
    ],
    col_widths=[2400, 2600, 4000],
))

B(heading('11.4 @ResponseStatus: el código HTTP correcto', 2))
B(p(
    'Por defecto, un endpoint que se ejecuta bien responde 200 OK. Para operaciones '
    'que crean (201 Created) o que no devuelven body (204 No Content), agregamos '
    '@ResponseStatus. En el proyecto:'
))
B(code_block(
    "@PostMapping\n"
    "@ResponseStatus(HttpStatus.CREATED)        // 201\n"
    "public ClienteDto crear(@Valid @RequestBody ClienteDto dto) { ... }\n"
    "\n"
    "@DeleteMapping(\"/{id}\")\n"
    "@ResponseStatus(HttpStatus.NO_CONTENT)     // 204, sin body\n"
    "public void eliminar(@PathVariable Long id) { ... }"
))
B(page_break())

# ============================ 12. VALIDACION ============================
B(heading('12. Validación con Bean Validation', 1))

B(heading('12.1 Jakarta Validation (antes JSR-380)', 2))
B(p(
    'Bean Validation es la especificación estándar de Jakarta para validar objetos. '
    'En el proyecto la usamos en dos lugares: en los DTOs (validación del input HTTP) '
    'y en las entidades (refuerzo a nivel de modelo).'))

B(p('Las anotaciones más comunes:'))
B(table(
    ['Anotación', 'Significado', 'Equivalente en class-validator (Nest)'],
    [
        ['@NotNull', 'El campo no puede ser null', '@IsNotEmpty()'],
        ['@NotBlank', 'String no nulo y no vacío (sin solo espacios)', '@IsString() + @IsNotEmpty()'],
        ['@Size(min, max)', 'Longitud o tamaño entre min y max', '@Length()'],
        ['@Email', 'Formato de email', '@IsEmail()'],
        ['@Positive', 'Número estrictamente > 0', '@IsPositive()'],
        ['@PositiveOrZero', 'Número >= 0', '@Min(0)'],
        ['@Pattern(regexp)', 'Coincide con un regex', '@Matches()'],
    ],
    col_widths=[2400, 3200, 3400],
))

B(heading('12.2 @Valid: dispara la validación', 2))
B(p(
    'En el controller, agregar @Valid antes de @RequestBody hace que Spring valide '
    'el DTO antes de invocar el método. Si alguna restricción falla, lanza '
    'MethodArgumentNotValidException, que después atraparemos en el handler global.'
))
B(code_block(
    "@PostMapping\n"
    "@ResponseStatus(HttpStatus.CREATED)\n"
    "public ClienteDto crear(@Valid @RequestBody ClienteDto dto) {\n"
    "    return service.crear(dto);\n"
    "}"
))

B(heading('12.3 Comparativa con Nest', 2))
B(p(
    'En NestJS, lo equivalente es: clase con decoradores de class-validator '
    '(@IsString, @IsEmail, @Length, etc.) y un ValidationPipe registrado de manera '
    'global. La filosofía es idéntica: validación declarativa, en el borde, antes '
    'de que la lógica de negocio reciba datos sucios.'
))
B(page_break())

# ============================ 13. MANEJO DE ERRORES ============================
B(heading('13. Manejo global de errores', 1))

B(heading('13.1 @RestControllerAdvice + @ExceptionHandler', 2))
B(p(
    'En lugar de envolver cada método con try/catch, Spring permite definir handlers '
    'globales que interceptan excepciones de TODOS los controllers. La pieza es '
    '@RestControllerAdvice (@ControllerAdvice + @ResponseBody). Adentro, cada '
    'método anotado con @ExceptionHandler maneja un tipo de excepción.'
))

B(p('La cita oficial:'))
B(quote_block(
    '“@RestControllerAdvice is a … shortcut annotation that combines @ControllerAdvice '
    'with @ResponseBody, in effect simply an @ControllerAdvice whose exception handler '
    'methods render to the response body.” — Spring Framework Reference.'
))

B(heading('13.2 Lo que hicimos en GlobalExceptionHandler', 2))
B(code_block(
    "@RestControllerAdvice\n"
    "public class GlobalExceptionHandler {\n"
    "\n"
    "    public record ErrorResponse(\n"
    "        LocalDateTime timestamp,\n"
    "        int status,\n"
    "        String error,\n"
    "        Object detalle\n"
    "    ) {}\n"
    "\n"
    "    @ExceptionHandler(RecursoNoEncontradoException.class)\n"
    "    public ResponseEntity<ErrorResponse> noEncontrado(...) {\n"
    "        return build(HttpStatus.NOT_FOUND, ex.getMessage(), null);\n"
    "    }\n"
    "\n"
    "    @ExceptionHandler(SaldoInsuficienteException.class)\n"
    "    public ResponseEntity<ErrorResponse> saldoInsuficiente(...) {\n"
    "        return build(HttpStatus.UNPROCESSABLE_ENTITY, ex.getMessage(), null);\n"
    "    }\n"
    "\n"
    "    @ExceptionHandler(MethodArgumentNotValidException.class)\n"
    "    public ResponseEntity<ErrorResponse> validacion(...) {\n"
    "        // arma { campo: mensaje } para cada error de @Valid\n"
    "    }\n"
    "}"
))

B(heading('13.3 Códigos HTTP que devolvemos', 2))
B(table(
    ['Excepción', 'HTTP', 'Cuándo'],
    [
        ['RecursoNoEncontradoException', '404 Not Found', 'ID no existe'],
        ['SaldoInsuficienteException', '422 Unprocessable Entity', 'Regla de negocio'],
        ['MethodArgumentNotValidException', '400 Bad Request', 'Validación de DTO'],
        ['Exception (catch-all)', '500 Internal Server Error', 'Otras'],
    ],
    col_widths=[3200, 2200, 3600],
))

B(heading('13.4 Comparativa con Nest', 2))
B(p(
    'En NestJS lo equivalente es ExceptionFilter con @Catch(MiException). El '
    'patrón es 1 a 1: handler global, mapeado por tipo de excepción, devolviendo '
    'una estructura uniforme. Spring lo expone con anotaciones; Nest con un '
    'filter registrado en el módulo o globalmente.'
))
B(page_break())

# ============================ 14. DTOs ============================
B(heading('14. DTOs: por qué no devolvemos entidades', 1))

B(p(
    'DTO (Data Transfer Object) es un objeto que solo lleva datos: lo que viaja '
    'entre capas o sale al cliente HTTP. La regla del proyecto: las entidades NUNCA '
    'salen del service. Hacia el controller solo viajan DTOs.'
))

B(heading('14.1 Tres razones técnicas', 2))
B(bullet(
    'Seguridad: las entidades pueden tener campos internos (passwords, datos '
    'sensibles, IDs internos) que no queremos exponer.'
))
B(bullet(
    'Errores de serialización: las entidades con relaciones bidireccionales caen en '
    'recursión al serializarse a JSON. Los DTOs son planos.'
))
B(bullet(
    'Acoplamiento: si cambia la estructura de la BD pero la API debe mantenerse '
    'estable, los DTOs son la frontera que protege al cliente.'
))

B(heading('14.2 Records: la forma elegante en Java moderno', 2))
B(p(
    'A partir de Java 14 existen los records: clases inmutables con getters '
    'automáticos generados por el compilador. Son ideales para DTOs:'
))
B(code_block(
    "public record ClienteDto(\n"
    "    Long id,\n"
    "    @NotBlank @Size(max = 100) String nombres,\n"
    "    @NotBlank @Size(max = 100) String apellidos,\n"
    "    @NotBlank @Size(min = 8, max = 8) String dni,\n"
    "    @Email String email\n"
    ") {}"
))

B(heading('14.3 Separar input y output', 2))
B(p(
    'Cuando el DTO de entrada y el de salida son distintos, se separan. En el '
    'proyecto, para crear una cuenta se reciben solo los campos necesarios:'
))
B(code_block(
    "// DTO de ENTRADA: lo que el cliente HTTP envía\n"
    "public record CrearCuentaRequest(\n"
    "    @NotBlank String numeroCuenta,\n"
    "    @NotNull @PositiveOrZero BigDecimal saldoInicial,\n"
    "    @NotNull Long clienteId\n"
    ") {}\n"
    "\n"
    "// DTO de SALIDA: lo que devolvemos al cliente\n"
    "public record CuentaDto(\n"
    "    Long id,\n"
    "    String numeroCuenta,\n"
    "    BigDecimal saldo,\n"
    "    LocalDateTime fechaApertura,\n"
    "    Long clienteId,\n"
    "    String clienteNombreCompleto\n"
    ") {}"
))
B(p(
    'En Nest, lo equivalente es tener CreateUserDto y UserResponseDto (o '
    'UpdateUserDto). El principio "separar entrada y salida" es universal.'
))
B(page_break())

# ============================ 15. COMPARATIVA ============================
B(heading('15. Comparativa NestJS ↔ Spring (tabla resumen)', 1))

B(p(
    'Para cerrar la parte teórica, esta tabla resume todas las equivalencias en '
    'una sola vista. Memorizándola, traducir un código de Nest a Spring (o al revés) '
    'se vuelve casi mecánico.'
))

B(table(
    ['Concepto', 'NestJS', 'Spring Boot'],
    [
        ['Entrypoint',
         'main.ts → bootstrap()',
         '@SpringBootApplication + main()'],
        ['Inyección de dependencias',
         'IoC container de Nest',
         'IoC container de Spring'],
        ['Marcar provider',
         '@Injectable()',
         '@Component / @Service / @Repository'],
        ['Inyección',
         'constructor(...) {}',
         'constructor + @Autowired (implícito)'],
        ['Controller HTTP',
         '@Controller + @Get/@Post',
         '@RestController + @GetMapping/@PostMapping'],
        ['Path param',
         '@Param("id")',
         '@PathVariable Long id'],
        ['Query param',
         '@Query("limite")',
         '@RequestParam int limite'],
        ['Body',
         '@Body() dto',
         '@RequestBody Dto dto'],
        ['Validación',
         'class-validator + ValidationPipe',
         'Bean Validation + @Valid'],
        ['Errores globales',
         'ExceptionFilter + @Catch',
         '@RestControllerAdvice + @ExceptionHandler'],
        ['Status code',
         '@HttpCode(204)',
         '@ResponseStatus(HttpStatus.NO_CONTENT)'],
        ['ORM entity',
         '@Entity (TypeORM)',
         '@Entity (JPA)'],
        ['Repositorio',
         'TypeORM Repository / Prisma client',
         'JpaRepository (Spring Data)'],
        ['Transacciones',
         'QueryRunner / typeorm-transactional',
         '@Transactional declarativo'],
        ['Configuración',
         'ConfigModule + .env',
         'application.properties'],
        ['Servidor',
         'Express / Fastify embebido',
         'Tomcat embebido'],
        ['Lenguaje',
         'TypeScript sobre Node.js',
         'Java sobre la JVM'],
    ],
    col_widths=[2400, 3200, 3400],
))
B(page_break())

# ============================ 16. BIBLIOGRAFIA ============================
B(heading('16. Bibliografía', 1))

B(p(
    'Todas las afirmaciones técnicas de este informe están respaldadas por '
    'documentación oficial. Las URLs siguientes son las fuentes consultadas, '
    'agrupadas por tema.'
))

B(heading('Spring Framework / Spring Boot', 2))
B(bullet('@SpringBootApplication — docs.spring.io/spring-boot/api/java/org/springframework/boot/autoconfigure/SpringBootApplication.html'))
B(bullet('Inyección por constructor — docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html'))
B(bullet('Estereotipos (@Component, @Service, @Repository) — docs.spring.io/spring-framework/reference/core/beans/classpath-scanning.html'))
B(bullet('@RestController — docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-rest-worker.html'))
B(bullet('@Transactional + rollback — docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html'))
B(bullet('@RestControllerAdvice — docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-advice.html'))
B(bullet('@ExceptionHandler — docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-exceptionhandler.html'))
B(bullet('Validación + @Valid — docs.spring.io/spring-framework/reference/web/webmvc/mvc-controller/ann-validation.html'))
B(bullet('Spring Boot starter de JPA — docs.spring.io/spring-boot/reference/data/sql.html'))

B(heading('Spring Data JPA', 2))
B(bullet('Conceptos centrales (CrudRepository, JpaRepository) — docs.spring.io/spring-data/jpa/reference/repositories/core-concepts.html'))
B(bullet('Query methods (derivadas) — docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html'))
B(bullet('Tabla de keywords — docs.spring.io/spring-data/jpa/reference/repositories/query-keywords-reference.html'))
B(bullet('Paginación con Pageable — docs.spring.io/spring-data/commons/reference/repositories/core-concepts.html'))

B(heading('Jakarta Persistence (JPA) e Hibernate', 2))
B(bullet('Especificación Jakarta Persistence 3.1 — jakarta.ee/specifications/persistence/3.1/'))
B(bullet('Default fetch de @ManyToOne (EAGER) — jakarta.ee/specifications/persistence/3.1/apidocs/jakarta.persistence/jakarta/persistence/manytoone'))
B(bullet('Default fetch de @OneToMany (LAZY) — jakarta.ee/specifications/persistence/3.1/apidocs/jakarta.persistence/jakarta/persistence/onetomany'))
B(bullet('CascadeType — jakarta.ee/specifications/persistence/3.1/apidocs/jakarta.persistence/jakarta/persistence/cascadetype'))
B(bullet('Hibernate User Guide (estados, dirty checking, fetching, identifier generators) — docs.hibernate.org/orm/current/userguide/html_single/Hibernate_User_Guide.html'))

B(heading('Bean Validation', 2))
B(bullet('Especificación Jakarta Bean Validation 3.0 — jakarta.ee/specifications/bean-validation/3.0/'))

B(heading('Otras referencias', 2))
B(bullet('Lombok @Data — projectlombok.org/features/Data'))
B(bullet('java.math.BigDecimal — docs.oracle.com/javase/8/docs/api/java/math/BigDecimal.html'))
B(bullet('Vlad Mihalcea — equals/hashCode/toString en JPA — vladmihalcea.com/the-best-way-to-implement-equals-hashcode-and-tostring-with-jpa-and-hibernate/'))
B(bullet('NestJS Providers (DI/IoC) — docs.nestjs.com/providers'))
B(bullet('NestJS Controllers — docs.nestjs.com/controllers'))
B(bullet('NestJS Validation — docs.nestjs.com/techniques/validation'))
B(bullet('NestJS Exception Filters — docs.nestjs.com/exception-filters'))

B(p(''))
B(p(
    '— Fin del informe teórico —', italic=True, color='888888'
))


# ---------------------------------------------------------------------------
# Construir el archivo .docx
# ---------------------------------------------------------------------------

DOCUMENT_XML = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    f'<w:document {NS}>\n'
    '  <w:body>\n'
    + ''.join(blocks)
    + '    <w:sectPr>\n'
    '      <w:pgSz w:w="12240" w:h="15840"/>\n'
    '      <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
    'w:header="720" w:footer="720" w:gutter="0"/>\n'
    '    </w:sectPr>\n'
    '  </w:body>\n'
    '</w:document>\n'
)


def build_docx():
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", PKG_RELS)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/styles.xml", STYLES_XML)
        z.writestr("word/numbering.xml", NUMBERING_XML)
        z.writestr("word/document.xml", DOCUMENT_XML)
    print(f"OK -> {OUTPUT}")
    print(f"   Tamano: {os.path.getsize(OUTPUT)} bytes")


if __name__ == "__main__":
    build_docx()
