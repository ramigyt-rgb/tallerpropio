# Owner OS / Taller Lab

Esta versión quedó corregida para que **puedas entrar a ver la app inmediatamente**.

## Modos

### 1) Modo demo/local
- no necesita `DATABASE_URL`
- no necesita login obligatorio
- entra sola
- trae datos demo cargados

### 2) Modo persistente
Más adelante, si querés guardar de verdad:
- agregás `DATABASE_URL`
- y automáticamente usa PostgreSQL externo

## Estética
Paleta gris claro, tonos de grises suaves, tarjetas blancas y look más limpio.

## Ejecutar local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy en Streamlit Cloud
Podés deployarla sin secrets: igual entra en demo/local.

## Persistencia real luego
```toml
DATABASE_URL = "postgresql://USUARIO:PASSWORD@HOST:PUERTO/postgres?sslmode=require"
```

## Login opcional
```bash
python tools/hash_password.py
```
y luego:
```toml
[auth]
username = "owner"
password_hash = "HASH_GENERADO"
display_name = "Owner"
```
