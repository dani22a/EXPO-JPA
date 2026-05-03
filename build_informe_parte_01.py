# -*- coding: utf-8 -*-
"""
Genera INFORME_PARTE_01.docx — informe del Integrante 1 de la exposicion.
Tema: Conceptos. ORM, JPA, Hibernate, Spring Data. 10 minutos, 100% teoria.

Reusa la maquinaria de OOXML del archivo build_informe.py (helpers de
parrafos, headings, code blocks, tablas, listas, page breaks).
"""
import os
import zipfile
from xml.sax.saxutils import escape as _esc

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "INFORME_PARTE_01.docx")

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
)


def esc(s):
    return _esc(s).replace('"', '&quot;').replace("'", '&apos;')


def run(text, *, bold=False, italic=False, mono=False, color=None, size=None):
    rpr = []
    if bold: rpr.append('<w:b/>')
    if italic: rpr.append('<w:i/>')
    if mono: rpr.append('<w:rFonts w:ascii="Consolas" w:hAnsi="Consolas" w:cs="Consolas"/>')
    if color: rpr.append(f'<w:color w:val="{color}"/>')
    if size: rpr.append(f'<w:sz w:val="{size*2}"/>')
    rpr_xml = f'<w:rPr>{"".join(rpr)}</w:rPr>' if rpr else ''
    return f'<w:r>{rpr_xml}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'


def heading(text, level=1):
    style = {1: 'Heading1', 2: 'Heading2', 3: 'Heading3'}.get(level, 'Heading1')
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{run(text, bold=True)}</w:p>'


def title(text):
    return f'<w:p><w:pPr><w:pStyle w:val="Title"/><w:jc w:val="center"/></w:pPr>{run(text, bold=True)}</w:p>'


def subtitle(text):
    return f'<w:p><w:pPr><w:jc w:val="center"/></w:pPr>{run(text, italic=True, color="555555")}</w:p>'


def para(*runs_xml, indent=0, align=None):
    pPr = []
    if indent: pPr.append(f'<w:ind w:left="{indent}"/>')
    if align: pPr.append(f'<w:jc w:val="{align}"/>')
    pPr_xml = f'<w:pPr>{"".join(pPr)}</w:pPr>' if pPr else ''
    return f'<w:p>{pPr_xml}{"".join(runs_xml)}</w:p>'


def p(text, **kw):
    return para(run(text, **kw))


def bullet(text, level=0):
    return (f'<w:p><w:pPr><w:pStyle w:val="ListBullet"/>'
            f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="1"/></w:numPr>'
            f'</w:pPr>{run(text)}</w:p>')


def bullet_runs(*runs_xml, level=0):
    return (f'<w:p><w:pPr><w:pStyle w:val="ListBullet"/>'
            f'<w:numPr><w:ilvl w:val="{level}"/><w:numId w:val="1"/></w:numPr>'
            f'</w:pPr>{"".join(runs_xml)}</w:p>')


def code_block(text):
    out = []
    for line in text.split('\n'):
        out.append(f'<w:p><w:pPr><w:pStyle w:val="Code"/></w:pPr>{run(line, mono=True)}</w:p>')
    return ''.join(out)


def quote_block(text):
    return f'<w:p><w:pPr><w:pStyle w:val="Quote"/></w:pPr>{run(text, italic=True)}</w:p>'


def callout(label, text):
    """Caja resaltada para notas de speaker / advertencias."""
    return (
        '<w:p><w:pPr>'
        '<w:pStyle w:val="Callout"/>'
        '<w:shd w:val="clear" w:color="auto" w:fill="FFF4CE"/>'
        '<w:pBdr>'
        '<w:left w:val="single" w:sz="24" w:color="F2A900"/>'
        '<w:top w:val="single" w:sz="4" w:color="F2A900"/>'
        '<w:right w:val="single" w:sz="4" w:color="F2A900"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="F2A900"/>'
        '</w:pBdr>'
        '<w:ind w:left="200" w:right="200"/>'
        '</w:pPr>'
        + run(f'{label} ', bold=True, color='8B5A00')
        + run(text)
        + '</w:p>'
    )


def table(headers, rows, col_widths=None):
    n = len(headers)
    if not col_widths:
        col_widths = [int(9000 / n)] * n
    grid = '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{w}"/>' for w in col_widths) + '</w:tblGrid>'

    def cell(content, *, header=False, w=2000):
        shading = '<w:shd w:val="clear" w:color="auto" w:fill="2E74B5"/>' if header else ''
        runs_xml = run(content, bold=header, color="FFFFFF" if header else None)
        return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{shading}</w:tcPr>'
                f'<w:p>{runs_xml}</w:p></w:tc>')

    head = '<w:tr>' + ''.join(cell(h, header=True, w=col_widths[i]) for i, h in enumerate(headers)) + '</w:tr>'
    body = []
    for r in rows:
        body.append('<w:tr>' + ''.join(cell(str(c), w=col_widths[i]) for i, c in enumerate(r)) + '</w:tr>')

    tbl_pr = (
        '<w:tblPr><w:tblW w:w="9000" w:type="dxa"/>'
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:left w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:bottom w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:right w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:insideH w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '<w:insideV w:val="single" w:sz="4" w:color="BFBFBF"/>'
        '</w:tblBorders></w:tblPr>'
    )
    return f'<w:tbl>{tbl_pr}{grid}{head}{"".join(body)}</w:tbl>' + p('')


def page_break():
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


# ---------------------------------------------------------------------------
# Estilos / numbering / content types (igual que en el otro doc, con extras)
# ---------------------------------------------------------------------------

