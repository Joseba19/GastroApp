# Gastrolab — Base de datos

Base de datos MySQL para la gestión interna de una escuela de cocina y su plataforma web pública. Centraliza el recetario, la información nutricional, la planificación de menús y la gestión de personal.

---

## Tablas

### `empleados`
Personal interno de la escuela: cocineros, docentes, personal de apoyo y alumnado de cocina y dietética.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_empleado` | INT (PK, AI) | Identificador único |
| `nombre` | VARCHAR(100) | Nombre del empleado |
| `apellidos` | VARCHAR(150) | Apellidos |
| `email` | VARCHAR(150) | Correo institucional (único) |
| `telefono` | VARCHAR(20) | Teléfono de contacto |
| `puesto` | ENUM | `cocinero`, `docente`, `apoyo`, `alumno_cocina`, `alumno_dietetica` |
| `activo` | TINYINT(1) | Soft delete: 1 = activo, 0 = inactivo |
| `fecha_alta` | DATE | Fecha de incorporación |

---

### `contratos`
Información laboral y económica de cada empleado. Un empleado puede tener varios contratos históricos, pero solo uno activo.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_contrato` | INT (PK, AI) | Identificador único |
| `id_empleado` | INT (FK) | Empleado al que pertenece |
| `tipo_contrato` | VARCHAR(100) | Indefinido, Temporal, Prácticas… |
| `fecha_inicio` | DATE | Inicio del contrato |
| `fecha_fin` | DATE | Fin del contrato (NULL = indefinido) |
| `horas_semanales` | DECIMAL(5,2) | Jornada semanal |
| `salario_bruto_anual` | DECIMAL(10,2) | Retribución bruta anual |
| `salario_neto` | DECIMAL(10,2) | Retribución neta |
| `activo` | TINYINT(1) | 1 = contrato vigente |

---

### `usuarios`
Usuarios externos que acceden a la plataforma web pública para consultar recetas y guardar favoritos.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_usuario` | INT (PK, AI) | Identificador único |
| `nombre` | VARCHAR(100) | Nombre del usuario |
| `email` | VARCHAR(150) | Email (único) |
| `password_hash` | VARCHAR(255) | Contraseña encriptada |
| `fecha_registro` | DATETIME | Momento de registro |
| `activo` | TINYINT(1) | Soft delete |

---

### `usuarios_login`
Credenciales de acceso al sistema interno. Solo se generan para empleados con puesto `cocinero` o `docente` (gestionado automáticamente por el trigger `trg_empleado_login`).

| Campo | Tipo | Descripción |
|---|---|---|
| `id_usuario` | INT (PK, AI) | Identificador único |
| `id_empleado` | INT (FK) | Empleado asociado |
| `username` | VARCHAR(80) | Nombre de usuario (único) |
| `password_hash` | VARCHAR(255) | Hash bcrypt |
| `activo` | TINYINT(1) | 1 = acceso habilitado |

---

### `ingredientes`
Base de datos nutricional de ingredientes. Todos los valores nutricionales están expresados por cada 100 g/ml.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_ingrediente` | INT (PK, AI) | Identificador único |
| `nombre` | VARCHAR(150) | Nombre del ingrediente |
| `unidad_medida` | VARCHAR(50) | Unidad base (g, ml, ud…) |
| `categoria` | VARCHAR(100) | Familia (Carne, Verdura, Lácteo…) |
| `calorias_100g` | DECIMAL(7,2) | Kcal por 100 g/ml |
| `proteinas_100g` | DECIMAL(6,2) | Proteínas por 100 g/ml |
| `carbohidratos_100g` | DECIMAL(6,2) | Carbohidratos por 100 g/ml |
| `grasas_100g` | DECIMAL(6,2) | Grasas por 100 g/ml |
| `fibra_100g` | DECIMAL(6,2) | Fibra por 100 g/ml |
| `sodio_100g` | DECIMAL(7,2) | Sodio (mg) por 100 g/ml |

---

