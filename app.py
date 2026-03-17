import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from data import get_processed_data

# App Configuration
st.set_page_config(page_title="Yerevan Utility Outages", page_icon="⚡", layout="wide")

# Apply custom CSS for a modern look
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e2f;
        padding: 18px 16px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin-bottom: 20px;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        gap: 4px;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #ff4b4b;
        line-height: 1.2;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .metric-detail {
        font-size: 0.85rem;
        font-weight: 500;
        color: #c0c0d0;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #707088;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔌 Yerevan Utility Outages")
st.markdown("Monitor electricity and water outages across different districts in Yerevan.")

# Loading Data
with st.spinner("Fetching and enriching data..."):
    df = get_processed_data()
    print("DEBUG APP.PY LOG:", df[["address_en", "building"]].dropna(subset=["building"]).head(3))

# Remove empty locations for the map, but keep them generally? Actually we need to filter
df["event_at"] = pd.to_datetime(df["event_at"])
df["event_at"] = df["event_at"].dt.tz_convert('Asia/Yerevan') if df["event_at"].dt.tz is not None else df[
    "event_at"].dt.tz_localize('UTC').dt.tz_convert('Asia/Yerevan')

# ----------------- #
#     SIDEBAR       #
# ----------------- #
st.sidebar.header("Filters")

# Date Filter
min_date = df["event_at"].min().date()
max_date = df["event_at"].max().date()
selected_dates = st.sidebar.date_input("Date Range", value=("2026-02-19", max_date), min_value=min_date,
                                       max_value=max_date)

# Utility Filter
available_kinds = df["kind"].dropna().unique()
kinds = st.sidebar.multiselect("Utility Type", options=sorted(list(available_kinds)),
                               default=sorted(list(available_kinds)))

# District Filter
available_districts = df["district_en"].dropna().unique()
districts = st.sidebar.multiselect("District", options=sorted(list(available_districts)))

# Address Filter
available_addresses = df["address_en"].dropna().unique()
addresses = st.sidebar.multiselect(
    "Address",
    options=sorted(list(available_addresses)),
    placeholder="Type to search addresses..."
)

# Apply Filters
mask = pd.Series(True, index=df.index)

if len(selected_dates) == 2:
    start_date, end_date = selected_dates
    mask &= (df["event_at"].dt.date >= start_date) & (df["event_at"].dt.date <= end_date)
elif len(selected_dates) == 1:
    mask &= (df["event_at"].dt.date == selected_dates[0])

if kinds:
    mask &= df["kind"].isin(kinds)

if districts:
    mask &= df["district_en"].isin(districts)

if addresses:
    mask &= df["address_en"].isin(addresses)

filtered_df = df[mask]

# ----------------- #
#      KPIs         #
# ----------------- #
col1, col2, col3, col4 = st.columns(4)

total_events = len(filtered_df)
total_electricity = len(filtered_df[filtered_df["kind"] == "Electricity"])
total_water = len(filtered_df[filtered_df["kind"] == "Water"])

if total_events > 0:
    latest_outage = filtered_df["event_at"].max().strftime('%Y-%m-%d %H:%M:%S')
    top_district = filtered_df["district_en"].mode()
    top_district_name = top_district.iloc[0] if not top_district.empty else "N/A"
    worst_candidates = filtered_df[filtered_df["building"].notna() & (filtered_df["building"].astype(str).str.strip() != "")]
    if not worst_candidates.empty:
        worst = worst_candidates.groupby("address_en").agg(
            total=("kind", "count"),
            elec=("kind", lambda x: (x == "Electricity").sum()),
            water=("kind", lambda x: (x == "Water").sum()),
        ).sort_values("total", ascending=False).iloc[0]
        worst_address = worst.name
        worst_label = f"{int(worst['total'])} times (⚡ {int(worst['elec'])} | 💧 {int(worst['water'])})"
    else:
        worst_address = "N/A"
        worst_label = ""
else:
    latest_outage = "N/A"
    top_district_name = "N/A"
    worst_address = "N/A"
    worst_label = ""

with col1:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{total_events:,}</div>
        <div class="metric-detail">⚡ {total_electricity:,} &nbsp;|&nbsp; 💧 {total_water:,}</div>
        <div class="metric-label">Total Interruptions</div>
    </div>
    ''', unsafe_allow_html=True)
with col2:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{latest_outage}</div>
        <div class="metric-label">Latest Interruption</div>
    </div>
    ''', unsafe_allow_html=True)