STYLES_XML = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="22"/><w:lang w:val="es-PE"/></w:rPr></w:rPrDefault>
    <w:pPrDefault><w:pPr><w:spacing w:before="60" w:after="120" w:line="300" w:lineRule="auto"/></w:pPr></w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:spacing w:before="360" w:after="240"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="56"/><w:color w:val="1F4E79"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="360" w:after="180"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="36"/><w:color w:val="1F4E79"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="280" w:after="140"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="28"/><w:color w:val="2E74B5"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:next w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:before="200" w:after="100"/><w:outlineLvl w:val="2"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:sz w:val="24"/><w:color w:val="2E74B5"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:pPr><w:spacing w:before="40" w:after="40"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Code"/><w:pPr><w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/><w:spacing w:before="0" w:after="0" w:line="260" w:lineRule="auto"/><w:ind w:left="200"/></w:pPr><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="20"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:pPr><w:ind w:left="600" w:right="600"/><w:spacing w:before="120" w:after="120"/></w:pPr><w:rPr><w:i/><w:color w:val="555555"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Callout"><w:name w:val="Callout"/><w:pPr><w:spacing w:before="120" w:after="120"/></w:pPr></w:style>
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
# CONTENIDO
# ---------------------------------------------------------------------------

blocks = []
B = blocks.append

# ============================ PORTADA ============================
B(p(''))
B(p(''))
B(p(''))
B(title('¿Qué es y por qué existe JPA?'))
B(subtitle('Informe del Integrante 1 — Bloque introductorio (10 min)'))
B(p(''))
B(p(''))
B(para(run('Curso: ', bold=True), run('Ingeniería Web — Spring Boot')))
B(para(run('Bloque: ', bold=True), run('Conceptos. ORM, JPA, Hibernate, Spring Data JPA')))
B(para(run('Tipo: ', bold=True), run('100% teoría, sin código en pantalla')))
B(para(run('Duración: ', bold=True), run('~10 minutos')))
B(p(''))

B(p('Para qué sirve este documento', bold=True))
B(p(
    'Este informe centraliza TODO lo que el integrante 1 necesita para exponer su bloque '
    'de 10 minutos: el contenido teórico organizado, las analogías con NestJS que la '
    'audiencia ya conoce, citas oficiales para sustentar lo que se afirma, un guion '
    'sugerido por sección con tiempos, y un anexo de Q&A para anticipar preguntas. '
    'No reemplaza al guion personal del expositor: lo alimenta.'
))

B(p('Reglas que conviene respetar para no pisar a los siguientes bloques', bold=True))
B(bullet('No mostrar código en pantalla. Si aparece código aquí, es solo para que el expositor entienda — no para proyectar.'))
B(bullet('No explicar configuración (eso lo hace el integrante 2).'))
B(bullet('No mostrar entidades concretas ni anotaciones (eso lo hace el integrante 3).'))
B(bullet('No hablar de repositorios concretos ni hacer demos (eso lo hace el integrante 4).'))
B(bullet('Tu trabajo: dejar claro QUÉ es JPA, DÓNDE se ubica y POR QUÉ existe.'))

B(page_break())

# ============================ MAPA DEL BLOQUE ============================
B(heading('Mapa del bloque (10 minutos)', 1))

B(p(
    'El bloque está dividido en cinco momentos. Cada momento tiene un objetivo y un '
    'tiempo asignado. Conviene cronometrar al menos dos ensayos para no extenderse: '
    'si te pasás del minuto 10, el integrante 4 termina sin tiempo para la demo (que '
    'es la cereza del postre y NO puede acortarse).'
))

B(table(
    ['#', 'Momento', 'Tiempo', 'Objetivo'],
    [
        ['1', 'El problema: impedance mismatch', '~2:00', 'Que la audiencia sienta el problema antes de ver la solución'],
        ['2', '¿Qué es un ORM?', '~2:00', 'Definir ORM y mostrar el "antes" sin ORM (JDBC)'],
        ['3', 'La torre de abstracción', '~2:00', 'Ubicar a JPA en la pila de capas'],
        ['4', 'JPA vs Hibernate vs Spring Data', '~2:00', 'Disolver la confusión típica entre los tres nombres'],
        ['5', 'Trade-offs y cierre', '~2:00', 'Honestidad técnica + handoff al integrante 2'],
    ],
    col_widths=[600, 3300, 1300, 3800],
))

B(callout('Recomendación de speaker:',
    'no leas las diapositivas. Las diapositivas son anclas visuales (un diagrama, '
    'tres bullets máximo). Vos contás la historia con tus palabras. Si te perdés, '
    'volvés al diagrama de la torre de abstracción — esa imagen organiza todo el bloque.'))

B(page_break())

# ============================ 1. IMPEDANCE MISMATCH ============================
B(heading('1. El problema: object-relational impedance mismatch', 1))
B(para(run('Tiempo objetivo: ', bold=True), run('2 minutos.')))

B(heading('1.1 ¿Qué significa "impedance mismatch"?', 2))
B(p(
    'Es un término que viene de la ingeniería eléctrica. Cuando dos circuitos tienen '
    'impedancias distintas y los conectás directamente, la transferencia de energía '
    'es ineficiente: una parte se refleja, una parte se pierde. Hace falta un '
    '"adaptador" en el medio.'
))
B(p(
    'En software, llamamos "object-relational impedance mismatch" al desencuentro '
    'entre dos modelos que parecen simples pero NO encajan naturalmente: el modelo '
    'orientado a objetos del lenguaje (Java, en nuestro caso) y el modelo relacional '
    'de las bases de datos (Postgres, MySQL, Oracle).'
))

