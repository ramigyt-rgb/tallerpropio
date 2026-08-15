# Owner OS / Taller Lab

App privada para pensar y gobernar el negocio, no para gestionar la reparación diaria de un auto.

## Qué incluye

- Sala de Mando del Dueño.
- Resultados reales mensuales.
- Tesis del negocio.
- Capital e inversión.
- Simulador.
- Objetivos económicos.
- Inteligencia de precios / baremo propio.
- Laboratorio comercial.
- Mapa de riesgos.
- Sociedad y negociación.
- Plan de independencia.
- Valuación.
- Diario de decisiones.
- Backup manual completo a ZIP/CSV.
- Login privado.
- Persistencia PostgreSQL externa.

## Arquitectura

`Streamlit -> SQLAlchemy -> PostgreSQL externo`

Recomendado: **Supabase Postgres**.

No existe SQLite ni archivo de base local. Si Streamlit se duerme, reinicia o redeploya, la base sigue en PostgreSQL.

---

# Instalación local

## 1. Crear proyecto

Descomprimir esta carpeta.

Abrir terminal dentro de `owner_os_taller_lab`.

## 2. Crear entorno

Windows:

```bash
py -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Instalar

```bash
pip install -r requirements.txt
```

## 4. Crear PostgreSQL en Supabase

1. Crear un proyecto en Supabase.
2. Abrir el proyecto.
3. Pulsar **Connect**.
4. Copiar el connection string compatible con tu entorno.
5. Para Streamlit Cloud suele convenir un **pooler** porque evita depender de conectividad IPv6.
6. Cambiar `[YOUR-PASSWORD]` por la contraseña real.
7. Agregar `?sslmode=require` si la cadena no lo trae.

Ejemplo conceptual:

```text
postgresql://usuario:password@host:puerto/postgres?sslmode=require
```

## 5. Crear contraseña privada

```bash
python tools/hash_password.py
```

Copiar el hash resultante.

## 6. Crear secrets local

Copiar:

`.streamlit/secrets.toml.example`

como:

`.streamlit/secrets.toml`

Editar:

```toml
DATABASE_URL = "..."

[auth]
username = "owner"
password_hash = "HASH_GENERADO"
display_name = "Owner"
```

**Nunca subir `secrets.toml` al repositorio.**

## 7. Ejecutar

```bash
streamlit run app.py
```

La primera conexión crea automáticamente todas las tablas y precarga:
- Fase 1: él $4 M / vos $2,67 M.
- Fase 2: él $6 M / vos $4 M.
- Fase 3: él $8 M / vos $5,33 M.
- matriz inicial de riesgos.
- dimensiones del plan de independencia.

No precarga movimientos de capital ni resultados reales, para no inventar hechos.

---

# Subir a GitHub + Streamlit Cloud

Subir al repo todo **menos** `.streamlit/secrets.toml`.

En Streamlit Community Cloud:

1. Crear app desde el repositorio.
2. Main file: `app.py`.
3. Ir a **Settings > Secrets**.
4. Pegar el contenido real de secrets.
5. Guardar y reiniciar la app.

Aunque Streamlit suspenda la interfaz, PostgreSQL es la fuente de verdad.

---

# Supabase / base de datos

`database.py` ejecuta `CREATE TABLE IF NOT EXISTS`, por lo que no hace falta correr SQL a mano.

También se incluye `setup_supabase.sql` para inspección, auditoría o creación manual desde Supabase SQL Editor.

## Backups

La app tiene un backup manual que genera un ZIP con CSV de todas las tablas.

Además, usar las opciones de backup que ofrezca tu proveedor PostgreSQL. El backup de aplicación y el backup del proveedor son capas distintas.

---

# Lógica central

## Capital expuesto

`Aportes tuyos - Recuperos tuyos`

Además separa:
- recuperable pendiente;
- costo hundido;
- aporte neto registrado del chapista.

## Simulador

Facturación:

`ticket promedio × cantidad de trabajos`

Costos variables:

`facturación × (materiales % + impuestos/comisiones %)`

Utilidad:

`facturación - variables - costos fijos`

Punto de equilibrio:

`costos fijos / margen de contribución`

Reparto:

solo sobre utilidad positiva.

## Objetivos

Calcula la utilidad mínima compatible con ambos objetivos:

`max(objetivo_vos / tu %, objetivo_él / % él)`

Luego:

`facturación requerida = utilidad necesaria / margen neto esperado`

y la divide por días productivos.

## Inteligencia de precios

Por trabajo calcula:
- costo directo;
- ganancia bruta;
- margen bruto;
- ingreso por hora;
- ganancia por hora;
- tasa de aceptación.

## Laboratorio comercial

Por canal calcula:
- CAC;
- tasa consulta -> presupuesto;
- tasa presupuesto -> cierre;
- facturación;
- ganancia atribuida;
- ROAS.

## Riesgos

`score = probabilidad × impacto`

Escala 1–5 por variable.

## Independencia

Promedio ponderado del avance de cada dimensión contra su objetivo.

## Valuación

Modelo interno:

`activos + utilidad mensual normalizada × múltiplo + intangibles - pasivos`

Luego aplica tu porcentaje.

No reemplaza una valuación profesional.

---

# Flujo de uso recomendado

1. Cargar **Capital e inversión**.
2. Escribir la **Tesis**.
3. Revisar los **Objetivos**.
4. Probar escenarios en **Simulador**.
5. Cada presupuesto: **Inteligencia de precios**.
6. Cada prueba de captación: **Laboratorio comercial**.
7. Una vez por mes: **Resultados reales**.
8. Una vez por semana: **Mapa de riesgos**.
9. Cada acuerdo verbal: **Sociedad y negociación**.
10. Cada decisión importante: **Diario de decisiones**.
11. Mensualmente: revisar **Plan de independencia**.
12. Trimestralmente: guardar una **Valuación**.

El objetivo es que, con el tiempo, la app se convierta en la memoria económica del negocio.
