# BookNest - Arquitectura del Sistema

## 1. Introducción

BookNest es una aplicación web orientada a la gestión de bibliotecas personales físicas. Su objetivo es permitir que cada usuario pueda organizar y administrar su colección de libros, registrar la ubicación física de sus ejemplares, realizar un seguimiento de sus lecturas, gestionar préstamos, mantener una lista de deseos y consultar información general sobre su biblioteca.

La presente propuesta define la arquitectura general de BookNest, los módulos que compondrán el sistema y las principales reglas de negocio que deberán respetarse durante su desarrollo. Asimismo, servirá como base para el diseño del modelo de datos y para la posterior implementación de la aplicación.

## 2. Objetivo de la arquitectura

La arquitectura de BookNest busca organizar el sistema mediante una separación clara de responsabilidades, favoreciendo un bajo acoplamiento y una alta cohesión entre sus componentes.

Se propone una arquitectura en capas que permita separar la interfaz de usuario, la lógica de negocio, el acceso a los datos y la persistencia. Esta organización facilitará el mantenimiento, las pruebas y la incorporación de nuevas funcionalidades sin afectar innecesariamente otros componentes del sistema.

Además, la arquitectura contempla la integración con servicios bibliográficos externos para facilitar la carga de información de los libros a partir de su ISBN.

## 3. Arquitectura general del sistema

BookNest utilizará una arquitectura cliente-servidor. El frontend funcionará como cliente y será responsable de presentar la interfaz web y permitir la interacción del usuario con las funcionalidades del sistema.

Las solicitudes realizadas desde el frontend serán enviadas al backend mediante una API REST utilizando HTTP y JSON. El backend, desarrollado con Python y FastAPI, será responsable de procesar las solicitudes, aplicar las reglas de negocio y coordinar el acceso a los datos.

Para la persistencia de la información se utilizará una base de datos relacional MySQL. El acceso a la base de datos se realizará mediante SQLAlchemy como ORM, permitiendo trabajar con las entidades del sistema desde Python y reduciendo el acoplamiento directo con las consultas SQL.

Además, el backend se integrará con una API bibliográfica externa para consultar información de libros a partir del ISBN, permitiendo obtener automáticamente datos como título, autores, editorial, fecha de publicación, sinopsis y portada cuando dicha información se encuentre disponible.

El flujo general de comunicación será:

Usuario → Frontend → API REST → Backend → Base de datos

Cuando sea necesario obtener información bibliográfica externa:

Backend → API bibliográfica externa

## 4. Arquitectura en capas

Para organizar las responsabilidades del sistema, BookNest utilizará una arquitectura en capas. Cada capa tendrá una función específica y se comunicará con las demás de manera controlada, evitando concentrar toda la lógica de la aplicación en un mismo componente.

### 4.1. Capa de presentación

Corresponde al frontend de la aplicación, desarrollado con HTML5, CSS3 y JavaScript.

Será responsable de mostrar la interfaz al usuario, capturar sus acciones y presentar la información recibida desde el backend. No contendrá reglas de negocio ni accederá directamente a la base de datos.

### 4.2. Capa de API o controladores

Estará implementada mediante FastAPI y será el punto de entrada de las solicitudes provenientes del frontend.

Su responsabilidad será recibir las peticiones HTTP, validar los datos de entrada correspondientes, invocar la lógica de negocio necesaria y devolver las respuestas mediante la API REST.

### 4.3. Capa de servicios o lógica de negocio

Contendrá las principales reglas de negocio de BookNest.

Esta capa será responsable de coordinar las operaciones del sistema y aplicar las validaciones correspondientes. Por ejemplo, controlar la capacidad disponible de un estante, impedir que un ejemplar tenga más de un préstamo activo o gestionar la conversión de un elemento de la lista de deseos en un ejemplar adquirido.

### 4.4. Capa de persistencia o acceso a datos

Será responsable de gestionar el acceso a la información almacenada en la base de datos.