B(heading('1.2 Los desencuentros, en concreto', 2))
B(p('Los dos modelos divergen en al menos cinco aspectos:'))
B(table(
    ['Aspecto', 'Modelo orientado a objetos (Java)', 'Modelo relacional (SQL)'],
    [
        ['Granularidad',
         'Clases con campos compuestos, listas anidadas, sub-objetos.',
         'Filas planas con tipos primitivos.'],
        ['Identidad',
         'Identidad por referencia (==) y por valor (equals()).',
         'Identidad por clave primaria.'],
        ['Herencia',
         'Existe (extends, abstract, polymorphism).',
         'No existe. Hay que simularla con tablas.'],
        ['Asociaciones',
         'Referencias directas (un objeto contiene otro).',
         'Claves foráneas (FK) con dirección unidireccional.'],
        ['Navegabilidad',
         'cliente.getPedidos().get(0).getProducto()',
         'JOINs explícitos en cada query.'],
    ],
    col_widths=[1800, 3600, 3600],
))

B(heading('1.3 Ejemplo concreto: Cliente con sus pedidos', 2))
B(p(
    'Tomá esta clase, mentalmente. No la vas a mostrar en pantalla; vas a describirla. '
    'Esto es Java tal cual escribiríamos:'
))
B(code_block(
    "class Cliente {\n"
    "    Long id;\n"
    "    String nombre;\n"
    "    List<Pedido> pedidos;   // <-- referencia directa a otra clase\n"
    "}\n"
    "\n"
    "class Pedido {\n"
    "    Long id;\n"
    "    BigDecimal total;\n"
    "}"
))
B(p(
    'En Java es natural decir "el cliente tiene una lista de pedidos". El programador '
    'piensa en grafos de objetos.'
))

B(p('En la base de datos relacional, lo MISMO se ve así:'))
B(code_block(
    "TABLE clientes (\n"
    "    id          BIGSERIAL PRIMARY KEY,\n"
    "    nombre      VARCHAR(100)\n"
    ")\n"
    "\n"
    "TABLE pedidos (\n"
    "    id          BIGSERIAL PRIMARY KEY,\n"
    "    cliente_id  BIGINT REFERENCES clientes(id),  -- FK\n"
    "    total       NUMERIC(19,2)\n"
    ")"
))
B(p(
    'No hay "lista" en la tabla cliente. La relación se invierte: la tabla pedidos '
    'tiene una clave foránea cliente_id que apunta hacia atrás. Para reconstruir '
    '"los pedidos de Juan", la base hace un JOIN.'
))

B(callout('Idea fuerza:',
    'el programador piensa en GRAFOS de objetos. La base de datos almacena RELACIONES '
    'normalizadas con claves foráneas. Alguien tiene que traducir entre esos dos '
    'mundos. Sin un traductor, ese trabajo lo hacés vos a mano, todo el día, en cada '
    'consulta. Y ahí entra el ORM.'))

B(heading('1.4 Cómo lo presento (guion sugerido, ~2 min)', 2))
B(quote_block(
    '"Antes de hablar de JPA quiero que entendamos el problema. En Java, cuando '
    'modelamos un cliente, decimos: un cliente TIENE una lista de pedidos. Es una '
    'referencia directa. En la base de datos relacional eso no existe. La base no '
    'sabe de listas: tiene una tabla clientes y una tabla pedidos, conectadas por '
    'una clave foránea. Dos modelos distintos, dos mentalidades distintas. A esto se '
    'le llama impedance mismatch — un término prestado de la ingeniería eléctrica que '
    'describe exactamente lo mismo: dos sistemas que no encajan naturalmente y '
    'necesitan un adaptador en el medio. Ese adaptador es el ORM."'
))

B(page_break())

# ============================ 2. ORM ============================
B(heading('2. ¿Qué es un ORM?', 1))
B(para(run('Tiempo objetivo: ', bold=True), run('2 minutos.')))

B(heading('2.1 Definición', 2))
B(p(
    'ORM significa Object-Relational Mapper: mapeador objeto-relacional. Es la pieza '
    'de software que se ubica entre el código orientado a objetos y la base de datos '
    'relacional. Su trabajo es traducir, en ambas direcciones, entre clases y tablas.'
))
B(bullet('De Java a SQL: cuando guardás un objeto, el ORM genera el INSERT.'))
B(bullet('De SQL a Java: cuando hacés una consulta, el ORM convierte cada fila del ResultSet en un objeto.'))

B(heading('2.2 Sin ORM: el sufrimiento del JDBC puro', 2))
B(p(
    'JDBC es la API de bajo nivel de Java para hablar con bases de datos. Existe '
    'desde 1997 y todo ORM termina apoyándose en JDBC por debajo. El problema es que, '
    'usado directamente, te obliga a escribir todo a mano. Mirá esto: traer una '
    'cuenta por id usando JDBC puro:'
))
B(code_block(
    "Connection conn = DriverManager.getConnection(url, user, pass);\n"
    "PreparedStatement ps = conn.prepareStatement(\n"
    "    \"SELECT id, titular, saldo FROM cuentas WHERE id = ?\"\n"
    ");\n"
    "ps.setLong(1, cuentaId);\n"
    "ResultSet rs = ps.executeQuery();\n"
    "\n"
    "Cuenta cuenta = null;\n"
    "if (rs.next()) {\n"
    "    cuenta = new Cuenta();\n"
    "    cuenta.setId(rs.getLong(\"id\"));\n"
    "    cuenta.setTitular(rs.getString(\"titular\"));\n"
    "    cuenta.setSaldo(rs.getBigDecimal(\"saldo\"));\n"
    "}\n"
    "\n"
    "rs.close();\n"
    "ps.close();\n"
    "conn.close();   // y todavía hay que envolver todo en try-catch-finally"
))
B(p(
    'Eso es para UNA consulta. Multiplicá ese trabajo por cada tabla, cada filtro, '
    'cada relación. El SQL aparece como String dentro del código (sin chequeo del '
    'compilador), las conexiones se filtran si te olvidás de cerrarlas, y el mapeo '
    'columna-a-campo es boilerplate puro.'
))

B(heading('2.3 Con ORM: la misma consulta, una línea', 2))
B(p('Lo mismo, con un ORM (lo que más adelante usaremos en el proyecto):'))
B(code_block("Cuenta cuenta = repo.findById(cuentaId).orElseThrow();"))