### `alergenos`
Catálogo estándar de alérgenos alimentarios (gluten, lácteos, frutos secos…).

| Campo | Tipo | Descripción |
|---|---|---|
| `id_alergeno` | INT (PK, AI) | Identificador único |
| `nombre` | VARCHAR(100) | Nombre oficial (único) |
| `descripcion` | TEXT | Detalle de alimentos que lo contienen |

---

### `ingredientes_alergenos`
Relación N:M entre ingredientes y alérgenos. Indica qué alérgenos contiene cada ingrediente.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_ingrediente` | INT (PK, FK) | Ingrediente |
| `id_alergeno` | INT (PK, FK) | Alérgeno |

---

### `categorias_receta`
Clasificación para organizar el recetario (Entrantes, Postres, Vegano…).

| Campo | Tipo | Descripción |
|---|---|---|
| `id_categoria` | INT (PK, AI) | Identificador único |
| `nombre` | VARCHAR(100) | Nombre de la categoría (único) |
| `descripcion` | TEXT | Tipos de platos que incluye |

---

### `recetas`
Cabecera de cada receta culinaria. Los ingredientes y los pasos se almacenan en tablas relacionadas.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_receta` | INT (PK, AI) | Identificador único |
| `nombre` | VARCHAR(200) | Nombre de la receta |
| `descripcion` | TEXT | Resumen o notas introductorias |
| `tiempo_preparacion` | INT | Minutos de trabajo activo |
| `tiempo_coccion` | INT | Minutos de fuego/horno |
| `raciones` | INT | Número de porciones |
| `dificultad` | ENUM | `facil`, `medio`, `dificil` |
| `id_categoria` | INT (FK) | Categoría principal |
| `id_creador` | INT (FK) | Empleado o alumno que la diseñó |
| `fecha_creacion` | DATE | Fecha de alta |

---

### `recetas_ingredientes`
Escandallo de cada receta: qué ingredientes la componen, en qué cantidad y con qué instrucciones específicas.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_receta` | INT (PK, FK) | Receta |
| `id_ingrediente` | INT (PK, FK) | Ingrediente |
| `cantidad` | DECIMAL(8,3) | Cantidad requerida |
| `unidad` | VARCHAR(50) | Unidad para esta receta |
| `notas` | VARCHAR(255) | Instrucciones específicas ("picado fino"…) |

---

### `pasos_receta`
Instrucciones de elaboración paso a paso de cada receta.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_paso` | INT (PK, AI) | Identificador único |
| `id_receta` | INT (FK) | Receta a la que pertenece |
| `numero_paso` | INT | Orden secuencial (1, 2, 3…) |
| `descripcion` | TEXT | Instrucción detallada |

---

### `menus`
Agrupaciones de recetas para planificaciones de servicio.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_menu` | INT (PK, AI) | Identificador único |
| `nombre` | VARCHAR(200) | Nombre del menú |
| `descripcion` | TEXT | Descripción |
| `tipo` | ENUM | `diario`, `semanal`, `especial` |
| `id_creador` | INT (FK) | Empleado que lo elaboró |
| `fecha_creacion` | DATE | Fecha de creación |
| `activo` | TINYINT(1) | 1 = menú vigente |

---

### `menus_recetas`
Composición de cada menú: qué recetas lo forman, en qué momento del servicio y en qué orden.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_menu` | INT (PK, FK) | Menú |
| `id_receta` | INT (PK, FK) | Receta |
| `tipo_plato` | ENUM | `entrante`, `principal`, `postre`, `bebida` |
| `orden` | INT | Orden dentro del mismo tipo de plato |

---

### `favoritos`
Recetas guardadas por los usuarios públicos de la plataforma web.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_usuario` | INT (PK, FK) | Usuario público |
| `id_receta` | INT (PK, FK) | Receta guardada |
| `fecha_adicion` | DATETIME | Momento en que se guardó |

---

## Vista

### `vista_nutricion_receta`
Consolida la información nutricional de cada receta calculando los macronutrientes por ración y listando los alérgenos presentes.

```sql