Se utilizará SQLAlchemy como ORM para representar y manipular las entidades del sistema desde Python. Esta capa permitirá separar la lógica de negocio de los detalles específicos de persistencia.

### 4.5. Capa de base de datos

La información persistente de BookNest será almacenada en una base de datos relacional MySQL.

En ella se conservarán los datos correspondientes a usuarios, libros, ejemplares, bibliotecas, estantes, lecturas, préstamos, anotaciones, lista de deseos y demás entidades necesarias para el funcionamiento del sistema.

### 4.6. Integraciones externas

Las comunicaciones con servicios externos se mantendrán separadas de la lógica principal del sistema.

Inicialmente, BookNest contará con una integración bibliográfica que permitirá consultar información de libros mediante ISBN. El backend será responsable de realizar estas consultas y transformar la información obtenida antes de utilizarla dentro de la aplicación.

## 5. Módulos del sistema

BookNest se organizará en módulos funcionales con responsabilidades específicas. Esta división busca mantener una alta cohesión dentro de cada módulo y reducir el acoplamiento entre las distintas funcionalidades del sistema.

### 5.1. Módulo de Usuarios y Autenticación

Será responsable de la gestión de las cuentas de usuario y del acceso seguro al sistema.

Permitirá el registro, inicio y cierre de sesión, modificación de los datos personales y cambio de contraseña. Cada usuario tendrá acceso únicamente a la información correspondiente a su propia biblioteca.

La eliminación de una cuenta se manejará mediante baja lógica, conservando la información relacionada para mantener la integridad de los datos. La recuperación de contraseña mediante correo electrónico se considera una funcionalidad futura y no formará parte del MVP.

### 5.2. Módulo de Catálogo de Libros y Ejemplares

Será responsable de la administración de los libros que forman parte de la colección del usuario.

El sistema diferenciará entre Libro y Ejemplar. Libro representará la información bibliográfica correspondiente a una edición, mientras que Ejemplar representará una copia física concreta perteneciente al usuario. De esta manera, un mismo libro podrá estar asociado a varios ejemplares físicos.

Permitirá registrar, consultar, modificar y dar de baja ejemplares, además de realizar búsquedas, aplicar filtros y ordenar la colección utilizando distintos criterios.

### 5.3. Módulo de Wishlist

Permitirá administrar los libros que el usuario desea adquirir.

Los elementos de la lista de deseos podrán registrarse manualmente o mediante una consulta por ISBN. Cada elemento podrá encontrarse en estado PENDIENTE, ADQUIRIDO o DESCARTADO.

Cuando un elemento sea marcado como ADQUIRIDO, se generará el ejemplar correspondiente dentro de la biblioteca personal del usuario. El nuevo ejemplar quedará inicialmente sin ubicación física asignada y con una lectura en estado PENDIENTE.

### 5.4. Módulo de Bibliotecas y Estantes

Será responsable de representar digitalmente la organización física de la colección.

El usuario podrá crear diferentes bibliotecas o espacios de almacenamiento y, dentro de cada una, definir sus respectivos estantes. Cada estante contará con una capacidad máxima expresada en cantidad de ejemplares.

El sistema controlará la ocupación de los estantes y permitirá identificar ejemplares con o sin ubicación asignada.

### 5.5. Módulo de Lecturas

Permitirá registrar y consultar el historial de lectura de cada ejemplar.

Cada ejemplar podrá tener múltiples lecturas a lo largo del tiempo, permitiendo registrar relecturas sin eliminar la información anterior. Las lecturas podrán encontrarse en estado PENDIENTE, EN_CURSO, LEIDO o ABANDONADO.

También podrán registrarse fechas de inicio y finalización, una calificación opcional de una a cinco estrellas y una reseña. Cuando ambas fechas estén disponibles, la duración de la lectura podrá calcularse automáticamente.

### 5.6. Módulo de Anotaciones

Permitirá almacenar anotaciones privadas del usuario.

Se contemplarán anotaciones generales, similares a un bloc de notas o post-it, y anotaciones asociadas a un ejemplar específico. Las anotaciones podrán crearse, modificarse y eliminarse.