B(p(
    'Eso es todo. Una línea, tipada, sin SQL escrito a mano, sin gestión manual de '
    'conexiones. El ORM hace, por debajo, exactamente lo de la diapositiva anterior — '
    'pero vos no tenés que escribirlo.'
))

B(heading('2.4 Equivalencia con NestJS (la referencia que ya conocemos)', 2))
B(p(
    'En el ecosistema Node, los ORM más populares son TypeORM y Prisma. Cumplen '
    'exactamente el mismo rol: traducen entre clases TypeScript y tablas SQL. La '
    'diferencia está en la API y en la madurez del ecosistema:'
))
B(table(
    ['Plataforma', 'ORM más usados', 'Especificación estandarizada'],
    [
        ['Node.js (Nest)', 'TypeORM, Prisma, MikroORM', 'No existe estándar único'],
        ['Java', 'Hibernate, EclipseLink, OpenJPA', 'Sí: JPA / Jakarta Persistence'],
    ],
    col_widths=[2500, 3500, 3000],
))
B(p(
    'Esa es una diferencia importante y se la vamos a explicar después: en Java '
    'existe una especificación común (JPA) que todos los ORM importantes implementan. '
    'En Node, cada librería tiene su propia API y migrar de una a otra es reescribir.'
))

B(heading('2.5 Cómo lo presento (guion sugerido, ~2 min)', 2))
B(quote_block(
    '"Un ORM es Object-Relational Mapper. Es el traductor. Tomá un objeto de Java, '
    'lo convierte en filas SQL. Tomá filas SQL, te las devuelve como objetos. Para '
    'que vean por qué lo necesitamos, imagínense escribir esto a mano cada vez que '
    'consultan algo: abrir una conexión, preparar un statement, setear cada parámetro, '
    'ejecutar, recorrer el ResultSet, copiar columna por columna a un objeto Java, '
    'cerrar todo. Eso es JDBC puro. Lo que hace un ORM es ocultar ese trabajo. Donde '
    'antes había treinta líneas, queda una. Para los que vinimos de Nest, los '
    'equivalentes que ya conocen son TypeORM y Prisma. La idea es exactamente la '
    'misma. Lo que cambia, y ya vamos a ver eso, es que en Java hay una especificación '
    'estándar — JPA — que ordena el ecosistema."'
))

B(page_break())

# ============================ 3. TORRE DE ABSTRACCION ============================
B(heading('3. La torre de abstracción', 1))
B(para(run('Tiempo objetivo: ', bold=True), run('2 minutos.')))

B(callout('Esta es LA diapositiva clave del bloque.',
    'La torre de abstracción es la imagen mental que tiene que quedarles a los oyentes. '
    'Si después de tu bloque pueden dibujar esta torre y nombrar las capas, ganaste.'))

B(heading('3.1 El diagrama', 2))
B(p('La torre completa, de arriba (lo que vos escribís) hacia abajo (la base de datos):'))
B(code_block(
    "+---------------------------------+\n"
    "|   Spring Data JPA               |  <-- Repositorios automaticos\n"
    "+---------------------------------+\n"
    "|   JPA (especificacion)          |  <-- Interfaces estandar (jakarta.persistence)\n"
    "+---------------------------------+\n"
    "|   Hibernate                     |  <-- Implementacion concreta de JPA\n"
    "+---------------------------------+\n"
    "|   JDBC                          |  <-- API de bajo nivel para hablar con la BD\n"
    "+---------------------------------+\n"
    "|   Driver (PostgreSQL, MySQL...)|  <-- Conector especifico de cada motor\n"
    "+---------------------------------+\n"
    "|   Base de Datos                 |\n"
    "+---------------------------------+"
))

B(heading('3.2 Recorrido de cada capa, de arriba hacia abajo', 2))

B(p('Spring Data JPA', bold=True))
B(bullet('La capa que toca el desarrollador la mayoría del tiempo.'))
B(bullet('Genera repositorios automáticamente: vos definís una interface y Spring crea la implementación en runtime.'))
B(bullet('Es OPCIONAL. Podrías usar JPA directamente sin Spring Data; te ahorraría algunas líneas pero perdés mucha productividad.'))

B(p('JPA (Jakarta Persistence)', bold=True))
B(bullet('Especificación. Define las anotaciones (@Entity, @Id, @OneToMany…) y las interfaces (EntityManager, Query…).'))
B(bullet('No tiene código ejecutable propio. Es un contrato: dice "todo ORM que cumpla conmigo debe comportarse así".'))
B(bullet('Antes se llamaba Java Persistence API. Cuando Java EE pasó a la Eclipse Foundation se renombró a Jakarta Persistence. El namespace pasó de javax.persistence a jakarta.persistence.'))

B(p('Hibernate', bold=True))
B(bullet('Implementación concreta de la especificación JPA. Es la que efectivamente traduce objetos a SQL y SQL a objetos.'))
B(bullet('Es el ORM más usado del ecosistema Java. Spring Boot lo trae por defecto cuando agregás el starter de JPA.'))
B(bullet('Existen otras implementaciones — EclipseLink, OpenJPA — pero el 95% de los proyectos Spring usan Hibernate.'))

B(p('JDBC', bold=True))
B(bullet('Java Database Connectivity. La API de bajo nivel, parte del JDK desde 1997.'))
B(bullet('Es la frontera entre Java y "todo lo que sea base de datos". Hibernate, por debajo, termina llamando a JDBC para enviar el SQL.'))

B(p('Driver de PostgreSQL', bold=True))
B(bullet('La librería específica que sabe hablar el protocolo de PostgreSQL.'))
B(bullet('Si mañana cambiamos a MySQL, intercambiamos el driver. JDBC le ofrece una interfaz uniforme a Hibernate; abajo el driver se encarga de los detalles del motor.'))

