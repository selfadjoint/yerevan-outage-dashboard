import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium.plugins import FastMarkerCluster
from streamlit.components.v1 import html as st_html
from data import get_processed_data


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

# Prepare event_at
df["event_at"] = pd.to_datetime(df["event_at"])
df["event_at"] = df["event_at"].dt.tz_convert("Asia/Yerevan") if df["event_at"].dt.tz is not None else df[
    "event_at"].dt.tz_localize("UTC").dt.tz_convert("Asia/Yerevan")

# Resolve language-dependent column names
addr_col = lang_col("address")
dist_col = lang_col("district")

# ----------------- #
#     SIDEBAR       #
# ----------------- #
st.sidebar.header(t("filters"))

# Date Filter
min_date = df["event_at"].min().date()
max_date = df["event_at"].max().date()
selected_dates = st.sidebar.date_input(
    t("date_range"), value=("2026-02-19", max_date), min_value=min_date, max_value=max_date
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

# Address Filter
available_addresses = sorted(df[addr_col].dropna().unique().tolist())
addresses = st.sidebar.multiselect(
    t("address"),
    options=available_addresses,
    placeholder=t("address_placeholder"),
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
    mask &= df[dist_col].isin(districts)

if addresses:
    mask &= df[addr_col].isin(addresses)

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
    top_district = filtered_df[dist_col].mode()
    top_district_name = top_district.iloc[0] if not top_district.empty else "N/A"
    worst_candidates = filtered_df[filtered_df["building"].notna() & (filtered_df["building"].astype(str).str.strip() != "")]
    if not worst_candidates.empty:
        worst = worst_candidates.groupby(addr_col).agg(
            total=("kind", "count"),
            elec=("kind", lambda x: (x == "Electricity").sum()),
            water=("kind", lambda x: (x == "Water").sum()),
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
#      MAP          #
# ----------------- #
st.subheader(t("map_header"))

map_data = filtered_df.dropna(subset=["map_lat", "map_lon"])
map_data = map_data[(map_data["map_lat"] != 0) & (map_data["map_lon"] != 0)]

if not map_data.empty:
    m = folium.Map(location=[map_data["map_lat"].mean(), map_data["map_lon"].mean()], zoom_start=11)
    map_data = map_data.sort_values("event_at", ascending=False)
    grouped = map_data.groupby(["map_lat", "map_lon"]).agg(
        address=(addr_col, lambda x: "<br/>".join(sorted(set(x.dropna()))[:3]) + (
            "<br/>... and more" if len(set(x.dropna())) > 3 else "")),
        district=(dist_col, "first"),
        last_event=("event_at", "max"),
        electricity_count=("kind", lambda x: (x == "Electricity").sum()),
        water_count=("kind", lambda x: (x == "Water").sum()),
    ).reset_index()

    # Vectorized: build tooltip and color columns
    grouped["color"] = grouped.apply(
        lambda r: "red" if r["electricity_count"] >= r["water_count"] else "blue", axis=1
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

    # Add markers using vectorized data
    for lat, lon, color, tooltip in zip(
        grouped["map_lat"], grouped["map_lon"], grouped["color"], grouped["tooltip"]
    ):
        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            tooltip=tooltip,
        ).add_to(m)

    # Render as static HTML — much faster than st_folium on reruns
    st_html(m._repr_html_(), height=520)
else:
    st.info(t("map_no_data"))

# ----------------- #
#     CHARTS        #
# ----------------- #
st.markdown("---")
col_chart1, col_chart2 = st.columns(2)
# Build translated color map for chart legends
translated_color_map = {kind_label("Electricity"): "#ff4b4b", kind_label("Water"): "#0096ff"}
with col_chart1:
    st.subheader(t("chart_by_district"))
    if not filtered_df.empty:
        chart_df = filtered_df.copy()
        chart_df["kind_display"] = chart_df["kind"].map(lambda k: kind_label(k))
        dist_counts = chart_df.groupby([dist_col, "kind_display"]).size().reset_index(name="count")
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
        timeline_df = filtered_df.copy()
        timeline_df["date"] = timeline_df["event_at"].dt.date
        timeline_df["kind_display"] = timeline_df["kind"].map(lambda k: kind_label(k))
        time_counts = timeline_df.groupby(["date", "kind_display"]).size().reset_index(name="count")
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
#       TABLE       #
# ----------------- #
st.subheader(t("table_header"))
cols_to_show = ["event_at", "kind", dist_col, addr_col, "consumer_count", "map_lat", "map_lon"]
cols_available = [c for c in cols_to_show if c in filtered_df.columns]
table_df = filtered_df[cols_available].sort_values(["event_at", addr_col], ascending=[False, True]).copy()
table_df["kind"] = table_df["kind"].map(lambda k: kind_label(k))
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
