import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from datetime import timedelta
from folium.plugins import FastMarkerCluster
from streamlit.components.v1 import html as st_html
from data import get_processed_data, MIN_DATE


# ---- Translations ---- #
TRANSLATIONS = {
    "en": {
        "title": "\U0001f50c Yerevan Utility Outages",
        "subtitle": "Monitor electricity and water outages across different districts in Yerevan.",
        "loading": "Fetching and enriching data...",
        "language": "Language",
        "filters": "Filters",
        "date_range": "Date Range",
        "utility_type": "Utility Type",
        "district": "District",
        "address": "Address",
        "address_placeholder": "Type to search addresses...",
        "total_interruptions": "Total Interruptions",
        "latest_interruption": "Latest Interruption",
        "most_affected_district": "Most Affected District",
        "worst_location": "Worst Location",
        "times": "times",
        "map_header": "\U0001f5fa\ufe0f Outages Map",
        "map_no_data": "No coordinate data available for the selected filters.",
        "interruptions": "Interruptions",
        "chart_by_district": "\U0001f4ca Interruptions by District",
        "chart_trends": "\U0001f4c8 Interruption Trends Over Time",
        "count_label": "Interruptions",
        "date": "Date",
        "no_data": "No data",
        "table_header": "\U0001f4cb Raw Data Explorer",
        "electricity": "Electricity",
        "water": "Water",
        "tooltip_address": "Address",
        "tooltip_district": "District",
        "tooltip_interruptions": "Interruptions",
        "tooltip_latest": "Latest Interruption",
        "col_event_at": "Event Datetime",
        "col_kind": "Utility Type",
        "col_district": "District",
        "col_address": "Address",
        "col_consumer_count": "Consumer Count",
        "col_lat": "Latitude",
        "col_lon": "Longitude",
        "disclaimer": "**Data sources:** Electricity outage data from [ENA](https://www.ena.am), water outage data from [Veolia Jur](https://t.me/s/VeoliaJur). "
                       "District and coordinates are obtained via geocoding and may contain inaccuracies. "
                       "This dashboard is provided for informational purposes only — the data is not guaranteed to be 100% accurate or complete.",
    },
    "hy": {
        "title": "\U0001f50c \u0535\u0580\u0587\u0561\u0576\u056b \u056f\u0578\u0574\u0578\u0582\u0576\u0561\u056c \u0568\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580",
        "subtitle": "\u0540\u0565\u057f\u0587\u0565\u056c \u0567\u056c\u0565\u056f\u057f\u0580\u0561\u056f\u0561\u0576\u0578\u0582\u0569\u0575\u0561\u0576 \u0587 \u057b\u0580\u0561\u0574\u0561\u057f\u0561\u056f\u0561\u0580\u0561\u0580\u0574\u0561\u0576 \u0568\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580\u0568 \u0535\u0580\u0587\u0561\u0576\u056b \u057f\u0561\u0580\u0562\u0565\u0580 \u0569\u0561\u0572\u0561\u0574\u0561\u057d\u0565\u0580\u0578\u0582\u0574:",
        "loading": "\u054f\u057e\u0575\u0561\u056c\u0576\u0565\u0580\u056b \u0562\u0565\u057c\u0576\u0578\u0582\u0574...",
        "language": "\u053c\u0565\u0566\u0578\u0582",
        "filters": "\u0556\u056b\u056c\u057f\u0580\u0565\u0580",
        "date_range": "\u0531\u0574\u057d\u0561\u0569\u057e\u056b \u0574\u056b\u057b\u0561\u056f",
        "utility_type": "\u053e\u0561\u057c\u0561\u0575\u0578\u0582\u0569\u0575\u0561\u0576 \u057f\u0565\u057d\u0561\u056f",
        "district": "\u0539\u0561\u0572\u0561\u0574\u0561\u057d",
        "address": "\u0540\u0561\u057d\u0581\u0565",
        "address_placeholder": "\u0553\u0576\u057f\u0580\u0565\u056c \u0570\u0561\u057d\u0581\u0565\u0576\u0565\u0580...",
        "total_interruptions": "\u0538\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580\u056b \u0584\u0561\u0576\u0561\u056f",
        "latest_interruption": "\u054e\u0565\u0580\u057b\u056b\u0576 \u0568\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0568",
        "most_affected_district": "\u0531\u0574\u0565\u0576\u0561\u057f\u0578\u0582\u057a\u057d \u0569\u0561\u0572\u0561\u0574\u0561\u057d\u0568",
        "worst_location": "\u0531\u0574\u0565\u0576\u0561\u057e\u0561\u057f \u057e\u0561\u0575\u0580\u0568",
        "times": "\u0561\u0576\u0563\u0561\u0574",
        "map_header": "\U0001f5fa\ufe0f \u0538\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580\u056b \u0584\u0561\u0580\u057f\u0565\u0566",
        "map_no_data": "\u0538\u0576\u057f\u0580\u057e\u0561\u056e \u0566\u057f\u056b\u0579\u0576\u0565\u0580\u056b \u0570\u0561\u0574\u0561\u0580 \u057f\u057e\u0575\u0561\u056c\u0576\u0565\u0580 \u0579\u056f\u0561\u0576:",
        "interruptions": "\u0538\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580",
        "chart_by_district": "\U0001f4ca \u0538\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580\u0568 \u0568\u057d\u057f \u0569\u0561\u0572\u0561\u0574\u0561\u057d\u0565\u0580\u056b",
        "chart_trends": "\U0001f4c8 \u0538\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580\u056b \u0574\u056b\u057f\u0578\u0582\u0574\u0576\u0565\u0580\u0568",
        "count_label": "\u0538\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580",
        "date": "\u0531\u0574\u057d\u0561\u0569\u056b\u057e",
        "no_data": "\u054f\u057e\u0575\u0561\u056c\u0576\u0565\u0580 \u0579\u056f\u0561\u0576",
        "table_header": "\U0001f4cb \u054f\u057e\u0575\u0561\u056c\u0576\u0565\u0580\u056b \u0561\u0572\u0575\u0578\u0582\u057d\u0561\u056f",
        "electricity": "\u0537\u056c\u0565\u056f\u057f\u0580\u0561\u056f\u0561\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576",
        "water": "\u054b\u0578\u0582\u0580",
        "tooltip_address": "\u0540\u0561\u057d\u0581\u0565",
        "tooltip_district": "\u0539\u0561\u0572\u0561\u0574\u0561\u057d",
        "tooltip_interruptions": "\u0538\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580",
        "tooltip_latest": "\u054e\u0565\u0580\u057b\u056b\u0576 \u0568\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0568",
        "col_event_at": "\u0531\u0574\u057d\u0561\u0569\u056b\u057e",
        "col_kind": "\u053e\u0561\u057c\u0561\u0575\u0578\u0582\u0569\u0575\u0561\u0576 \u057f\u0565\u057d\u0561\u056f",
        "col_district": "\u0539\u0561\u0572\u0561\u0574\u0561\u057d",
        "col_address": "\u0540\u0561\u057d\u0581\u0565",
        "col_consumer_count": "\u054d\u057a\u0561\u057c\u0578\u0572\u0576\u0565\u0580\u056b \u0584\u0561\u0576\u0561\u056f",
        "col_lat": "\u053c\u0561\u0575\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576",
        "col_lon": "\u0535\u0580\u056f\u0561\u0575\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576",
        "disclaimer": "**\u054f\u057e\u0575\u0561\u056c\u0576\u0565\u0580\u056b \u0561\u0572\u0562\u0575\u0578\u0582\u0580\u0576\u0565\u0580\u055d** \u0537\u056c\u0565\u056f\u057f\u0580\u0561\u056f\u0561\u0576\u0578\u0582\u0569\u0575\u0561\u0576 \u0568\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580\u056b \u057f\u057e\u0575\u0561\u056c\u0576\u0565\u0580\u0568\u055d [ENA](https://www.ena.am), \u057b\u0580\u0561\u0574\u0561\u057f\u0561\u056f\u0561\u0580\u0561\u0580\u0574\u0561\u0576 \u0568\u0576\u0564\u0570\u0561\u057f\u0578\u0582\u0574\u0576\u0565\u0580\u056b \u057f\u057e\u0575\u0561\u056c\u0576\u0565\u0580\u0568\u055d [\u054e\u0565\u0578\u056c\u056b\u0561 \u054b\u0578\u0582\u0580](https://t.me/s/VeoliaJur): "
                       "\u0539\u0561\u0572\u0561\u0574\u0561\u057d\u0576 \u0578\u0582 \u056f\u0578\u0578\u0580\u0564\u056b\u0576\u0561\u057f\u0576\u0565\u0580\u0568 \u057d\u057f\u0561\u0581\u057e\u0561\u056e \u0565\u0576 \u0563\u0565\u0578\u056f\u0578\u0564\u0561\u057e\u0578\u0580\u0574\u0561\u0576 \u0574\u056b\u057b\u0578\u0581\u0578\u057e \u0587 \u056f\u0561\u0580\u0578\u0572 \u0565\u0576 \u057a\u0561\u0580\u0578\u0582\u0576\u0561\u056f\u0565\u056c \u0561\u0576\u0573\u0577\u057f\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0576\u0565\u0580: "
                       "\u054d\u0578\u0582\u0575\u0576 \u057e\u0561\u0570\u0561\u0576\u0561\u056f\u0568 \u0576\u0561\u056d\u0561\u057f\u0565\u057d\u057e\u0561\u056e \u0567 \u0574\u056b\u0561\u0575\u0576 \u057f\u0565\u0572\u0565\u056f\u0561\u057f\u057e\u0561\u056f\u0561\u0576 \u0576\u057a\u0561\u057f\u0561\u056f\u0576\u0565\u0580\u0578\u057e \u2014 \u057f\u057e\u0575\u0561\u056c\u0576\u0565\u0580\u056b 100% \u0573\u0577\u057f\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0568 \u0587 \u0561\u0574\u0562\u0578\u0572\u057b\u0561\u056f\u0561\u0576\u0578\u0582\u0569\u0575\u0578\u0582\u0576\u0568 \u0565\u0580\u0561\u0577\u056d\u0561\u057e\u0578\u0580\u057e\u0561\u056e \u0579\u0567:",
    },
}