B(p('Base de Datos', bold=True))
B(bullet('PostgreSQL, MySQL, Oracle, SQL Server. La capa final donde viven los datos.'))

B(heading('3.3 La idea fuerza del diagrama', 2))
B(callout('Cada capa habla solo con la capa de abajo.',
    'Spring Data JPA usa JPA. JPA delega en Hibernate. Hibernate usa JDBC. JDBC usa el driver. El driver usa la base. Vos, como desarrollador, escribís en la capa más alta. Las capas de abajo trabajan, pero no las tocás. Esto es separación de responsabilidades.'))

B(p(
    'La gracia de la torre es que cada capa abstrae a la siguiente. Si querés cambiar '
    'de base de datos, cambiás el driver y, en algunos casos, el dialecto de Hibernate. '
    'El resto del código no se entera. Esa portabilidad es uno de los valores '
    'centrales de JPA.'
))

B(heading('3.4 Cómo lo presento (guion sugerido, ~2 min)', 2))
B(quote_block(
    '"Esta es la diapositiva más importante del bloque. Quiero que la dibujen mentalmente '
    'y se la lleven. Arriba de la torre, ustedes — el código que escriben. Abajo, la '
    'base de datos. En el medio hay cinco capas. La de más arriba, Spring Data JPA, '
    'es la que tocan el 95% del tiempo. Genera repositorios automáticamente. Debajo '
    'está JPA, que NO ejecuta nada: es solo una especificación, un contrato. Debajo '
    'de JPA está Hibernate, que es la implementación concreta de ese contrato y la '
    'que efectivamente traduce objetos a SQL. Después JDBC — la API estándar de Java '
    'para bases de datos. Después el driver de PostgreSQL, específico del motor. Y al '
    'final, la base. Cada capa habla solo con la siguiente. Esa separación es la que '
    'permite que, si mañana cambian de Postgres a MySQL, cambien solo el driver y no '
    'reescriban toda la app."'
))

B(page_break())

# ============================ 4. DISTINCION CRITICA ============================
B(heading('4. La distinción crítica: JPA vs Hibernate vs Spring Data JPA', 1))
B(para(run('Tiempo objetivo: ', bold=True), run('2 minutos.')))

B(callout('Confusión típica:',
    '"JPA" e "Hibernate" se usan como sinónimos, y agregás "Spring Data JPA" en la mezcla y la cabeza explota. Tu trabajo es disolver esa confusión en dos minutos.'))

B(heading('4.1 La analogía que más rinde: interface vs clase', 2))
B(p(
    'Para que les quede claro de una, usá la analogía con interfaces de Java. Es '
    'algo que ya vieron y entienden:'
))
B(table(
    ['Java básico', 'Mundo de la persistencia'],
    [
        ['interface List', 'JPA (especificación)'],
        ['class ArrayList implements List', 'Hibernate (implementación de JPA)'],
        ['Una librería que extiende ArrayList', 'Spring Data JPA (sobre JPA)'],
    ],
    col_widths=[3800, 5200],
))
B(p(
    'Una interfaz Java define qué métodos existen, pero no los implementa. ArrayList '
    'es una clase que implementa esa interfaz. JPA es la "interfaz" del mundo de la '
    'persistencia: define las anotaciones y los contratos. Hibernate es la '
    '"implementación". Spring Data JPA es una capa adicional construida encima de JPA '
    'que automatiza patrones repetitivos.'
))

B(heading('4.2 Resumen en una tabla', 2))
B(table(
    ['Pieza', 'Qué es', '¿Ejecuta código?', 'Quién la provee'],
    [
        ['JPA', 'Especificación (interfaces, anotaciones)', 'No', 'Eclipse Foundation (antes Oracle)'],
        ['Hibernate', 'Implementación concreta de JPA', 'Sí — el ORM real', 'Red Hat'],
        ['Spring Data JPA', 'Capa de abstracción sobre JPA', 'Sí — genera proxies', 'VMware/Spring team'],
    ],
    col_widths=[2200, 3400, 1900, 2500],
))

B(heading('4.3 ¿Se pueden cambiar entre sí?', 2))
B(bullet_runs(
    run('JPA: ', bold=True),
    run(
        'no se "cambia". Es la especificación. Si tu proyecto usa JPA, ya está atado '
        'a JPA. La pregunta es qué implementación elegís.'
    ),
))
B(bullet_runs(
    run('Hibernate: ', bold=True),
    run(
        'es reemplazable por otra implementación de JPA (EclipseLink, OpenJPA), pero '
        'en la práctica casi nadie lo cambia. Spring Boot lo trae de fábrica.'
    ),
))
B(bullet_runs(
    run('Spring Data JPA: ', bold=True),
    run(
        'es opcional. Podrías programar contra el EntityManager de JPA directamente. '
        'Lo elegimos porque elimina mucho boilerplate.'
    ),
))

B(heading('4.4 Comparación con NestJS (clave didáctica)', 2))
B(p(
    'Esta es una de las grandes diferencias entre los dos ecosistemas y vale la pena '
    'mencionarla porque la audiencia ya conoce Nest:'
))
B(bullet(
    'En Java existe UNA especificación común (JPA). Cualquier ORM que la implemente '
    'expone las mismas anotaciones (@Entity, @Id, @OneToMany) y la misma API '
    '(EntityManager). Migrar de Hibernate a EclipseLink es, en general, indoloro.'
))
B(bullet(
    'En Node no existe equivalente. TypeORM, Prisma y MikroORM tienen APIs distintas. '
    'Migrar entre ellos es reescribir todas las entidades y todas las queries. Cada '
    'librería inventó su propio dialecto.'
))
B(p(
    'Esa estandarización es uno de los valores que aporta el ecosistema Java en este '
    'tema. No es algo trivial: significa que el conocimiento que adquieren con '
    'Hibernate les sirve aunque el equipo migre a EclipseLink en cinco años.'
))

