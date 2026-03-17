# Yerevan Utility Outages Dashboard

Bilingual (English / Armenian) Streamlit dashboard that visualizes electricity and water utility outages across Yerevan's 12 districts.

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.54%2B-FF4B4B)

## Features

- **Language toggle** — Switch between English and Armenian (Հայերեն); all UI labels, filters, tooltips, chart legends, and table headers adapt accordingly
- **Interactive filters** — Date range, utility type, district, and address (sidebar)
- **KPI cards** — Total interruptions, latest interruption timestamp, most affected district, worst location (building-level)
- **Folium map** — One marker per location, colored by dominant outage kind (⚡ red / 💧 blue), with bilingual tooltips
- **Plotly charts** — Interruptions by district (bar, sorted descending) and trends over time (line)
- **Data table** — Sortable raw data with translated column headers and utility type values

## Prerequisites

- **Python ≥ 3.11**
- **[uv](https://docs.astral.sh/uv/)** package manager
- **PostgreSQL** database with the `vtar` schema (outages, addresses, cities, geocode_cache tables)

## Setup

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Configure database credentials** in `.streamlit/secrets.toml` (git-ignored):

   ```toml
   [connections.postgresql]
   host = "your-host"
   port = 5432
   database = "your-db"
   username = "your-user"
   password = "your-password"
   ```

3. **(Re)create the SQL view** (one-time, or after schema changes):

   ```bash
   python apply_schema_raw.py
   ```

## Running

```bash
uv run streamlit run app.py
```

## Project Structure

| File | Purpose |
|---|---|
| `app.py` | Main Streamlit app — sidebar, KPIs, map, charts, table, translations |
| `data.py` | Data layer — `fetch_raw_data()` (cached 1h) and `get_processed_data()` |
| `source_schema.sql` | SQL view `vtar.yerevan_outages` joining outages, addresses, cities, and geocode cache |
| `apply_schema_raw.py` | Apply the SQL view using `psycopg2` directly |
| `apply_schema.py` | Apply the SQL view using Streamlit's SQLAlchemy connection |
| `check_*.py` | Ad-hoc diagnostic scripts (DB connectivity, data shapes, geocoding) |
| `pyproject.toml` | Project metadata and dependencies (managed with `uv`) |

## Data Flow

```
PostgreSQL (vtar schema)
  → source_schema.sql view (maps ENA→Electricity, VJUR→Water)
    → data.py fetch_raw_data() (cached, aliases lat/lon → map_lat/map_lon)
      → get_processed_data() (appends building numbers to addresses)
        → app.py (filters, visualizes, translates)
```

## Key Conventions

- **Utility types** — Raw DB: `ENA` / `VJUR`; SQL view maps to `Electricity` / `Water`; app translates to Armenian when needed
- **Colors** — Electricity = `#ff4b4b` (red), Water = `#0096ff` (blue)
- **Bilingual columns** — `address_en` / `address_hy`, `district_en` / `district_hy` — selected at runtime via `lang_col()` helper
- **Map coordinates** — Aliased as `map_lat` / `map_lon` (not `latitude` / `longitude`)
- **District filtering** — SQL filters by Armenian name (`geocode_district_hy`); UI displays the language-appropriate column

