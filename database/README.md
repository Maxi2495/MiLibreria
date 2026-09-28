# Base de datos

Esta carpeta contiene los archivos relacionados con el diseño y la creación de la base de datos de BookNest.

## Tecnología

El sistema utilizará MySQL como sistema de gestión de base de datos relacional.

## Archivos

### `schema.sql`

Contiene el esquema inicial de la base de datos e incluye:

- creación de la base de datos `booknest`;
- creación de las tablas principales;
- claves primarias;
- claves foráneas;
- restricciones de integridad;
- relaciones entre las entidades;
- índices principales para las consultas previstas por el sistema.

El script fue elaborado a partir del modelo de datos definido en `docs/arquitectura.md`.

## Ejecución

El esquema puede crearse ejecutando el archivo `schema.sql` sobre una instancia de MySQL.

Desde el cliente de MySQL puede utilizarse:

```sql
SOURCE database/schema.sql;