Las anotaciones vinculadas a un ejemplar serán independientes de sus lecturas, por lo que no se asociarán a una lectura particular ni se compartirán automáticamente con otros ejemplares del mismo libro.

### 5.7. Módulo de Préstamos

Será responsable de registrar y controlar los préstamos de ejemplares físicos a terceros.

Cada préstamo almacenará los datos básicos de la persona que recibe el ejemplar, la fecha del préstamo, una fecha prevista de devolución opcional y, cuando corresponda, la fecha real de devolución.

Los préstamos podrán encontrarse en estado ACTIVO, VENCIDO, DEVUELTO o CANCELADO. Un mismo ejemplar podrá tener múltiples préstamos históricos, pero solamente uno podrá permanecer activo al mismo tiempo.

### 5.8. Módulo de Dashboard y Estadísticas

Permitirá visualizar un resumen general de la biblioteca personal del usuario.

El dashboard podrá mostrar la cantidad total de ejemplares, estados de lectura, préstamos activos o vencidos, ejemplares con o sin ubicación y distribuciones por género, autor, editorial y saga.

También podrá presentar anotaciones generales y actividad reciente, manteniendo el alcance como un panel resumen de la colección.

### 5.9. Módulo de Integración Bibliográfica

Será responsable de la comunicación con servicios bibliográficos externos.

Permitirá consultar información a partir de un ISBN para facilitar la carga de libros y obtener automáticamente los datos disponibles, como título, autores, editorial, fecha de publicación, sinopsis y portada.

La información obtenida podrá ser revisada o completada por el usuario antes de incorporarse al sistema.

## 6. Reglas de negocio

Las siguientes reglas definen las condiciones que deberán respetarse durante el funcionamiento de BookNest. Estas reglas serán aplicadas principalmente desde la capa de servicios y deberán ser consideradas también al diseñar el modelo de datos y sus restricciones.

### 6.1. Usuarios

- Cada usuario deberá registrarse con un correo electrónico único.
- La contraseña nunca se almacenará en texto plano, sino mediante un mecanismo seguro de hash.
- Cada usuario solamente podrá acceder y administrar los datos correspondientes a su propia cuenta y biblioteca personal.
- Un usuario autenticado podrá modificar su nombre, apellido, correo electrónico y contraseña.
- Al modificar el correo electrónico, deberá verificarse que no se encuentre registrado por otro usuario.
- Para cambiar la contraseña se solicitará la contraseña actual.
- La eliminación de la cuenta se realizará mediante baja lógica. La cuenta quedará inactiva y no podrá utilizarse para iniciar sesión.
- La recuperación de contraseña mediante correo electrónico no formará parte del MVP y quedará contemplada como funcionalidad futura.

### 6.2. Libros y ejemplares

- BookNest diferenciará entre Libro y Ejemplar.
- Libro representará los datos bibliográficos correspondientes a una edición, mientras que Ejemplar representará una copia física concreta perteneciente a un usuario.
- Un mismo Libro podrá estar asociado a múltiples Ejemplares.
- El ISBN identificará una edición bibliográfica y no un ejemplar físico individual.
- La carga manual de un Libro requerirá como mínimo un título y al menos un autor.
- El ISBN, editorial, fecha de publicación, géneros, saga, posición dentro de la saga, sinopsis y portada serán datos opcionales en una carga manual.
- Un Libro podrá tener uno o varios autores.
- Un Libro podrá pertenecer a uno o varios géneros.
- Un Libro podrá estar asociado a una editorial.
- Un Libro podrá pertenecer opcionalmente a una saga o serie y registrar su posición dentro de ella.
- Cada Ejemplar podrá registrar de manera opcional su fecha de adquisición, estado físico, precio de compra, moneda y una observación.
- La ubicación física de un Ejemplar será opcional.
- Un Ejemplar podrá existir sin estar asignado a ningún estante.
- La baja de un Ejemplar será lógica, con el objetivo de conservar la integridad y el historial de la información.
- No podrá darse de baja un Ejemplar mientras posea un préstamo activo.

