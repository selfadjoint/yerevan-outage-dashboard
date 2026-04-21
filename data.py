import pandas as pd
import streamlit as st

_CACHE_TTL = 1800  # 30 minutes

# Earliest date the dashboard shows — also used as SQL filter
MIN_DATE = "2026-02-19"


@st.cache_data(ttl=_CACHE_TTL)
def fetch_raw_data():
    conn = st.connection("postgresql", type="sql")
    query = """
        SELECT
            event_at, kind, address_hy, address_en, building, 
            consumer_count, latitude as map_lat, longitude as map_lon, 
            geocode_district_hy as district_hy, geocode_district_en as district_en
        FROM vtar.yerevan_outages
        WHERE event_at >= :min_date
          AND geocode_district_hy IN ('Կենտրոն', 'Աջափնյակ', 'Ավան', 'Նոր Նորք', 
                                      'Էրեբունի', 'Մալաթիա-Սեբաստիա', 'Նուբարաշեն', 
                                      'Դավթաշեն', 'Շենգավիթ', 'Նորք Մարաշ', 'Արաբկիր', 'Քանաքեռ-Զեյթուն')
    """
    return conn.query(query, ttl=_CACHE_TTL, params={"min_date": MIN_DATE})


@st.cache_data(ttl=_CACHE_TTL)
def get_processed_data() -> pd.DataFrame:
    df = fetch_raw_data().copy()

    # Timezone conversion (done once in cache, not on every rerun)
    df["event_at"] = pd.to_datetime(df["event_at"])
    if df["event_at"].dt.tz is not None:
        df["event_at"] = df["event_at"].dt.tz_convert("Asia/Yerevan")
    else:
        df["event_at"] = df["event_at"].dt.tz_localize("UTC").dt.tz_convert("Asia/Yerevan")

    # Append building to address if available
    has_building = df["building"].notna() & (df["building"].astype(str).str.strip() != "")
    building_str = " " + df["building"].astype(str).str.strip()

    df.loc[has_building, "address_en"] = df.loc[has_building, "address_en"].astype(str) + building_str[has_building]
    df.loc[has_building, "address_hy"] = df.loc[has_building, "address_hy"].astype(str) + building_str[has_building]

    # Pre-compute boolean columns for fast aggregation
    df["is_elec"] = df["kind"] == "Electricity"
    df["is_water"] = df["kind"] == "Water"

    return df


@st.cache_data(ttl=_CACHE_TTL, show_spinner=False)
def build_map_groups(map_df: pd.DataFrame, addr_col: str, dist_col: str) -> pd.DataFrame:
    """One row per unique (lat, lon): aggregated counts + display fields.

    Cached so the groupby only reruns when the filtered slice actually changes.
    """
    grouped = (
        map_df.groupby([addr_col])
        .agg(
            map_lat=("map_lat", "first"),
            map_lon=("map_lon", "first"),
            district=(dist_col, "first"),
            last_event=("event_at", "max"),
            elec=("is_elec", "sum"),
            water=("is_water", "sum"),
        )
        .reset_index()
        .rename(columns={addr_col: "address"})
    )
    grouped["total"] = grouped["elec"] + grouped["water"]
    grouped["dominant"] = grouped["elec"].ge(grouped["water"]).map(
        {True: "Electricity", False: "Water"}
    )
    grouped["last_event_str"] = grouped["last_event"].dt.strftime("%Y-%m-%d %H:%M")
    return grouped


