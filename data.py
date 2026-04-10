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

    # Pre-compute date column for fast filtering
    df["event_date"] = df["event_at"].dt.date

    return df