B(heading('4.5 Cómo lo presento (guion sugerido, ~2 min)', 2))
B(quote_block(
    '"Voy a disolver una confusión típica. La gente dice JPA, Hibernate y Spring Data '
    'JPA como si fueran lo mismo. No lo son. Acuérdense de Java básico: hay '
    'interfaces y hay clases. List es una interfaz; ArrayList es la clase que la '
    'implementa. JPA es exactamente eso: una INTERFAZ del mundo de la persistencia. '
    'Define las anotaciones, define los contratos, pero no ejecuta nada. Hibernate '
    'es la CLASE — la implementación concreta que hace el trabajo. Spring Data JPA '
    'es una librería adicional que se construye encima y automatiza los patrones más '
    'comunes, como generarte un repositorio sin escribirlo. Punto importante: en '
    'Java tenemos esta especificación común, JPA. En Node, ustedes que vienen de '
    'Nest, no la tienen. TypeORM, Prisma y MikroORM cada uno tienen su propia API. '
    'Tener un estándar es valioso: el conocimiento que adquieren con Hibernate les '
    'sirve aunque cambien de implementación."'
))

B(page_break())

# ============================ 5. TRADE-OFFS Y CIERRE ============================
B(heading('5. Trade-offs: ventajas y costos del ORM', 1))
B(para(run('Tiempo objetivo: ', bold=True), run('2 minutos (incluyendo handoff).')))

B(callout('Honestidad técnica:',
    'NO presentes el ORM como bala de plata. Mostrar que conocés sus límites te da credibilidad y te diferencia del que solo memorizó la diapositiva oficial.'))

B(heading('5.1 A favor', 2))
B(bullet_runs(
    run('Productividad: ', bold=True),
    run('escribís un 70-80% menos de código de acceso a datos. Lo que con JDBC son 30 líneas, con un ORM es una.'),
))
B(bullet_runs(
    run('Portabilidad: ', bold=True),
    run('JPA está estandarizado. Cambiar de motor de BD afecta solo al driver y al dialecto. El código de negocio no se entera.'),
))
B(bullet_runs(
    run('Menos bugs de SQL: ', bold=True),
    run('el SQL escrito a mano como String dentro de Java no tiene chequeo del compilador. Un typo en un nombre de columna explota en runtime. JPA trabaja con tipos Java; muchos errores se detectan en compilación.'),
))
B(bullet_runs(
    run('Gestión automática de transacciones, conexiones y caché: ', bold=True),
    run('el ORM administra el ciclo de vida de los recursos. Te olvidás de cerrar conexiones a mano.'),
))

B(heading('5.2 En contra', 2))
B(bullet_runs(
    run('Capa de magia: ', bold=True),
    run('el ORM oculta lo que pasa. Dos líneas de Java pueden disparar diez queries. Si no entendés la herramienta, esas queries se acumulan sin que te enteres.'),
))
B(bullet_runs(
    run('Problema N+1: ', bold=True),
    run(
        'el clásico. Cargás una lista de N entidades y, al iterar para acceder a una '
        'relación, el ORM dispara N queries adicionales. Resultado: 1 + N queries para '
        'algo que debería ser 1 con un JOIN. Tiene solución (fetch joins, EntityGraph), '
        'pero hay que conocer el problema para resolverlo.'
    ),
))
B(bullet_runs(
    run('Curva de aprendizaje: ', bold=True),
    run('JPA tiene matices: estados de la entidad, lazy vs eager, propagación de transacciones, ciclo de vida del persistence context. No se aprende en una tarde.'),
))
B(bullet_runs(
    run('Casos donde no rinde: ', bold=True),
    run('reportes complejos, agregaciones masivas, ETLs… ahí muchas veces conviene SQL nativo (que JPA igualmente soporta) o herramientas como JDBC Template / jOOQ.'),
))

B(heading('5.3 La conclusión honesta', 2))
B(p(
    'El ORM es una abstracción: simplifica el caso común a costa de complicar los '
    'casos extremos. Para un CRUD de negocio típico (que es el 90% del trabajo) la '
    'productividad gana por goleada. Para reportería pesada o queries muy '
    'optimizadas, el ORM puede ser un cuello de botella y conviene "bajar de capa" y '
    'usar SQL más cercano al motor.'
))
B(p(
    'Saber cuándo subir de abstracción y cuándo bajar es lo que distingue a un dev '
    'que sabe usar ORM de uno que solo lo aplica.'
))

B(heading('5.4 Cómo lo presento (guion sugerido, ~1:30)', 2))
B(quote_block(
    '"Antes de cerrar, una nota de honestidad técnica. El ORM no es bala de plata. '
    'A favor tiene cosas grandes: 70 u 80% menos código, portabilidad entre motores, '
    'menos bugs de SQL, gestión automática de conexiones y transacciones. En contra: '
    'es una capa de magia que oculta lo que pasa. Si no la conocés, tu app puede '
    'estar disparando cien queries para algo que debería ser una. El problema clásico '
    'que nombrarles —y que van a oír mucho cuando trabajen con JPA— es el N+1: cargás '
    'una lista de clientes y, al iterar para ver sus pedidos, dispara una query por '
    'cada cliente. Tiene solución, pero hay que conocerlo. La regla práctica es: para '
    'un CRUD típico el ORM es un golazo; para reportería compleja, a veces conviene '
    'bajar de capa y escribir SQL."'
))