# Map English kind values to translation keys
KIND_KEYS = {"Electricity": "electricity", "Water": "water"}


def t(key):
    """Return translated string for current language."""
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS[lang].get(key, key)


def lang_col(base):
    """Return the language-specific column name: 'address' -> 'address_en' or 'address_hy'."""
    lang = st.session_state.get("lang", "en")
    return f"{base}_{lang}"


def kind_label(kind_en):
    """Translate a kind value like 'Electricity' to the current language."""
    return t(KIND_KEYS.get(kind_en, kind_en))


# App Configuration
st.set_page_config(page_title="Yerevan Utility Outages", page_icon="\u26a1", layout="wide")

# Apply custom CSS for a modern look
st.markdown(
    """
<style>
    .metric-card {
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 18px 16px;
        border-radius: 10px;
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
        color: inherit;
        opacity: 0.7;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .metric-label {
        font-size: 0.8rem;
        color: inherit;
        opacity: 0.5;
        margin-top: 2px;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Language selector (must be before any translated content)
lang_options = {"English": "en", "\u0540\u0561\u0575\u0565\u0580\u0565\u0576": "hy"}
selected_lang_label = st.sidebar.radio(
    "\U0001f310 Language / \u053c\u0565\u0566\u0578\u0582",
    options=list(lang_options.keys()),
    horizontal=True,
    key="lang_radio",
)
st.session_state["lang"] = lang_options[selected_lang_label]
st.title(t("title"))
st.markdown(t("subtitle"))

# Loading Data
with st.spinner(t("loading")):
    df = get_processed_data()

# Resolve language-dependent column names
addr_col = lang_col("address")
dist_col = lang_col("district")

# ----------------- #
#     SIDEBAR       #
# ----------------- #
st.sidebar.header(t("filters"))

# Date Filter
min_date = pd.Timestamp(MIN_DATE).date()
today = pd.Timestamp.now("Asia/Yerevan").date()
max_date = max(df["event_at"].max().date(), today)
default_start = max(today - timedelta(days=30), min_date)
selected_dates = st.sidebar.date_input(
    t("date_range"), value=(default_start, max_date), min_value=min_date, max_value=max_date
)

# Utility Filter — display translated labels, map back to English for filtering
available_kinds_en = sorted(df["kind"].dropna().unique().tolist())
kind_display_to_en = {kind_label(k): k for k in available_kinds_en}
selected_kind_labels = st.sidebar.multiselect(
    t("utility_type"),
    options=list(kind_display_to_en.keys()),
    default=list(kind_display_to_en.keys()),
)
kinds = [kind_display_to_en[lbl] for lbl in selected_kind_labels]

# District Filter
available_districts = sorted(df[dist_col].dropna().unique().tolist())
districts = st.sidebar.multiselect(t("district"), options=available_districts)

# Address Filter — text search instead of 54K-option multiselect
address_search = st.sidebar.text_input(
    t("address"),
    placeholder=t("address_placeholder"),
)
# Scope address matches to already-selected districts (if any)
if address_search:
    search_base = df[df[dist_col].isin(districts)][addr_col] if districts else df[addr_col]
    matching = sorted(search_base[search_base.str.contains(address_search, case=False, na=False)].unique().tolist())
    addresses = st.sidebar.multiselect(
        f"🔍 {len(matching)} matches",
        options=matching[:200],
        default=matching[:200] if len(matching) <= 10 else [],
    )
else:
    addresses = []

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
    mask &= df[dist_col].isin(districts)

if addresses:
    mask &= df[addr_col].isin(addresses)

filtered_df = df[mask]

# Pre-compute kind display column once (reused by charts and table)
_kind_display_map = {k: kind_label(k) for k in ["Electricity", "Water"]}

# ----------------- #
#      KPIs         #
# ----------------- #
col1, col2, col3, col4 = st.columns(4)
total_events = len(filtered_df)
total_electricity = int(filtered_df["is_elec"].sum())
total_water = int(filtered_df["is_water"].sum())
if total_events > 0:
    latest_outage = filtered_df["event_at"].max().strftime('%Y-%m-%d %H:%M:%S')
    top_district = filtered_df[dist_col].mode()
    top_district_name = top_district.iloc[0] if not top_district.empty else "N/A"
    worst_candidates = filtered_df[filtered_df["building"].notna() & (filtered_df["building"].astype(str).str.strip() != "")]
    if not worst_candidates.empty:
        worst = worst_candidates.groupby(addr_col).agg(
            total=("kind", "count"),
            elec=("is_elec", "sum"),
            water=("is_water", "sum"),
        ).sort_values("total", ascending=False).iloc[0]
        worst_address = worst.name
        worst_label = f"{int(worst['total'])} {t('times')} (⚡ {int(worst['elec'])} | 💧 {int(worst['water'])})"
    else:
        worst_address = "N/A"
        worst_label = ""
else:
    latest_outage = "N/A"
    top_district_name = "N/A"
    worst_address = "N/A"
    worst_label = ""
with col1:
    st.markdown(
        f'''
    <div class="metric-card">
        <div class="metric-value">{total_events:,}</div>
        <div class="metric-detail">⚡ {total_electricity:,} &nbsp;|&nbsp; 💧 {total_water:,}</div>
        <div class="metric-label">{t("total_interruptions")}</div>
    </div>
    ''',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'''
    <div class="metric-card">
        <div class="metric-value">{latest_outage}</div>
        <div class="metric-label">{t("latest_interruption")}</div>
    </div>
    ''',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'''
    <div class="metric-card">
        <div class="metric-value">{top_district_name}</div>
        <div class="metric-label">{t("most_affected_district")}</div>
    </div>
    ''',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'''
    <div class="metric-card">
        <div class="metric-value">{worst_address}</div>
        <div class="metric-detail">{worst_label}</div>
        <div class="metric-label">{t("worst_location")}</div>
    </div>
    ''',
        unsafe_allow_html=True,
    )

# ----------------- #
#     CHARTS        #
# ----------------- #
col_chart1, col_chart2 = st.columns(2)
# Build translated color map for chart legends
translated_color_map = {kind_label("Electricity"): "#ff4b4b", kind_label("Water"): "#0096ff"}
with col_chart1:
    st.subheader(t("chart_by_district"))
    if not filtered_df.empty:
        kind_display = filtered_df["kind"].map(_kind_display_map)
        dist_counts = (
            pd.DataFrame({dist_col: filtered_df[dist_col], "kind_display": kind_display})
            .groupby([dist_col, "kind_display"]).size().reset_index(name="count")
        )
        district_order = dist_counts.groupby(dist_col)["count"].sum().sort_values(ascending=False).index.tolist()
        fig1 = px.bar(
            dist_counts,
            x=dist_col,
            y="count",
            color="kind_display",
            category_orders={dist_col: district_order},
            color_discrete_map=translated_color_map,
            labels={dist_col: t("district"), "count": t("count_label"), "kind_display": t("utility_type")},
        )
        fig1.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write(t("no_data"))
with col_chart2:
    st.subheader(t("chart_trends"))
    if not filtered_df.empty:
        time_counts = (
            pd.DataFrame({"date": filtered_df["event_at"].dt.date, "kind_display": filtered_df["kind"].map(_kind_display_map)})
            .groupby(["date", "kind_display"]).size().reset_index(name="count")
        )
        fig2 = px.line(
            time_counts,
            x="date",
            y="count",
            color="kind_display",
            color_discrete_map=translated_color_map,
            labels={"date": t("date"), "count": t("count_label"), "kind_display": t("utility_type")},
            markers=True,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.write(t("no_data"))

# ----------------- #
#      MAP          #
# ----------------- #
st.subheader(t("map_header"))

map_data = filtered_df.dropna(subset=["map_lat", "map_lon"])
map_data = map_data[(map_data["map_lat"] != 0) & (map_data["map_lon"] != 0)]

if not map_data.empty:
    m = folium.Map(location=[map_data["map_lat"].mean(), map_data["map_lon"].mean()], zoom_start=11)
    map_data = map_data.sort_values("event_at", ascending=False)

    # Pre-compute boolean columns for vectorized aggregation
    grouped = map_data.groupby(["map_lat", "map_lon"]).agg(
        address=(addr_col, lambda x: "<br/>".join(sorted(set(x.dropna()))[:3]) + (
            "<br/>... and more" if len(set(x.dropna())) > 3 else "")),
        district=(dist_col, "first"),
        last_event=("event_at", "max"),
        electricity_count=("is_elec", "sum"),
        water_count=("is_water", "sum"),
    ).reset_index()

    # Vectorized color assignment using numpy
    grouped["color"] = np.where(
        grouped["electricity_count"] >= grouped["water_count"], "red", "blue"
    )
    grouped["last_event_str"] = grouped["last_event"].dt.strftime('%Y-%m-%d %H:%M:%S').fillna("N/A")
    lbl_addr = t("tooltip_address")
    lbl_dist = t("tooltip_district")
    lbl_intr = t("tooltip_interruptions")
    lbl_last = t("tooltip_latest")
    grouped["tooltip"] = (
        "<b>" + lbl_addr + ":</b> " + grouped["address"].fillna("N/A") + " <br/> "
        "<b>" + lbl_dist + ":</b> " + grouped["district"].fillna("N/A") + " <br/> "
        "<b>" + lbl_intr + ":</b> ⚡ " + grouped["electricity_count"].astype(str) +
        " | 💧 " + grouped["water_count"].astype(str) + " <br/> "
        "<b>" + lbl_last + ":</b> " + grouped["last_event_str"]
    )

    # Cluster markers via FastMarkerCluster — sends a single JSON array
    # instead of generating one JS object per marker.
    cluster_data = grouped[["map_lat", "map_lon", "color", "tooltip"]].values.tolist()

    callback = """\
function (row) {
    var marker = L.circleMarker(new L.LatLng(row[0], row[1]), {
        radius: 6,
        color: row[2],
        fill: true,
        fillColor: row[2],
        fillOpacity: 0.7
    });
    marker.bindTooltip(row[3]);
    return marker;
}"""

    FastMarkerCluster(
        data=cluster_data,
        callback=callback,
        disableClusteringAtZoom=15,
        maxClusterRadius=40,
        spiderfyOnMaxZoom=False,
    ).add_to(m)

    # Render as static HTML — much faster than st_folium on reruns
    map_html = m._repr_html_()
    # Folium's _repr_html_() uses a responsive padding-bottom wrapper that
    # makes the map shorter than the iframe on narrow viewports.  Override it
    # with CSS so the map always fills the full iframe, then shrink the
    # Streamlit container on mobile via JS injected into the parent document.
    _MAP_HEIGHT_DESKTOP = 480
    _MAP_HEIGHT_MOBILE = 350
    responsive_wrapper = f"""\
<style>
  /* Make folium content fill the entire st_html iframe */
  html, body {{ margin:0; padding:0; height:100%; overflow:hidden; }}
  body > div {{ width:100% !important; height:100% !important; }}
  body > div > div {{
      position:relative !important;
      width:100% !important;
      height:100% !important;
      padding-bottom:0 !important;
  }}
  body > div > div > iframe {{
      position:absolute; width:100%; height:100%;
  }}
</style>
{map_html}
<script>
(function() {{
    var isMobile = window.innerWidth <= 768;
    if (!isMobile) return;
    var h = {_MAP_HEIGHT_MOBILE};
    var frame = window.frameElement;
    if (frame) {{
        var parentDoc = frame.ownerDocument;
        var style = parentDoc.createElement('style');
        style.textContent = '.stElementContainer:has(iframe) {{ height: ' + h + 'px !important; flex: 0 0 ' + h + 'px !important; }}';
        parentDoc.head.appendChild(style);
        frame.style.setProperty('height', h + 'px', 'important');
    }}
}})();
</script>
"""
    st_html(responsive_wrapper, height=_MAP_HEIGHT_DESKTOP)
else:
    st.info(t("map_no_data"))

# ----------------- #
#       TABLE       #
# ----------------- #
st.markdown("---")
st.subheader(t("table_header"))
cols_to_show = ["event_at", "kind", dist_col, addr_col, "consumer_count", "map_lat", "map_lon"]
cols_available = [c for c in cols_to_show if c in filtered_df.columns]
table_df = filtered_df[cols_available].sort_values(["event_at", addr_col], ascending=[False, True]).head(5000)
table_df = table_df.assign(kind=table_df["kind"].map(_kind_display_map))
col_rename = {
    "event_at": t("col_event_at"),
    "kind": t("col_kind"),
    dist_col: t("col_district"),
    addr_col: t("col_address"),
    "consumer_count": t("col_consumer_count"),
    "map_lat": t("col_lat"),
    "map_lon": t("col_lon"),
}
table_df = table_df.rename(columns=col_rename)
st.dataframe(table_df, use_container_width=True)

# ----------------- #
#    DISCLAIMER     #
# ----------------- #
st.markdown("---")
st.caption(t("disclaimer"))

