# BookNest — Sistema de Gestión de Bibliotecas Personales

**Trabajo Final Integrador**  
*Tecnicatura Universitaria en Programación — Universidad Tecnológica Nacional (UTN)*  
**Ciclo Lectivo:** 2026  

* **Equipo de Desarrollo:** Maximiliano Niemiec & Paola Pasallo  
* **Docente Tutora:** Lic. Sofía Carnevale  
* **Repositorio Oficial:** [https://github.com/Maxi2495/MiLibreria](https://github.com/Maxi2495/MiLibreria)  

---

## 1. Nombre del Proyecto
**BookNest** es una aplicación web orientada a la gestión, trazabilidad y organización de bibliotecas personales. El sistema permite registrar los libros que posee cada usuario, organizar su ubicación física en estantes reales, realizar un seguimiento de sus lecturas, gestionar préstamos y obtener estadísticas sobre la composición de su colección.

El concepto de BookNest surge de la idea de crear un espacio digital donde "vivan" los libros del usuario, manteniendo una relación directa entre la colección física del hogar y su representación digital.

---

## 2. Problemática y Justificación del Desarrollo

### 2.1. Diagnóstico del Problema
A medida que una biblioteca personal comienza a crecer, mantenerla organizada se convierte en una tarea compleja. Resulta difícil conocer rápidamente qué ejemplares se poseen, dónde se encuentran ubicados, cuáles fueron leídos y cuáles fueron prestados a terceros.

Entre las principales problemáticas identificadas se encuentran:
* **Pérdida de ejemplares por préstamos no registrados:** Préstamos a familiares o conocidos sin control de fechas ni destinatarios.
* **Desorganización y dificultad de localización física:** Dificultad para encontrar un ejemplar distribuido entre diferentes muebles, estantes o habitaciones.
* **Compras duplicadas:** Adquisición involuntaria de ejemplares que ya formaban parte de la colección por falta de un inventario accesible en tiempo real.
* **Falta de seguimiento de lectura:** Dificultad para registrar libros leídos, pendientes, fechas, valoraciones y citas personales.
* **Información bibliográfica dispersa:** Carga manual repetitiva de datos que podrían obtenerse de forma automática.
* **Falta de organización en compras futuras:** Listas de deseos (*wishlists*) desvinculadas del inventario real.

---

## 3. Justificación Técnica: Comparativa frente a Planillas de Cálculo

| Criterio | Limitación de una Planilla de Cálculo (Excel / Sheets) | Solución Propuesta por BookNest |
| :--- | :--- | :--- |
| **Organización de datos** | Información dispersa y difícil de consultar en tiempo real. | Gestión centralizada mediante una aplicación web responsiva. |
| **Integridad de datos** | Errores tipográficos, duplicación de autores/géneros y falta de restricciones. | Base de datos relacional (MySQL) normalizada con claves foráneas y tipado estricto. |
| **Gestión de préstamos** | Seguimiento manual estático sin reglas de disponibilidad. | Máquina de estados de préstamos con control de disponibilidad en tiempo real. |
| **Localización física** | Difícil representación de la distribución espacial de los libros. | Gestión jerárquica de bibliotecas, estantes y capacidades reales. |
| **Carga de ejemplares** | Carga 100% manual propensa a errores. | Búsqueda y autocompletado automático de metadatos mediante API externa por código ISBN. |
| **Lista de deseos** | Separada del inventario y mantenida de forma manual. | Wishlist integrada con flujo de conversión directa a ejemplar adquirido. |
| **Seguimiento de lecturas** | Requiere mantenimiento manual de celdas. | Estados de lectura (*Pendiente, Leyendo, Leído, Abandonado*), fechas, reseñas y notas. |
| **Visualización** | Estadísticas y gráficos que requieren armado manual. | Dashboard interactivo con indicadores de colección y ocupación de estantes. |
| **Escalabilidad** | Rígida; no permite integraciones ni crecimiento modular. | Arquitectura desacoplada en capas extensible a futuros inventarios del hogar. |

---

## 4. Objetivos del Proyecto

### 4.1. Objetivo General
Desarrollar una aplicación web que permita a los usuarios gestionar, organizar y visualizar su biblioteca personal, vinculando los libros con su ubicación física, realizando un seguimiento de sus lecturas, registrando valoraciones, administrando préstamos, gestionando una lista de deseos y obteniendo estadísticas sobre su colección.

### 4.2. Objetivos Específicos
* Centralizar el inventario bibliográfico de cada usuario de forma independiente.
* Facilitar el alta de libros mediante carga manual o consulta automática por ISBN via API externa.
* Representar la organización física del hogar (muebles, estantes y capacidades).
* Visualizar de manera gráfica la ocupación y distribución de los estantes.
* Registrar el ciclo de vida de préstamos a terceros.
* Gestionar una lista de deseos integrada que permita mover libros adquiridos al inventario físico.
* Proveer un dashboard visual con métricas y composición de la biblioteca.

---

## 5. Alcance del Sistema: Módulos del MVP

### 5.1. Gestión de Usuarios
* Registro, inicio y cierre de sesión seguro.
* Aislamiento de datos: cada usuario administra su propia biblioteca privada.

### 5.2. Catálogo de Libros (CRUD)
* Alta, edición, baja y consulta de libros.
* Búsqueda facetada y ordenamiento multicriterio (título, autor, género, editorial, año).

### 5.3. Integración con API de ISBN
* Consulta de código ISBN consumiendo APIs públicas (Google Books / Open Library).
* Autocompletado de título, autor, editorial, fecha de publicación, sinopsis y portada.

### 5.4. Lista de Deseos (Wishlist)
* Registro de libros pendientes de compra.
* Flujo de conversión: al marcar un libro como adquirido, se transfiere al catálogo y se le asigna un estante físico.

### 5.5. Gestión de Espacios Físicos y Representación Visual
* Creación de muebles/bibliotecas y asignación de estantes con capacidad máxima de ejemplares.
* Representación gráfica del nivel de ocupación de cada estante (porcentaje y tarjetas de libros).

### 5.6. Seguimiento de Lectura
* Estados: *Pendiente de lectura*, *En lectura*, *Leído*, *Abandonado*.
* Fechas de inicio/fin, calificación (estrellas), reseñas y anotaciones privadas.

### 5.7. Control de Préstamos
* Registro de destinatario, fecha de salida, fecha límite de devolución y observaciones de estado.
* Indicador de disponibilidad: un libro prestado no puede ser prestado nuevamente hasta su retorno.

### 5.8. Dashboard y Estadísticas
* Gráficos por género, autores predominantes, estado de lectura y ocupación de estanterías.

---

## 6. Funcionalidades Futuras (Fase 2 / Post-MVP)
Siguiendo las pautas pedagógicas de viabilidad temporal, se planifican para una etapa posterior:
* **Comunidad y Red Social:** Amigos, intercambio de recomendaciones públicas y préstamos entre usuarios de la plataforma.
* **Notificaciones:** Recordatorios automáticos por correo de préstamos vencidos.
* **Extensión Multidominio:** Módulos para inventario de despensa/alacena e insumos del hogar.

---

## 7. Arquitectura y Stack Tecnológico

El sistema adopta una arquitectura desacoplada **Cliente-Servidor (SPA + API RESTful)**:

```text
  [ CLIENTE (Navegador) ]  <=== (HTTP/JSON via Fetch) ===>  [ BACKEND API REST ]  <=== (SQLAlchemy) ===>  [ BASE DE DATOS ]
   HTML5 + CSS3 + JS                                          Python + FastAPI                                  MySQL (Cloud)
```

| Componente | Tecnología / Herramienta | Justificación |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript Vanilla | Interfaz responsiva, liviana y sin sobrecarga de frameworks externos. |
| **Backend** | Python 3 + FastAPI | Framework moderno para APIs REST, tipado estricto con Pydantic y documentación Swagger interactiva (`/docs`). |
| **ORM** | SQLAlchemy | Mapeo objeto-relacional robusto, transacciones seguras y prevención de SQL Injection. |
| **Base de Datos** | MySQL | Motor relacional con integridad referencial estricta y soporte de transacciones ACID. |
| **API Externa** | Google Books / Open Library | Obtención automática de metadatos bibliográficos por ISBN. |
| **Control de Versiones** | Git + GitHub | Control de código fuente y flujo de trabajo colaborativo. |
| **Gestión Ágil** | Trello (Kanban) | Organización de tareas (*Backlog, En Progreso, En Revisión, Finalizado*). |
| **Pruebas de API** | Swagger UI (`/docs`) y Postman | Validación y documentación de endpoints REST. |

---

## 8. Despliegue en la Nube (Cloud Deployment)

En cumplimiento de los requisitos de la cátedra:
* **Frontend:** Alojado en **Vercel** / **Netlify**.
* **Backend:** Alojado en **Render** (ejecución del servicio ASGI Uvicorn con HTTPS).
* **Base de Datos:** Instancia gestionada de **MySQL** en la nube (**Aiven** / **Clever Cloud**).

---

## 9. Metodología de Trabajo y Ramas de Git

Se utiliza una estrategia de desarrollo basada en ramas (*Feature Branch Workflow*):
* `main`: Código estable y desplegado en producción.
* `develop`: Integración continua de avances probados.
* `feature/<nombre-funcionalidad>`: Ramas específicas para cada módulo integradas mediante Pull Requests revisados por el equipo.