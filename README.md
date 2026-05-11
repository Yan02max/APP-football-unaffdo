# UNAFFDO - Gestión de Torneos de Fútbol Americano

App web para gestionar la temporada de la Liga UNAFFDO (República Dominicana).

## Instalación

```bash
pip install -r requirements.txt
```

## Inicializar la base de datos

```bash
python init_db.py
```

Para reiniciar desde cero:

```bash
python init_db.py --reset
```

## Ejecutar la app

```bash
streamlit run app.py
```

## Ejecutar smoke tests

```bash
python test_smoke.py
```

## Credenciales de prueba

| Usuario   | Contraseña  | Rol     | Permisos                            |
|-----------|-------------|---------|-------------------------------------|
| admin     | admin123    | admin   | Todo: resultados + gestión equipos  |
| arbitro1  | arbitro123  | arbitro | Solo registrar resultados           |

## Acceso público (sin login)

- Calendario completo organizado por domingo y bloque
- Tabla de clasificación

## Estructura del proyecto

```
app.py          - App Streamlit principal
auth.py         - Autenticación y helpers de permisos
config.yaml     - Usuarios y configuración de cookie
database.py     - Conexión SQLAlchemy
models.py       - Modelos Equipo, Temporada, Partido
tournament.py   - Generación de calendario y clasificación
init_db.py      - Script de inicialización de BD
test_smoke.py   - Smoke tests sin framework
requirements.txt
```

## Formato de torneo

- **6 equipos**: Sky Runners, Spartans, SD Sharks, Dagaz, Black Ops, Suicide Squads
- **Round-robin ida y vuelta**: 10 jornadas, 30 partidos
- **5 domingos**: 17 may, 24 may, 31 may, 7 jun, 14 jun 2026
- **2 bloques por domingo**: 3 partidos cada uno
- **Puntuación**: Victoria=3 pts, Empate=1 pt, Derrota=0 pts