### 6.3. Wishlist

- Cada usuario tendrá su propia lista de deseos.
- Los elementos de la Wishlist podrán registrarse manualmente o mediante una consulta bibliográfica por ISBN.
- La carga manual podrá realizarse aun cuando el usuario no conozca el ISBN.
- Un elemento de la Wishlist podrá encontrarse en estado PENDIENTE, ADQUIRIDO o DESCARTADO.
- Si se ingresa un ISBN que ya se encuentra en la Wishlist del usuario, el sistema no permitirá generar un elemento duplicado.
- Si el ISBN corresponde a un Libro del cual el usuario ya posee un Ejemplar, el sistema mostrará una advertencia, pero permitirá incorporarlo a la Wishlist, ya que el usuario podría querer adquirir otra copia.
- Cuando un elemento sea cargado manualmente sin ISBN, el sistema podrá advertir sobre posibles coincidencias de título y autor, pero no bloqueará su incorporación.
- Un elemento de la Wishlist podrá representar tanto un libro deseado de forma genérica como una edición específica identificada mediante ISBN.
- Al marcar un elemento como ADQUIRIDO, se generará un Ejemplar dentro de la biblioteca personal del usuario.
- El nuevo Ejemplar se creará inicialmente sin ubicación física asignada.
- Al generarse el nuevo Ejemplar, se creará una Lectura inicial en estado PENDIENTE.
- Si el elemento de la Wishlist no poseía un ISBN específico, al momento de adquirirlo el usuario podrá completar o confirmar los datos de la edición finalmente adquirida.
- Los elementos marcados como ADQUIRIDO o DESCARTADO se conservarán como historial y no serán eliminados automáticamente.

### 6.4. Bibliotecas y estantes

- Cada usuario podrá crear múltiples Bibliotecas o espacios físicos de almacenamiento.
- El nombre de una Biblioteca deberá ser único dentro de la cuenta del usuario.
- Cada Biblioteca podrá contener múltiples Estantes.
- El nombre de un Estante deberá ser único dentro de su Biblioteca, aunque podrá repetirse en Bibliotecas diferentes.
- Cada Estante tendrá una capacidad máxima definida en cantidad de Ejemplares.
- Cada Ejemplar ubicado físicamente ocupará una unidad de capacidad.
- La capacidad de un Estante podrá modificarse posteriormente.
- No se permitirá reducir la capacidad de un Estante por debajo de la cantidad de Ejemplares que se encuentren actualmente ubicados en él.
- Cuando un Estante alcance su capacidad máxima, no podrán asignarse nuevos Ejemplares hasta que exista espacio disponible o se aumente su capacidad.
- La asignación de un Ejemplar a una Biblioteca y Estante será opcional.
- Los Ejemplares sin ubicación permanecerán identificados como "Sin ubicación asignada".
- BookNest conservará únicamente la ubicación física actual del Ejemplar y no mantendrá un historial de movimientos entre Estantes.
- Para eliminar un Estante que contenga Ejemplares, el usuario deberá previamente trasladarlos a otro Estante con capacidad disponible o dejarlos sin ubicación asignada.
- Para eliminar una Biblioteca que contenga Ejemplares, deberá aplicarse el mismo criterio, reubicando los Ejemplares o dejándolos sin ubicación antes de completar la eliminación.

### 6.5. Lecturas

