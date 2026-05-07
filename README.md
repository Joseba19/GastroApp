# GastroApp — Plataforma de gestión para escuelas de cocina 🍳

GastroApp es un sistema completo de administración gastronómica concebido para centralizar todas las operaciones de una escuela de cocina. Integra una potente base de datos relacional con dos aplicaciones web diferenciadas: un portal público para consultar recetas y un panel interno de gestión, ofreciendo una solución integral tanto para el personal como para los usuarios externos.

---

## 🗂️ Descripción general del proyecto

El repositorio se organiza en dos módulos principales y los ficheros de base de datos necesarios para desplegarlos:

- **`GastroApp/`** – Aplicación web pública (Flask)
- **`GastroManagment/`** – Panel de administración interna (Flask)
- **`gastrolab.sql`** – Volcado completo de la base de datos MySQL
- **`RolesUsuarios.sql`** – Definición de roles y permisos para la base de datos

La base de datos, denominada **Gastrolab**, unifica el recetario, la información nutricional, la planificación de menús y la gestión de personal en un solo lugar.

> El proyecto está compuesto principalmente por **HTML (49.4 %)**, **Python (41.2 %)** y **CSS (9.4 %)**.

---

## 🧱 Estructura de la base de datos

La base de datos `gastrolab` está diseñada para cubrir todos los aspectos operativos de una escuela de cocina:

| Tabla | Descripción |
|---|---|
| `empleados` | Personal interno: cocineros, docentes, apoyo y alumnos de cocina/dietética |
| `contratos` | Información laboral de cada empleado (histórico y vigente) |
| `usuarios` | Usuarios externos que acceden a la plataforma web pública |
| `usuarios_login` | Credenciales de acceso al sistema interno (solo para cocineros y docentes) |
| `ingredientes` | Base de datos nutricional por cada 100 g/ml |
| `alérgenos` | Catálogo estándar de alérgenos alimentarios |
| `ingredientes_alergenos` | Relación N:M entre ingredientes y alérgenos |
| `categorias_receta` | Clasificación del recetario (entrantes, postres, vegano…) |
| `recetas` | Cabecera de cada receta culinaria |
| `recetas_ingredientes` | Escandallo: ingredientes, cantidades y notas |
| `pasos_receta` | Instrucciones de elaboración ordenadas |
| `menus` | Planificación de menús (diarios, semanales, especiales) |
| `menus_recetas` | Composición de cada menú con tipo de plato y orden |
| `favoritos` | Recetas guardadas por usuarios públicos |

### Vista destacada

**`vista_nutricion_receta`** — Calcula los macronutrientes por ración y lista los alérgenos presentes en cada receta.

### Roles y permisos

El archivo `RolesUsuarios.sql` crea dos roles de base de datos:

- `rol_lectura` — Solo permisos de `SELECT` sobre todas las tablas
- `rol_admin` — Privilegios completos

Además, define los usuarios `lector1`, `lector2` y `admin` con las contraseñas indicadas en el script.

---

## 🚀 Funcionalidades principales

### GastroApp (portal público)

- Página de inicio con buscador y listado de recetas
- Vista detallada de cada receta (ingredientes, pasos, tiempo, dificultad)
- Modal de inicio de sesión con validación contra MySQL
- Página "Sobre nosotros" con información del proyecto
- Diseño responsive con paleta de colores orgánica

### GastroManagment (panel de administración)

- Sistema de autenticación con sesiones, contraseñas hasheadas (bcrypt) y decorador `login_required`
- Dashboard con tarjetas de acceso rápido a ingredientes recientes y empleados nuevos
- Listado de recetas paginado con filtros por categoría y dificultad
- Vista detallada de cada receta: pasos, ingredientes, alérgenos e información nutricional
- Formulario para insertar nuevas recetas completas (ingredientes, cantidades, pasos)
- Gestión de ingredientes, menús, empleados, contratos y alérgenos
- Base de datos alojada en un servidor externo (`nas.latorreg.es`)

