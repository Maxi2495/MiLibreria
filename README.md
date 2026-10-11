# BookNest

## Sistema de Gestión de Bibliotecas Personales

BookNest es una aplicación web orientada a la gestión de bibliotecas personales físicas. El sistema busca centralizar la organización de libros y ejemplares, representar su ubicación dentro de bibliotecas y estantes del hogar y permitir el seguimiento de lecturas, préstamos, anotaciones y libros deseados.

El proyecto se desarrolla como Trabajo Final Integrador de la Tecnicatura Universitaria en Programación de la UTN.

## Integrantes

- Maximiliano Niemiec
- Paola Pasallo

**Docente tutora:** Lic. Sofía Carnevale

## Funcionalidades principales

El MVP de BookNest contempla:

- registro y autenticación de usuarios;
- gestión de libros y ejemplares físicos;
- organización mediante bibliotecas y estantes;
- control de capacidad y ubicación física de los ejemplares;
- registro y seguimiento de lecturas y relecturas;
- calificaciones y reseñas;
- gestión de préstamos;
- anotaciones generales y asociadas a ejemplares;
- wishlist de libros deseados;
- consulta de información bibliográfica mediante servicios externos;
- dashboard con indicadores y estadísticas de la biblioteca personal.

## Arquitectura

BookNest utilizará una arquitectura cliente-servidor organizada en capas.

El frontend se comunicará con el backend mediante una API REST utilizando HTTP y JSON. El backend concentrará la lógica de negocio y accederá a una base de datos relacional mediante un ORM.

La descripción detallada de la arquitectura, los módulos, las reglas de negocio y el modelo de datos se encuentra en [`docs/arquitectura.md`](docs/arquitectura.md).

## Tecnologías

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- FastAPI
- SQLAlchemy

### Base de datos

- MySQL

### Herramientas y documentación

- Git
- GitHub
- Swagger / OpenAPI
- Postman
- Mermaid

## Estructura del repositorio

```text
MiLibreria/
├── backend/
│   └── README.md
├── database/
│   ├── README.md
│   └── schema.sql
├── docs/
│   ├── arquitectura.md
│   └── propuesta_proyecto.md
├── frontend/
│   └── README.md
└── README.md
```