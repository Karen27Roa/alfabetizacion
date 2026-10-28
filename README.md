# Interfaz programada — Diagnóstico de alfabetización mediática (Python + Django)

## Puesta en marcha
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate            # crea tablas y carga V1–V10 y las 18 preguntas (borrador)
python manage.py createsuperuser    # tu usuario administrador
python manage.py runserver          # http://127.0.0.1:8000
pytest                              # 29 pruebas
```
- **Estudiantes**: se registran solos en `/cuentas/registro/`.
- **Docentes**: el administrador los crea en `/admin/` → Usuarios → bloque "Perfil" → rol "Docente".
- **Rangos / semáforo / recomendaciones**: `/admin/` → Configuraciones de riesgo (cada cambio crea versión nueva).
- **PostgreSQL**: define POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST; si no, usa SQLite.

## Pendiente ANTES de usarlo con estudiantes reales
1. Reemplazar las 18 preguntas por las del formulario original (`/admin/instrumento/pregunta/`). El PDF no las trae.
   Deben estar redactadas de modo que 5 = mayor riesgo, porque el puntaje es la suma simple (18–90).
2. Definir `DOMINIOS_PERMITIDOS` en config/settings.py con el dominio de la universidad.

## Mapa PDF → código
| Requisito | Dónde |
|---|---|
| RF-01 cuestionario 18 preguntas | instrumento/views.py, templates/instrumento/cuestionario.html |
| RF-02/03 puntaje y nivel | puntaje/motor.py (Python puro) |
| RF-04 resultado + recomendación | templates/instrumento/resultado.html |
| RF-05/06 dashboard y filtros | reportes/, templates/reportes/ (HTMX + Chart.js) |
| RF-07 exportar | reportes/views.py (Excel con openpyxl) |
| RF-08 rangos configurables | configuracion/ |
| RF-09 repetir sin sobrescribir | instrumento/services.py |
| RF-11 roles | cuentas/ |