---

## 🛠️ Tecnologías utilizadas

| Capa | Tecnología |
|---|---|
| Backend | Python 3, Flask |
| Base de datos | MySQL 8.0 |
| Frontend | HTML5, CSS3 (variables CSS, grid, flexbox) |
| Librerías | `mysql-connector-python`, `bcrypt`, `pytest` |
| Herramientas | Git, GitHub |

---

## 📁 Estructura del proyecto

```
GastroApp/
├── GastroApp/                    # Aplicación web pública
│   ├── static/
│   │   ├── img/                  # Imágenes del sitio
│   │   └── style.css             # Hoja de estilos principal
│   ├── templates/
│   │   ├── index.html            # Página principal
│   │   └── nosotros.html         # Página "Sobre nosotros"
│   ├── __pycache__/              # Archivos compilados de Python
│   ├── app.py                    # Lógica de la app pública
│   ├── app2.py                   # Versión alternativa (recetas desde JSON)
│   ├── test.py                   # Pruebas unitarias (pytest)
│   ├── testdb.py                 # Script de prueba de conexión a BD
│   └── .gitignore
├── GastroManagment/              # Panel de administración
│   ├── static/                   # Recursos estáticos
│   ├── templates/                # Plantillas Jinja2
│   ├── app.py                    # Lógica principal del panel
│   ├── db.py                     # Capa de acceso a datos
│   ├── README.md                 # Documentación de la base de datos
│   ├── RolesUsuarios.sql         # Roles y permisos
│   └── .gitignore
├── gastrolab.sql                 # Volcado completo de la BD
└── RolesUsuarios.sql             # Script global de roles y usuarios
```

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/Joseba19/GastroApp.git
cd GastroApp
```

### 2. Configurar la base de datos

El volcado completo se encuentra en `gastrolab.sql`. Ejecútalo en tu servidor MySQL:

```bash
mysql -u root -p < gastrolab.sql
```

Posteriormente, carga los roles y usuarios:

```bash
mysql -u root -p < RolesUsuarios.sql
```

### 3. Configurar las credenciales de conexión

Edita los archivos de configuración en ambas aplicaciones:

- En `GastroApp/app.py` (línea 4)
- En `GastroManagment/db.py` (líneas 4-6)

Ajusta `host`, `user`, `password` y `database` según tu entorno.

### 4. Instalar dependencias

```bash
pip install flask mysql-connector-python bcrypt pytest
```

### 5. Ejecutar las aplicaciones

**Portal público:**

```bash
cd GastroApp
python app.py
```

**Panel de administración:**

```bash
cd GastroManagment
python app.py
```

> ⚠️ **Nota:** Para un entorno de producción, modifica la clave secreta de Flask (`app.secret_key`) y elimina las credenciales hardcodeadas del código fuente.

---

## 🧪 Pruebas

El proyecto incluye pruebas unitarias para la aplicación pública, utilizando `pytest` con fixtures y mocks. Las pruebas cubren la carga y guardado de archivos JSON, las rutas del servidor y la autenticación.

```bash
cd GastroApp
python -m pytest test.py -v
```

El script `testdb.py` permite verificar la conectividad con la base de datos de forma rápida.

---

## 👥 Contribuidores

Este proyecto ha sido desarrollado por un equipo de cuatro personas:

- [@Joseba19](https://github.com/Joseba19)
- [@jonkaso](https://github.com/jonkaso)
- [@aaronbgrg-dot](https://github.com/aaronbgrg-dot)
- [@villamikel44-svg](https://github.com/villamikel44-svg)

El historial de commits muestra un total de **22 confirmaciones**, con la última actividad registrada en mayo de 2026.

---

## 📝 Licencia

Este proyecto no especifica actualmente una licencia de uso. Si deseas utilizarlo, te recomendamos contactar con los autores.

---

*GastroApp — Donde la tecnología y la gastronomía se encuentran.*