- Cada Lectura estará asociada a un Ejemplar específico.
- Cada Ejemplar podrá tener múltiples Lecturas, permitiendo registrar relecturas sin modificar ni eliminar las anteriores.
- Al crear un nuevo Ejemplar, se generará automáticamente una primera Lectura en estado PENDIENTE.
- Una Lectura podrá encontrarse en estado PENDIENTE, EN_CURSO, LEIDO o ABANDONADO.
- Las fechas de inicio y finalización serán opcionales.
- Si una Lectura posee fecha de inicio y fecha de finalización, BookNest podrá calcular automáticamente la cantidad de días que tomó completar la lectura.
- La duración de una Lectura será un dato calculado y no se almacenará de forma redundante.
- Cada Lectura podrá tener una calificación opcional de 1 a 5 estrellas.
- La calificación solamente admitirá valores enteros comprendidos entre 1 y 5.
- Cada Lectura podrá incluir una reseña opcional.
- Las diferentes Lecturas de un mismo Ejemplar podrán tener calificaciones y reseñas diferentes.
- BookNest podrá calcular el promedio de las calificaciones correspondientes a las Lecturas de un Ejemplar.
- El promedio de calificaciones será un valor calculado y no se almacenará como un dato independiente.

### 6.6. Anotaciones

- BookNest permitirá crear anotaciones generales y anotaciones asociadas a un Ejemplar.
- Las anotaciones generales funcionarán como notas personales simples o "post-it" del usuario y no estarán asociadas a ningún libro.
- Una anotación general podrá contener un título opcional y un contenido.
- Se registrará la fecha de creación y la fecha de última modificación de las anotaciones.
- El usuario podrá crear, modificar y eliminar sus anotaciones.
- Un Ejemplar podrá tener múltiples anotaciones asociadas.
- Las anotaciones de un Ejemplar serán independientes de sus Lecturas.
- Una anotación no deberá estar asociada a una Lectura específica.
- Si el usuario posee más de un Ejemplar correspondiente al mismo Libro, las anotaciones de cada Ejemplar se mantendrán independientes y no se compartirán automáticamente.
- La información relacionada específicamente con el estado físico de una copia podrá registrarse mediante la observación del Ejemplar, evitando utilizar las anotaciones para ese propósito.

### 6.7. Préstamos

- Cada Préstamo estará asociado a un Ejemplar físico específico.
- Un Ejemplar podrá tener múltiples Préstamos a lo largo del tiempo, conservando su historial.
- Un mismo Ejemplar solamente podrá tener un Préstamo activo a la vez.
- No será necesario que la persona que recibe el libro tenga una cuenta en BookNest.
- Para cada Préstamo se registrarán directamente el nombre y apellido de la persona que recibe el Ejemplar.
- El teléfono y el correo electrónico del destinatario serán datos opcionales.
- La fecha de realización del Préstamo será obligatoria.
- La fecha prevista de devolución será opcional.
- Al registrarse la devolución se almacenará la fecha real de devolución.
- Un Préstamo podrá encontrarse en estado ACTIVO, VENCIDO, DEVUELTO o CANCELADO.
- Si existe una fecha prevista de devolución y esta es superada mientras el Ejemplar continúa prestado, el Préstamo se considerará VENCIDO.
- Si no se indicó una fecha prevista de devolución, el Préstamo permanecerá ACTIVO hasta que se registre su devolución o cancelación.
- El estado CANCELADO permitirá anular un Préstamo registrado por error sin eliminar físicamente su historial.
- Un Ejemplar podrá ser prestado aunque no tenga una ubicación física asignada.
- Mientras un Ejemplar se encuentre prestado, dejará de contabilizarse dentro de la ocupación física de su Estante, liberando ese espacio para otro Ejemplar.
- La ubicación anterior podrá conservarse como referencia para el momento de la devolución, pero el espacio no quedará reservado.
- Al registrar la devolución, el usuario deberá decidir nuevamente la ubicación física del Ejemplar.
- El Ejemplar podrá regresar a su ubicación anterior únicamente si el Estante dispone de capacidad.
- Si la ubicación anterior ya no tiene capacidad disponible, el usuario deberá seleccionar otro Estante o dejar el Ejemplar sin ubicación asignada.
- No podrá darse de baja un Ejemplar mientras posea un Préstamo activo o vencido sin resolver.

### 6.8. Búsqueda, filtros y ordenamiento

