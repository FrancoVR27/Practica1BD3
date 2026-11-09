# CRUD Cassandra / AstraDB + Flask

Objetivo: comprobar la velocidad y capacidad de Cassandra para manejar escrituras simultáneas sin bloquearse.

## 1. Crear la BD (consola CQL de AstraDB)

```sql
CREATE KEYSPACE IF NOT EXISTS app_keyspace
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};

USE app_keyspace;

CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY,
    nombre text,
    fecha timestamp
);
```

> Nota: la aplicación también crea el keyspace y la tabla automáticamente al conectar si no existen.

## 2. Requisitos

- Python 3.9+
- Cuenta en [AstraDB](https://astra.datastax.com) con una base de datos creada.
- `secure-connect-db.zip` (bundle de conexión seguro de AstraDB).
- Client ID y Client Secret (Tokens de AstraDB).

## 3. Ejecutar en local

```bash
# Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno y editar con tus credenciales de AstraDB
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac

# Ejecutar
python app.py
```

Abrir http://localhost:5000

## 4. Desplegar en Render

1. Sube este proyecto a GitHub.
2. En [Render](https://render.com), crea un **Web Service** conectando el repositorio.
3. Configura:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Añade las variables de entorno en Render (Environment):
   - `ASTRA_DB_SECURE_CONNECT_BUNDLE` → sube el archivo `secure-connect-db.zip` al repositorio y pon su nombre (o usa Disk/secret según prefieras).
   - `ASTRA_DB_CLIENT_ID`
   - `ASTRA_DB_CLIENT_SECRET`
   - `ASTRA_DB_KEYSPACE` = `app_keyspace`
   - `SECRET_KEY`
5. Despliega y obtén la URL pública.

### Nota sobre el bundle de conexión en Render
El archivo `secure-connect-db.zip` debe estar accesible por la app. Opciones:
- Inclúelo en el repositorio y usa `ASTRA_DB_SECURE_CONNECT_BUNDLE=secure-connect-db.zip`.
- O bien, configúralo como disco/secret en Render y ajusta la variable.

## 5. Prueba de carga simultánea

1. Comparte la URL pública con tus compañeros.
2. Pídeles que entren y registren su nombre **exactamente al mismo tiempo**.
3. Accede a `/usuarios` (o ejecuta en CQL):

```sql
SELECT COUNT(*) FROM app_keyspace.usuarios;
-- o
SELECT * FROM app_keyspace.usuarios;
```

Cassandra acepta escrituras concurrentes sin bloquearse; verifica que todos los nombres queden registrados.

## Estructura

```
app.py              # Flask + conexión a AstraDB (cassandra-driver)
requirements.txt    # dependencias
Procfile            # comando de inicio para Render
.env.example        # variables de entorno (copiar a .env)
templates/
  index.html        # formulario de nombre
  usuarios.html     # listado y conteo
```