B(heading('5.5 Frase de cierre y handoff', 2))
B(p(
    'Cuando el cronómetro marque ~9:30, cerrás con una frase como esta. La idea es '
    'recapitular en cinco palabras y abrirle la pista al integrante 2:'
))
B(quote_block(
    '"Resumiendo: tenemos dos mundos que no encajan, un traductor que se llama ORM, '
    'una torre de capas en la que JPA es la especificación, Hibernate la implementación '
    'y Spring Data el azúcar. Ahora que sabemos QUÉ es JPA y dónde se ubica, le paso '
    'la palabra a [nombre] para ver CÓMO configuramos todo esto en un proyecto Spring '
    'Boot real."'
))

B(callout('Manejo del tiempo final:',
    'si te queda tiempo, NO improvises contenido nuevo. Repetí la torre de abstracción una segunda vez (es la imagen que más rinde), o anticipá una pregunta del Q&A. Si te quedaste corto, es preferible: el bloque siguiente lo agradece.'))

B(page_break())

# ============================ APENDICE A: Q&A ============================
B(heading('Apéndice A — Preguntas que pueden hacerte (Q&A prep)', 1))

B(p(
    'Anticipar es media respuesta. Estas son las preguntas más probables. Tenelas '
    'leídas; no hace falta memorizarlas. Si te preguntan algo que no sabés, decí "no '
    'lo sé con certeza, lo investigo y te confirmo" — esa frase suma puntos siempre.'
))

B(heading('P1. Si JPA es solo una especificación, ¿de dónde vienen las anotaciones que escribimos?', 2))
B(p(
    'Las anotaciones (@Entity, @Id, @OneToMany, etc.) ESTÁN definidas en JPA, en el '
    'paquete jakarta.persistence. Lo que no está en JPA es el código que las procesa: '
    'eso lo hace Hibernate (o cualquier otra implementación). Es decir, JPA dice '
    '"@Entity significa esto"; Hibernate lee la anotación y actúa en consecuencia.'
))

B(heading('P2. ¿Por qué Spring Boot trae Hibernate y no otra cosa?', 2))
B(p(
    'Decisión histórica y de mercado. Hibernate es de lejos la implementación más '
    'usada y la mejor mantenida. Si necesitás otra, podés excluirla del starter y '
    'agregar EclipseLink, pero el 99% de los proyectos no lo hace. La documentación '
    'oficial de Spring Boot lo lista como "una de las implementaciones JPA más '
    'populares" y la incluye por defecto en spring-boot-starter-data-jpa.'
))

B(heading('P3. ¿Spring Data JPA reemplaza a JPA?', 2))
B(p(
    'No. Spring Data JPA se construye SOBRE JPA. Cuando usás Spring Data, por debajo '
    'sigue corriendo JPA (vía Hibernate). Lo que hace Spring Data es ahorrarte código: '
    'declarás una interface y te genera la implementación. Pero las anotaciones '
    'sobre las entidades (@Entity, @Id, etc.) siguen siendo de JPA.'
))

B(heading('P4. ¿Puedo escribir SQL nativo si JPA no me alcanza?', 2))
B(p(
    'Sí, y es totalmente válido. JPA soporta queries nativas vía @Query con '
    'nativeQuery = true. Lo recomendable es: usar JPQL/derived queries para el caso '
    'común, y bajar a SQL nativo solo cuando hace falta funcionalidad específica del '
    'motor (window functions, CTEs, JSON en Postgres, etc.). El integrante 4 muestra '
    'algunos ejemplos en la demo.'
))

B(heading('P5. ¿Qué es el problema N+1 exactamente?', 2))
B(p(
    'Es el caso más conocido de queries ineficientes con ORM. Imaginá que pedís 100 '
    'clientes con findAll(). Eso son 1 query (SELECT FROM clientes). Después iterás '
    'la lista y, por cada cliente, accedés a su lista de pedidos. Como las relaciones '
    'están configuradas en LAZY, cada acceso dispara otra query (SELECT FROM pedidos '
    'WHERE cliente_id = ?). Resultado: 1 + 100 = 101 queries para algo que debería '
    'ser una sola con JOIN. Se resuelve con fetch joins, @EntityGraph o configurando '
    'EAGER cuando se justifica. Pero la solución requiere CONOCER el problema.'
))

B(heading('P6. ¿JPA y Jakarta Persistence son lo mismo?', 2))
B(p(
    'Sí, son dos nombres del mismo estándar. Era "JPA" (Java Persistence API) cuando '
    'pertenecía a Java EE bajo Oracle. En 2017 se transfirió a la Eclipse Foundation '
    'y se renombró a Jakarta Persistence. El namespace pasó de javax.persistence a '
    'jakarta.persistence. La gente sigue diciendo "JPA" por costumbre — y es correcto.'
))

B(heading('P7. ¿Qué pasa si la base de datos no es relacional? ¿JPA sirve para Mongo?', 2))
B(p(
    'JPA está diseñada para bases relacionales. Para MongoDB existe Spring Data '
    'MongoDB, que tiene una API similar (con repositorios) pero no es JPA. La pieza '
    '"Spring Data" es un paraguas: tiene un módulo por cada tipo de almacén — JPA, '
    'MongoDB, Redis, Cassandra, etc. — y todos comparten el patrón de repositorios.'
))

B(heading('P8. ¿Por qué algunos enseñan a usar Lombok con @Data en entidades y otros lo desaconsejan?', 2))
B(p(
    'Es uno de los puntos polémicos del ecosistema. @Data genera equals/hashCode '
    'usando todos los campos, lo que rompe el contrato cuando el ID lo asigna la BD '
    '(el hash cambia entre antes y después de persistir). También genera toString '
    'que recorre todas las relaciones, lo que dispara LazyInitializationException o '
    'recursión infinita en relaciones bidireccionales. La recomendación responsable '
    '(que sostiene Vlad Mihalcea, Hibernate Developer Advocate) es: en entidades JPA '
    'usar @Getter y @Setter, NO @Data. Pero eso, técnicamente, lo verán con más '
    'detalle más adelante en el curso.'
))

B(page_break())