with col3:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{top_district_name}</div>
        <div class="metric-label">Most Affected District</div>
    </div>
    ''', unsafe_allow_html=True)
with col4:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{worst_address}</div>
        <div class="metric-detail">{worst_label}</div>
        <div class="metric-label">Worst Location</div>
    </div>
    ''', unsafe_allow_html=True)

# ----------------- #
#      MAP          #
# ----------------- #
st.subheader("🗺️ Outages Map")

map_data = filtered_df.dropna(subset=["map_lat", "map_lon"])
map_data = map_data[(map_data["map_lat"] != 0) & (map_data["map_lon"] != 0)]  # sanitize

if not map_data.empty:
    # Create Folium Map
    m = folium.Map(location=[map_data["map_lat"].mean(), map_data["map_lon"].mean()], zoom_start=11)

    # Sort by event_at descending to get latest dates first
    map_data = map_data.sort_values("event_at", ascending=False)

    # Group by location (one marker per address) with per-kind counts
    grouped = map_data.groupby(["map_lat", "map_lon"]).agg(
        address_en=("address_en", lambda x: "<br/>".join(sorted(set(x.dropna()))[:3]) + (
            "<br/>... and more" if len(set(x.dropna())) > 3 else "")),
        district=("district_en", "first"),
        last_event=("event_at", "max"),
        electricity_count=("kind", lambda x: (x == "Electricity").sum()),
        water_count=("kind", lambda x: (x == "Water").sum()),
    ).reset_index()

    for idx, row in grouped.iterrows():
        # Color by the dominant outage kind at this location
        color = "red" if row["electricity_count"] >= row["water_count"] else "blue"
        dominant_kind = "Electricity" if row["electricity_count"] >= row["water_count"] else "Water"

        last_event_str = row["last_event"].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row["last_event"]) else "N/A"

        tooltip_html = (
            f"<b>Address:</b> {row.get('address_en', 'N/A')} <br/> "
            f"<b>District:</b> {row.get('district', 'N/A')} <br/> "
            f"<b>Interruptions:</b> ⚡ {row['electricity_count']} | 💧 {row['water_count']} <br/> "
            f"<b>Latest Interruption:</b> {last_event_str}"
        )

        folium.CircleMarker(
            location=[row["map_lat"], row["map_lon"]],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            tooltip=tooltip_html
        ).add_to(m)

    st_folium(m, width="100%", height=500, returned_objects=[])
else:
    st.info("No coordinate data available for the selected filters.")

# ----------------- #
#     CHARTS        #
# ----------------- #
st.markdown("---")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 Interruptions by District")
    if not filtered_df.empty:
        dist_counts = filtered_df.groupby(["district_en", "kind"]).size().reset_index(name="count")
        district_order = dist_counts.groupby("district_en")["count"].sum().sort_values(ascending=False).index.tolist()
        fig1 = px.bar(dist_counts, x="district_en", y="count", color="kind",
                      category_orders={"district_en": district_order},
                      color_discrete_map={"Electricity": "#ff4b4b", "Water": "#0096ff"},
                      labels={"district_en": "District", "count": "Affected Addresses"})
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write("No data")

with col_chart2:
    st.subheader("📈 Interruption Trends Over Time")
    if not filtered_df.empty:
        # Resample by day
        timeline_df = filtered_df.copy()
        timeline_df["date"] = timeline_df["event_at"].dt.date
        time_counts = timeline_df.groupby(["date", "kind"]).size().reset_index(name="count")
        fig2 = px.line(time_counts, x="date", y="count", color="kind",
                       color_discrete_map={"Electricity": "#ff4b4b", "Water": "#0096ff"},
                       labels={"date": "Date", "count": "Affected Addresses"},
                       markers=True)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.write("No data")

# ----------------- #
#       TABLE       #
# ----------------- #
st.subheader("📋 Raw Data Explorer")
cols_to_show = ["event_at", "kind", "district_en", "address_en", "consumer_count", "map_lat", "map_lon"]
# Check if columns exist
cols_available = [c for c in cols_to_show if c in filtered_df.columns]
st.dataframe(filtered_df[cols_available].sort_values("event_at", ascending=False), use_container_width=True)
