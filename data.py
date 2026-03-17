import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)  # Cache DB fetch in Streamlit
def fetch_raw_data():
    conn = st.connection("postgresql", type="sql")
    query = """
        SELECT
            event_at, kind, address_hy, address_en, building, 
            consumer_count, latitude as map_lat, longitude as map_lon, 
            geocode_district_hy as district_hy, geocode_district_en as district_en
        FROM vtar.yerevan_outages
        WHERE geocode_district_hy IN ('Կենտրոն', 'Աջափնյակ', 'Ավան', 'Նոր Նորք', 
                                      'Էրեբունի', 'Մալաթիա-Սեբաստիա', 'Նուբարաշեն', 
                                      'Դավթաշեն', 'Շենգավիթ', 'Նորք Մարաշ', 'Արաբկիր', 'Քանաքեռ-Զեյթուն')
    """
    return conn.query(query)

def get_processed_data() -> pd.DataFrame:
    df = fetch_raw_data()
    
    # Append building to address if available
    has_building = df["building"].notna() & (df["building"].astype(str).str.strip() != "")
    building_str = " " + df["building"].astype(str).str.strip()
    
    df.loc[has_building, "address_en"] = df.loc[has_building, "address_en"].astype(str) + building_str[has_building]
    df.loc[has_building, "address_hy"] = df.loc[has_building, "address_hy"].astype(str) + building_str[has_building]
    
    return df