# ============================ APENDICE B: GLOSARIO ============================
B(heading('Apéndice B — Glosario rápido', 1))

B(p('Diccionario corto de términos que vas a usar o que te pueden preguntar.'))

B(table(
    ['Término', 'Definición rápida'],
    [
        ['ORM', 'Object-Relational Mapper. Pieza de software que traduce entre objetos de un lenguaje y filas de una base relacional.'],
        ['JDBC', 'Java Database Connectivity. API de bajo nivel del JDK para hablar con bases de datos. Existe desde 1997.'],
        ['JPA', 'Jakarta Persistence (antes Java Persistence API). Especificación estándar de Java para ORM. Define anotaciones e interfaces, no ejecuta nada.'],
        ['Hibernate', 'Implementación de JPA más usada del mercado. Es el ORM real que ejecuta las traducciones. Default en Spring Boot.'],
        ['Spring Data JPA', 'Capa de abstracción sobre JPA construida por el equipo de Spring. Genera repositorios automáticamente a partir de interfaces.'],
        ['Entidad', 'Clase Java anotada con @Entity que se mapea a una tabla. Cada instancia representa una fila.'],
        ['Repositorio', 'Interfaz que expone operaciones de persistencia para una entidad (save, findAll, findById, etc.).'],
        ['Persistence Context', 'Espacio en memoria donde Hibernate gestiona las entidades activas en una transacción.'],
        ['Impedance mismatch', 'El desencuentro estructural entre el modelo orientado a objetos y el modelo relacional.'],
        ['Problema N+1', 'Patrón ineficiente donde una operación dispara 1 + N queries debido a relaciones LAZY mal manejadas.'],
        ['Driver JDBC', 'Librería específica de un motor (PostgreSQL, MySQL...) que sabe hablar el protocolo de ese motor.'],
        ['Dialecto', 'Configuración que le dice a Hibernate qué variante de SQL generar (PostgreSQLDialect, MySQLDialect, etc.).'],
    ],
    col_widths=[2400, 6600],
))

B(page_break())

# ============================ APENDICE C: CHECKLIST DE ENSAYO ============================
B(heading('Apéndice C — Checklist de ensayo', 1))

B(p('Antes de la exposición, repasá esto. Marcá lo que ya tenés listo:'))

B(p('Contenido', bold=True))
B(bullet('Sé describir, en una frase, el impedance mismatch.'))
B(bullet('Sé dibujar la torre de abstracción de memoria, en orden.'))
B(bullet('Puedo explicar la diferencia entre JPA, Hibernate y Spring Data sin leer.'))
B(bullet('Tengo lista la analogía interface vs clase para la pregunta más común.'))
B(bullet('Conozco al menos dos ventajas y dos costos del ORM.'))
B(bullet('Tengo memorizada la frase de cierre con el nombre del integrante 2.'))

B(p('Cronometraje', bold=True))
B(bullet('Hice al menos un ensayo completo cronometrado.'))
B(bullet('No me paso del minuto 10:30 (margen de 30 segundos).'))
B(bullet('Si me quedo corto, sé qué reforzar (la torre de abstracción es la red de seguridad).'))

B(p('Diapositivas', bold=True))
B(bullet('Slide 1: título del bloque + mi nombre + 1 frase de gancho.'))
B(bullet('Slide 2: el ejemplo Cliente / List<Pedido> vs las dos tablas con FK.'))
B(bullet('Slide 3: la torre de abstracción (esta debe estar IMPECABLE).'))
B(bullet('Slide 4: tabla con JPA / Hibernate / Spring Data y qué es cada cosa.'))
B(bullet('Slide 5: tres ventajas, tres costos.'))
B(bullet('Slide 6: frase de handoff con el nombre del próximo expositor.'))

B(p('Lo que NO va en mis slides', bold=True))
B(bullet('Código (lo dijo la consigna: 100% teoría).'))
B(bullet('application.properties — eso lo cubre el integrante 2.'))
B(bullet('Anotaciones específicas como @Column o @ManyToOne — eso lo cubre el integrante 3.'))
B(bullet('Repositorios y queries — eso lo cubre el integrante 4.'))

B(page_break())

# ============================ BIBLIOGRAFIA ============================
B(heading('Bibliografía', 1))

B(p(
    'Las afirmaciones técnicas de este informe están respaldadas por documentación '
    'oficial. URLs principales agrupadas por tema:'
))

B(heading('Especificación JPA / Jakarta Persistence', 2))
B(bullet('Especificación Jakarta Persistence 3.1 — jakarta.ee/specifications/persistence/3.1/'))
B(bullet('Renombramiento Java EE → Jakarta EE — jakarta.ee/about/'))

B(heading('Hibernate', 2))
B(bullet('Hibernate User Guide — docs.hibernate.org/orm/current/userguide/html_single/Hibernate_User_Guide.html'))
B(bullet('Hibernate ORM (sitio principal) — hibernate.org/orm/'))

B(heading('Spring', 2))
B(bullet('Spring Boot Reference — JPA y Spring Data JPA — docs.spring.io/spring-boot/reference/data/sql.html'))
B(bullet('Spring Data JPA Reference — docs.spring.io/spring-data/jpa/reference/'))
B(bullet('Spring Data Commons Reference — docs.spring.io/spring-data/commons/reference/'))

B(heading('JDBC', 2))
B(bullet('JDBC Overview (Oracle) — docs.oracle.com/javase/tutorial/jdbc/overview/'))

B(heading('Conceptos generales y referencias autorizadas', 2))
B(bullet('Vlad Mihalcea (Hibernate Developer Advocate) — vladmihalcea.com'))
B(bullet('NestJS — docs.nestjs.com (Providers, Database) para las analogías de la audiencia'))

B(p(''))
B(p('— Fin del informe del Integrante 1 —', italic=True, color='888888'))


# ---------------------------------------------------------------------------
# Build
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