- El usuario podrá buscar elementos de su colección por título, autor o ISBN.
- El catálogo permitirá aplicar filtros por género, autor, editorial y saga.
- También podrán aplicarse filtros según el estado de lectura del Ejemplar.
- Se podrá filtrar por Biblioteca y Estante.
- El sistema permitirá diferenciar entre Ejemplares con ubicación física asignada y Ejemplares sin ubicación.
- Se podrá filtrar según el estado de préstamo del Ejemplar.
- También podrá utilizarse el estado físico del Ejemplar como criterio de filtrado.
- Los resultados podrán ordenarse por título, autor y fecha de adquisición.
- Los filtros y criterios de ordenamiento podrán utilizarse para facilitar la localización y consulta de los Ejemplares de una colección.

### 6.9. Dashboard y estadísticas

- Cada usuario visualizará únicamente estadísticas correspondientes a su propia colección.
- El Dashboard podrá mostrar la cantidad total de Ejemplares registrados.
- Se mostrará un resumen de Ejemplares según sus estados de lectura: PENDIENTE, EN_CURSO, LEIDO y ABANDONADO.
- Se podrán visualizar la cantidad de Préstamos activos y vencidos.
- Se podrá mostrar la cantidad de Ejemplares con ubicación física asignada y sin ubicación.
- El Dashboard podrá presentar la distribución de la colección por género, autor, editorial y saga.
- Podrán mostrarse las anotaciones generales del usuario a modo de notas o "post-it".
- El Dashboard podrá incluir información sobre actividad reciente, como últimas adquisiciones o Lecturas registradas.
- Las estadísticas se obtendrán a partir de los datos existentes en el sistema, evitando almacenar de forma redundante valores que puedan calcularse.

### 6.10. Integración bibliográfica y portadas

- El usuario podrá registrar un Libro manualmente o realizar una búsqueda mediante ISBN.
- Cuando se utilice un ISBN, el backend consultará un servicio bibliográfico externo para intentar obtener los metadatos disponibles.
- Los datos recuperados podrán incluir título, autores, editorial, fecha de publicación, géneros, sinopsis y portada, según la disponibilidad de la API utilizada.
- La información obtenida automáticamente podrá ser revisada y completada por el usuario antes de incorporarse al sistema.
- Si la API devuelve una portada, BookNest la utilizará inicialmente como imagen del Libro.
- Si no existe una portada disponible, se mostrará una imagen genérica de BookNest.
- El usuario podrá cargar una portada propia o reemplazar la portada obtenida automáticamente.
- La ausencia de información en el servicio bibliográfico externo no impedirá la carga manual del Libro.

## 7. Alcance y decisiones de diseño del MVP

Con el objetivo de mantener un alcance viable para la primera versión de BookNest, se definieron las siguientes decisiones de diseño:

- BookNest estará orientado inicialmente a la gestión de libros físicos. La administración de libros digitales no formará parte del MVP.
- Las funcionalidades sociales, como amigos, recomendaciones entre usuarios, comentarios públicos o interacción entre perfiles, se consideran funcionalidades futuras.
- La recuperación de contraseña mediante correo electrónico se implementará en una etapa posterior.
- Los destinatarios de los préstamos no deberán registrarse como usuarios de BookNest ni se administrará una agenda independiente de contactos. Sus datos básicos se almacenarán directamente en cada Préstamo.
- No se conservará un historial de movimientos físicos de los Ejemplares entre Bibliotecas y Estantes. Solamente será relevante su ubicación actual.
- La capacidad de los Estantes se expresará en cantidad de Ejemplares y no mediante dimensiones físicas o medidas de los libros.
- No se reservará el espacio de un Estante cuando un Ejemplar se encuentre prestado.
- Los valores que puedan obtenerse mediante cálculos, como el promedio de calificaciones, la duración de una Lectura o la ocupación de un Estante, se calcularán a partir de los datos existentes siempre que resulte conveniente, evitando información redundante.
- Las notificaciones automáticas por correo electrónico, incluyendo recordatorios de préstamos vencidos, quedarán contempladas como una mejora futura.
- Las funcionalidades futuras podrán incorporarse de forma progresiva aprovechando la separación por módulos y capas definida para el sistema.