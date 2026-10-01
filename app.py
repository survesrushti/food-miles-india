import json
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Food Miles | India",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROCESSED = BASE_DIR / "data" / "processed"

DASHBOARD_FILE = PROCESSED / "dashboard_food_data.csv"
METADATA_FILE = PROCESSED / "dashboard_metadata.json"
TOP_SOURCES_FILE = PROCESSED / "analysis_top_sources.csv"
YEARLY_FILE = PROCESSED / "analysis_yearly_trends.csv"
RESEARCH_SUMMARY_FILE = PROCESSED / "research_summary.json"
PARTNERS_FILE = PROCESSED / "food_miles_by_partner.csv"
FINDINGS_FILE = PROCESSED / "research_findings.csv"


# ============================================================
# DESIGN TOKENS
# ============================================================

MINT = "#34d399"
CYAN = "#22d3ee"
CORAL = "#fb7185"
SLATE = "#94a3b8"
TEXT = "#e6edf3"
MUTED = "#8b9aab"
DISTANCE_SCALE = ["#34d399", "#22d3ee", "#60a5fa"]

PLOTLY_CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

FOOD_ICONS = {
    "Almonds, in shell": "🌰",
    "Apples": "🍎",
    "Bananas": "🍌",
    "Cashew nuts, in shell": "🥜",
    "Chick peas, dry": "🌱",
    "Coffee, green": "☕",
    "Grapes": "🍇",
    "Hazelnuts, in shell": "🌰",
    "Kiwi fruit": "🥝",
    "Lentils, dry": "🌱",
    "Maize (corn)": "🌽",
    "Mangoes, guavas and mangosteens": "🥭",
    "Palm oil": "🌴",
    "Potatoes": "🥔",
    "Refined sugar": "🍬",
    "Rice": "🍚",
    "Soya beans": "🌱",
    "Tea leaves": "🍵",
    "Tomatoes": "🍅",
    "Wheat": "🌾",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{--bg:#0a0f14;--card:#111922;--card-2:#0e151c;--border:#1f2b37;--text:#e6edf3;--muted:#8b9aab;--mint:#34d399;--cyan:#22d3ee;--coral:#fb7185;}
html,body,.stApp{font-family:'Inter','Segoe UI',-apple-system,Roboto,sans-serif;}
.stApp{background:radial-gradient(1100px 480px at 8% -8%,rgba(52,211,153,.11),transparent 60%),radial-gradient(900px 420px at 100% 0%,rgba(34,211,238,.08),transparent 55%),var(--bg);color:var(--text);}
header[data-testid="stHeader"]{background:transparent;}
footer{visibility:hidden;}
.block-container{max-width:1180px;padding-top:2rem;padding-bottom:4rem;}
.hero{border:1px solid var(--border);border-radius:24px;padding:2.2rem 2.4rem;margin-bottom:1.4rem;background:linear-gradient(135deg,rgba(52,211,153,.12),rgba(17,25,34,.92) 45%,rgba(34,211,238,.07));}
.hero-eyebrow{font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);font-weight:600;}
.hero h1{font-size:3.1rem;margin:.35rem 0 0;padding:0;font-weight:800;color:var(--text);letter-spacing:-.02em;}
.hero-sub{font-size:1.3rem;color:var(--mint);font-weight:600;margin-bottom:.6rem;}
.hero p{color:var(--muted);max-width:740px;line-height:1.65;margin:0;}
.pills{display:flex;flex-wrap:wrap;gap:.5rem;margin-top:1.2rem;}
.pill{border:1px solid var(--border);border-radius:999px;padding:.28rem .8rem;font-size:.78rem;color:var(--text);background:rgba(255,255,255,.03);}
.pill.mint{border-color:rgba(52,211,153,.5);color:var(--mint);}
.pill.cyan{border-color:rgba(34,211,238,.5);color:var(--cyan);}
.pill.coral{border-color:rgba(251,113,133,.5);color:var(--coral);}
.section{margin:2.8rem 0 1rem;}
.eyebrow{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--mint);font-weight:700;}
.section h2{font-size:1.65rem;margin:.25rem 0 .2rem;padding:0;font-weight:700;color:var(--text);}
.section-sub{color:var(--muted);margin:0;max-width:780px;line-height:1.55;}
.kpi{background:linear-gradient(180deg,#131d27,#0e161e);border:1px solid var(--border);border-radius:18px;padding:1.1rem 1.25rem;height:100%;}
.kpi-label{font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:600;}
.kpi-value{font-size:2rem;font-weight:700;line-height:1.15;margin:.4rem 0 .25rem;color:var(--text);}
.kpi.mint .kpi-value{color:var(--mint);}
.kpi.cyan .kpi-value{color:var(--cyan);}
.kpi.coral .kpi-value{color:var(--coral);}
.kpi-value.small{font-size:1.3rem;}
.kpi-sub{font-size:.8rem;color:var(--muted);line-height:1.4;}
.food-hero{display:flex;align-items:center;gap:1.2rem;border:1px solid rgba(52,211,153,.35);border-radius:22px;padding:1.3rem 1.5rem;background:linear-gradient(120deg,rgba(52,211,153,.13),rgba(17,25,34,.95) 60%);margin:1rem 0 1.1rem;}
.food-icon{font-size:2.5rem;width:74px;height:74px;border-radius:20px;background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.4);display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.food-name{font-size:1.9rem;font-weight:700;color:var(--text);line-height:1.2;}
.tags{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:.5rem;}
.callout{border-radius:14px;padding:.85rem 1.1rem;font-size:.92rem;line-height:1.55;margin:.8rem 0;border:1px solid var(--border);color:var(--text);}
.callout.coral{background:rgba(251,113,133,.08);border-color:rgba(251,113,133,.38);}
.callout.cyan{background:rgba(34,211,238,.07);border-color:rgba(34,211,238,.32);}
.src{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:.85rem 1rem;margin-bottom:.65rem;}
.src-top{display:flex;justify-content:space-between;align-items:baseline;gap:.5rem;}
.src-rank{color:var(--mint);font-weight:700;font-size:.85rem;margin-right:.35rem;}
.src-name{font-weight:600;color:var(--text);}
.src-share{color:var(--cyan);font-weight:700;}
.bar{height:6px;border-radius:999px;background:#1a2530;margin:.55rem 0 .45rem;overflow:hidden;}
.bar span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--mint),var(--cyan));}
.src-meta{font-size:.8rem;color:var(--muted);}
.meter{height:14px;border-radius:999px;background:#1a2530;margin:.7rem 0 .5rem;overflow:hidden;}
.meter span{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--mint),var(--cyan));}
div[data-baseweb="select"]>div,div[data-baseweb="input"]>div{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:12px!important;}
.stTabs [data-baseweb="tab-list"]{gap:.4rem;border-bottom:1px solid var(--border);}
.stTabs [data-baseweb="tab"]{color:var(--muted);}
.stTabs [aria-selected="true"]{color:var(--mint)!important;}
[data-testid="stExpander"]{border:1px solid var(--border);border-radius:14px;background:var(--card-2);}
.stDownloadButton button{background:transparent;border:1px solid var(--border);color:var(--text);border-radius:10px;}
.stDownloadButton button:hover{border-color:var(--mint);color:var(--mint);}
.footer-note{color:var(--muted);font-size:.8rem;text-align:center;margin-top:3rem;padding-top:1.2rem;border-top:1px solid var(--border);}
"""


# ============================================================
# HELPERS
# ============================================================

def render(markup):
    """Show HTML. Lines are joined so Markdown does not treat indents as code."""
    cleaned = " ".join(line.strip() for line in markup.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def compact(value):
    """Short number format, e.g. 158,603,475 -> 158.6M."""
    if pd.isna(value):
        return "N/A"
    size = abs(value)
    if size >= 1e9:
        return f"{value / 1e9:,.1f}B"
    if size >= 1e6:
        return f"{value / 1e6:,.1f}M"
    if size >= 1e3:
        return f"{value / 1e3:,.1f}K"
    return f"{value:,.0f}"


def number(value, pattern="{:,.0f}", suffix=""):
    """Format a number, or return N/A for missing values."""
    if pd.isna(value):
        return "N/A"
    return pattern.format(value) + suffix


def safe_filename(text):
    """Make a food name safe to use in a file name."""
    return text.replace(",", "").replace("(", "").replace(")", "").replace(" ", "_")


def section(number_label, title, subtitle=""):
    sub = f'<p class="section-sub">{escape(subtitle)}</p>' if subtitle else ""
    render(
        f'<div class="section"><div class="eyebrow">{escape(number_label)}</div>'
        f"<h2>{escape(title)}</h2>{sub}</div>"
    )


def kpi(label, value, sub="", accent="mint", small=False, hover=""):
    size = " small" if small else ""
    return (
        f'<div class="kpi {accent}" title="{escape(hover)}">'
        f'<div class="kpi-label">{escape(label)}</div>'
        f'<div class="kpi-value{size}">{escape(str(value))}</div>'
        f'<div class="kpi-sub">{escape(sub)}</div></div>'
    )


def style_fig(fig, height=360):
    """Apply the dark research theme to a Plotly figure."""
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=30, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#c9d4df", size=13),
        hoverlabel=dict(bgcolor="#0f171f", bordercolor="#2a3a4a", font=dict(color=TEXT)),
        legend=dict(orientation="h", y=1.14, x=0, bgcolor="rgba(0,0,0,0)"),
    )
    grid = "rgba(148,163,184,0.10)"
    line = "rgba(148,163,184,0.22)"
    fig.update_xaxes(gridcolor=grid, zerolinecolor=line, linecolor=line)
    fig.update_yaxes(gridcolor=grid, zerolinecolor=line, linecolor=line)
    return fig


def show_chart(fig, key):
    """Show a Plotly chart, falling back gracefully on API differences."""
    try:
        st.plotly_chart(fig, theme=None, config=PLOTLY_CONFIG, key=key)
    except TypeError:
        st.plotly_chart(fig, key=key)


def source_card(rank, row):
    share = float(row["share_of_food_imports"])
    width = min(max(share, 0), 100)
    return (
        '<div class="src"><div class="src-top"><span>'
        f'<span class="src-rank">#{rank}</span>'
        f'<span class="src-name">{escape(str(row["Country"]))}</span></span>'
        f'<span class="src-share">{share:.1f}%</span></div>'
        f'<div class="bar"><span style="width:{width:.1f}%"></span></div>'
        f'<div class="src-meta">{row["quantity_tonnes"]:,.0f} tonnes · '
        f'{row["distance_km"]:,.0f} km (straight-line)</div></div>'
    )


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():

    dashboard = pd.read_csv(DASHBOARD_FILE)
    sources = pd.read_csv(TOP_SOURCES_FILE)
    yearly = pd.read_csv(YEARLY_FILE)

    partners = pd.read_csv(PARTNERS_FILE) if PARTNERS_FILE.exists() else None
    findings = pd.read_csv(FINDINGS_FILE) if FINDINGS_FILE.exists() else None

    with open(METADATA_FILE, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    with open(RESEARCH_SUMMARY_FILE, "r", encoding="utf-8") as file:
        research_summary = json.load(file)

    return dashboard, sources, yearly, partners, findings, metadata, research_summary


dashboard, sources, yearly, partners, findings, metadata, research_summary = load_data()

if "low_import_volume" not in dashboard.columns:
    dashboard["low_import_volume"] = False

START_YEAR = metadata["analysis_period"]["start_year"]
END_YEAR = metadata["analysis_period"]["end_year"]
PERIOD = f"{START_YEAR}–{END_YEAR}"

MIN_TONNES = metadata.get(
    "low_volume_threshold_tonnes",
    research_summary.get("minimum_import_tonnes_for_rankings", 10000),
)

st.markdown(f"<style>{' '.join(CSS.strip().splitlines())}</style>", unsafe_allow_html=True)


# ============================================================
# 1. HERO
# ============================================================

trade_partners = metadata.get("trade_partners", "N/A")

render(
    f"""
    <div class="hero">
    <div class="hero-eyebrow">M.Sc. Computer Science · Data Visualization Research Project</div>
    <h1>Food Miles</h1>
    <div class="hero-sub">Tracking the Journey of Food</div>
    <p>An interactive research dashboard exploring how far food travels through
    international trade to reach India, and how imports relate to India's domestic
    food production.</p>
    <div class="pills">
    <span class="pill mint">● Period {PERIOD}</span>
    <span class="pill cyan">Data: FAOSTAT · CEPII</span>
    <span class="pill">{metadata["total_foods"]} foods</span>
    <span class="pill">{trade_partners} trade partners</span>
    </div>
    </div>
    """
)


# ============================================================
# 2. KPI OVERVIEW
# ============================================================

section("01 · Overview", "Key Numbers", f"Summary of the validated results for {PERIOD}.")

ranked_foods = dashboard[~dashboard["low_import_volume"].astype(bool)]
total_miles = dashboard["import_food_miles_billion"].sum()
median_distance = ranked_foods["weighted_import_distance_km"].median()
distinct_sources = sources["Country"].nunique()

k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    render(kpi(
        "Foods Analysed", metadata["total_foods"],
        "staple foods, fruits, nuts and oils", "mint",
        hover="Foods selected from FAOSTAT trade data."
    ))

with k2:
    render(kpi(
        "Total Import Food Miles", f"{total_miles:,.0f} B",
        f"billion tonne-km, {PERIOD}", "cyan",
        hover="Sum of quantity x distance over all foods and source countries."
    ))

with k3:
    render(kpi(
        "Median Import Distance", f"{median_distance:,.0f} km",
        f"middle value of {len(ranked_foods)} foods with at least {MIN_TONNES:,} t imports",
        "mint",
        hover="Median of each food's quantity-weighted import distance. "
              "A pooled average would mostly describe palm oil."
    ))

with k4:
    render(kpi(
        "Source Countries", f"{distinct_sources}",
        "distinct countries supplying India", "cyan",
        hover="Countries with a valid distance that exported at least one of the foods to India."
    ))


# ============================================================
# 3. FOOD EXPLORER
# ============================================================

section(
    "02 · Food Explorer", "Choose a Food",
    "Search by name, then pick a food. Every section below updates for your choice."
)

food_list = dashboard["Food"].tolist()

explorer_left, explorer_right = st.columns([1, 2], gap="medium")

with explorer_left:
    search_text = st.text_input(
        "Search foods",
        placeholder="Search, e.g. rice, nut, oil",
        label_visibility="collapsed",
        key="food_search",
    )

matches = food_list

if search_text.strip():
    matches = [f for f in food_list if search_text.strip().lower() in f.lower()]

with explorer_right:
    if not matches:
        st.warning("No food matches your search. Showing all foods.")
        matches = food_list

    selected_food = st.selectbox(
        "Select a food",
        matches,
        label_visibility="collapsed",
        key="food_select",
    )

selected = dashboard[dashboard["Food"] == selected_food].iloc[0]
is_low_volume = bool(selected["low_import_volume"])
dependency_value = selected["import_dependency_percent"]
production_value = selected["india_production_tonnes"]

tags = [f'<span class="pill mint">{PERIOD}</span>']
if is_low_volume:
    tags.append('<span class="pill coral">Low import volume</span>')
if pd.isna(dependency_value):
    tags.append('<span class="pill">Dependency not calculated</span>')

render(
    f"""
    <div class="food-hero">
    <div class="food-icon">{FOOD_ICONS.get(selected_food, "🌍")}</div>
    <div>
    <div class="eyebrow">Selected food</div>
    <div class="food-name">{escape(selected_food)}</div>
    <div class="tags">{"".join(tags)}</div>
    </div>
    </div>
    """
)


# ============================================================
# 4. SELECTED FOOD OVERVIEW
# ============================================================

section("03 · Selected Food", "Overview", f"Trade with India, {PERIOD}.")

if is_low_volume:
    render(
        f'<div class="callout coral"><b>Low import volume.</b> India imported only '
        f'{selected["import_quantity_tonnes"]:,.0f} tonnes of {escape(selected_food)} '
        f"in {PERIOD}. Distances and source shares for this food rest on very small "
        "volumes and should not be used for conclusions. It is excluded from the "
        "research rankings.</div>"
    )

s1, s2, s3, s4 = st.columns(4, gap="medium")

with s1:
    render(kpi(
        "Total Imports", compact(selected["import_quantity_tonnes"]),
        f"tonnes, {PERIOD}", "mint"
    ))

with s2:
    render(kpi(
        "Weighted Import Distance",
        f"{selected['weighted_import_distance_km']:,.0f} km",
        "quantity-weighted average", "cyan",
        hover="Average distance after weighting each source country by the quantity it supplied."
    ))

with s3:
    render(kpi(
        "Import Food Miles", f"{selected['import_food_miles_billion']:,.2f} B",
        "billion tonne-km", "mint",
        hover="Sum of (tonnes x km) over all source countries."
    ))

with s4:
    render(kpi(
        "Source Countries", f"{int(selected['source_countries'])}",
        "countries supplying India", "cyan"
    ))

food_sources = sources[sources["Item"] == selected_food].sort_values(
    "quantity_tonnes", ascending=False
)
food_yearly = yearly[yearly["Item"] == selected_food].sort_values("Year")
file_stub = safe_filename(selected_food)

d1, d2, d3 = st.columns(3, gap="medium")

with d1:
    st.download_button(
        "⬇ Food summary (CSV)",
        data=dashboard[dashboard["Food"] == selected_food].to_csv(index=False).encode("utf-8"),
        file_name=f"{file_stub}_summary.csv",
        mime="text/csv",
        key="dl_summary",
    )

with d2:
    st.download_button(
        "⬇ Source countries (CSV)",
        data=food_sources.to_csv(index=False).encode("utf-8"),
        file_name=f"{file_stub}_import_sources.csv",
        mime="text/csv",
        key="dl_sources",
    )

with d3:
    st.download_button(
        "⬇ Year-wise data (CSV)",
        data=food_yearly.to_csv(index=False).encode("utf-8"),
        file_name=f"{file_stub}_yearly.csv",
        mime="text/csv",
        key="dl_yearly",
    )


# ============================================================
# 5. FOOD JOURNEY
# ============================================================

section(
    "04 · Food Journey", "Where Does It Come From?",
    "Top source countries by quantity, with estimated straight-line distance to India. "
    "Distances are not shipping routes."
)

journey_left, journey_right = st.columns([1, 1.5], gap="large")

with journey_left:

    if len(food_sources) > 0:
        cards = [source_card(i + 1, row) for i, (_, row) in enumerate(food_sources.head(5).iterrows())]
        render("".join(cards))
    else:
        st.info("No source-country data available.")

with journey_right:

    map_data = None

    if partners is not None:
        map_data = partners[
            (partners["Item"] == selected_food) & partners["iso3"].notna()
        ].copy()

    if map_data is not None and len(map_data) > 0:

        fig_map = px.scatter_geo(
            map_data,
            locations="iso3",
            locationmode="ISO-3",
            size="quantity_tonnes",
            color="distance_km",
            hover_name="Partner Countries",
            hover_data={
                "iso3": False,
                "quantity_tonnes": ":,.0f",
                "distance_km": ":,.0f",
                "share_of_food_imports_pct": ":.1f",
            },
            labels={
                "quantity_tonnes": "Quantity (tonnes)",
                "distance_km": "Distance (km)",
                "share_of_food_imports_pct": "Share of imports (%)",
            },
            color_continuous_scale=DISTANCE_SCALE,
            size_max=40,
        )

        fig_map.add_trace(
            go.Scattergeo(
                locations=["IND"],
                locationmode="ISO-3",
                mode="markers",
                marker=dict(size=13, color="#f8fafc", symbol="star",
                            line=dict(color=MINT, width=1.5)),
                name="India (destination)",
                hovertext="India (destination)",
                hoverinfo="text",
            )
        )

        fig_map.update_geos(
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
            showland=True, landcolor="#16212c",
            showocean=True, oceancolor="#0a0f14",
            showcountries=True, countrycolor="#243443",
            coastlinecolor="#243443",
            showframe=False,
        )

        style_fig(fig_map, height=430)
        fig_map.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar=dict(title="Distance (km)", thickness=10, len=0.7),
            showlegend=False,
        )

        show_chart(fig_map, key="map_sources")

        st.caption(
            "Bubble size shows the quantity imported from each country; colour shows the "
            "estimated straight-line distance to India (star). Hover over a bubble for details."
        )

    else:
        st.info("Map data is not available for this food.")

if len(food_sources) > 0:

    with st.expander("Top 10 source countries: chart and table"):

        top10 = food_sources.head(10).copy()

        fig_top = px.bar(
            top10.sort_values("quantity_tonnes"),
            x="quantity_tonnes",
            y="Country",
            orientation="h",
            color="distance_km",
            color_continuous_scale=DISTANCE_SCALE,
            labels={"quantity_tonnes": "Quantity (tonnes)", "distance_km": "Distance (km)"},
            hover_data={"share_of_food_imports": ":.1f"},
        )
        style_fig(fig_top, height=380)
        fig_top.update_layout(coloraxis_colorbar=dict(title="km", thickness=10))
        show_chart(fig_top, key="bar_top_sources")

        table_sources = top10[
            ["Country", "quantity_tonnes", "distance_km", "share_of_food_imports"]
        ].copy()
        table_sources.columns = [
            "Country", "Quantity (tonnes)", "Distance (km)", "Share of Imports (%)"
        ]

        st.dataframe(table_sources, width="stretch", hide_index=True)


# ============================================================
# 6. IMPORT VS EXPORT
# ============================================================

section(
    "05 · Import vs Export", "Imports and Exports Compared",
    "Food Miles = tonnes × km, summed over all partner countries."
)

trade_left, trade_right = st.columns([1.6, 1], gap="large")

with trade_left:

    fig_trade = go.Figure(
        go.Bar(
            x=["Imports", "Exports"],
            y=[selected["import_food_miles_billion"], selected["export_food_miles_billion"]],
            marker_color=[MINT, CYAN],
            text=[
                f"{selected['import_food_miles_billion']:,.2f} B",
                f"{selected['export_food_miles_billion']:,.2f} B",
            ],
            textposition="outside",
            hovertemplate="%{x}: %{y:,.3f} billion tonne-km<extra></extra>",
        )
    )
    style_fig(fig_trade, height=340)
    fig_trade.update_layout(yaxis_title="Food Miles (billion tonne-km)", showlegend=False)
    show_chart(fig_trade, key="chart_import_export")

with trade_right:

    render(
        kpi(
            "Imports", compact(selected["import_quantity_tonnes"]) + " t",
            f"weighted distance {selected['weighted_import_distance_km']:,.0f} km",
            "mint", small=True,
        )
    )
    st.write("")
    render(
        kpi(
            "Exports", compact(selected["export_quantity_tonnes"]) + " t",
            f"weighted distance {selected['weighted_export_distance_km']:,.0f} km",
            "cyan", small=True,
        )
    )

st.caption(
    "Quantity, distance and Food Miles use the same period. A bigger bar means more "
    "tonne-kilometres, which can come from larger volumes, longer distances, or both."
)


# ============================================================
# 7. YEAR-WISE FOOD MILES
# ============================================================

section(
    "06 · Trend", "Year-wise Food Miles",
    f"Yearly import and export Food Miles for {selected_food}, {PERIOD}."
)

if len(food_yearly) > 0:

    fig_year = go.Figure()

    fig_year.add_trace(go.Scatter(
        x=food_yearly["Year"], y=food_yearly["import_food_miles_billion"],
        mode="lines+markers", name="Import Food Miles",
        line=dict(color=MINT, width=3), marker=dict(size=6),
        hovertemplate="%{y:,.3f} B tonne-km",
    ))

    fig_year.add_trace(go.Scatter(
        x=food_yearly["Year"], y=food_yearly["export_food_miles_billion"],
        mode="lines+markers", name="Export Food Miles",
        line=dict(color=CYAN, width=3), marker=dict(size=6),
        hovertemplate="%{y:,.3f} B tonne-km",
    ))

    style_fig(fig_year, height=380)
    fig_year.update_layout(
        hovermode="x unified",
        yaxis_title="Food Miles (billion tonne-km)",
        xaxis_title="Year",
    )
    show_chart(fig_year, key="chart_yearly")

    with st.expander("Year-wise data table"):

        table_yearly = food_yearly[
            ["Year", "import_food_miles_billion", "export_food_miles_billion"]
        ].copy()
        table_yearly.columns = [
            "Year", "Import Food Miles (B tonne-km)", "Export Food Miles (B tonne-km)"
        ]

        st.dataframe(table_yearly, width="stretch", hide_index=True)

else:
    st.info("No yearly data available for this food.")


# ============================================================
# 8. INDIA PRODUCTION & TRADE
# ============================================================

section(
    "07 · Production & Trade", "India Production and Trade",
    f"Average tonnes per year, {PERIOD}, so production, imports and exports are comparable."
)

if pd.notna(production_value):

    p1, p2, p3 = st.columns(3, gap="medium")

    with p1:
        render(kpi("India Production", compact(production_value),
                   f"tonnes per year (average, {PERIOD})", "mint"))
    with p2:
        render(kpi("Imports", compact(selected["avg_annual_imports_tonnes"]),
                   f"tonnes per year (average, {PERIOD})", "cyan"))
    with p3:
        render(kpi("Exports", compact(selected["avg_annual_exports_tonnes"]),
                   f"tonnes per year (average, {PERIOD})", "white"))

    use_log = st.toggle(
        "Logarithmic scale (makes small values visible)", value=False, key="log_scale"
    )

    values = [
        production_value,
        selected["avg_annual_imports_tonnes"],
        selected["avg_annual_exports_tonnes"],
    ]

    fig_prod = go.Figure(
        go.Bar(
            x=["India production", "Imports", "Exports"],
            y=values,
            marker_color=[MINT, CYAN, SLATE],
            text=[compact(v) for v in values],
            textposition="outside",
            hovertemplate="%{x}: %{y:,.0f} tonnes per year<extra></extra>",
        )
    )
    style_fig(fig_prod, height=340)
    fig_prod.update_layout(
        yaxis_title="Average tonnes per year",
        yaxis_type="log" if use_log else "linear",
        showlegend=False,
    )
    show_chart(fig_prod, key="chart_production")

else:

    if selected_food == "Refined sugar":
        st.info(
            "Refined sugar is a processed product, while the production data covers "
            "sugar cane. The two are not comparable, so production and import "
            "dependency are not shown for this food."
        )
    else:
        st.info(
            "India's production of this food is not reported in the FAOSTAT production "
            "data used in this project, so production and import dependency are not shown."
        )


# ============================================================
# 9. IMPORT DEPENDENCY
# ============================================================

section(
    "08 · Import Dependency", "How Much Comes From Imports?",
    "The share of the food available in India that came from imports."
)

dep_left, dep_right = st.columns([1, 1.2], gap="large")

with dep_left:

    if pd.notna(dependency_value):
        width = min(max(float(dependency_value), 0), 100)
        render(
            f"""
            <div class="kpi mint">
            <div class="kpi-label">Import dependency · {PERIOD}</div>
            <div class="kpi-value">{dependency_value:.2f}%</div>
            <div class="meter"><span style="width:{width:.1f}%"></span></div>
            <div class="kpi-sub">of domestic supply came from imports</div>
            </div>
            """
        )
    else:
        render(kpi("Import dependency", "N/A", "not calculated for this food", "coral"))

with dep_right:

    st.markdown(
        "**Import dependency = imports ÷ (production + imports − exports) × 100**, "
        f"using national totals pooled over {PERIOD}."
    )
    st.caption(
        "It ignores stocks, seed, animal feed and waste. It is not calculated where "
        "India's production is missing in the data, and it is not calculated for refined "
        "sugar, because production data covers sugar cane."
    )

if pd.isna(dependency_value) and selected_food != "Refined sugar":
    render(
        '<div class="callout cyan">Import dependency is not shown because India\'s '
        "production of this food is not reported in the FAOSTAT production data used "
        "here. It is not treated as zero.</div>"
    )


# ============================================================
# 10. RESEARCH FINDINGS
# ============================================================

section(
    "09 · Research Findings", "What the Data Shows",
    "Findings from the validated analysis across all foods."
)

f1, f2, f3, f4 = st.columns(4, gap="medium")

finding = research_summary["highest_weighted_import_distance"]
with f1:
    render(kpi("Highest Import Distance", finding["food"],
               f"{finding['distance_km']:,.0f} km (weighted average)", "mint", small=True))

finding = research_summary["highest_total_import_food_miles"]
with f2:
    render(kpi("Highest Total Food Miles", finding["food"],
               f"{finding['food_miles_billion_tonne_km']:,.2f} billion tonne-km", "cyan", small=True))

finding = research_summary["most_source_countries"]
with f3:
    render(kpi("Most Source Countries", finding["food"],
               f"{finding['countries']} countries", "mint", small=True))

finding = research_summary["highest_average_import_dependency"]
with f4:
    render(kpi("Highest Import Dependency", finding["food"],
               f"{finding['percentage']:.2f}% of domestic supply", "cyan", small=True))

excluded_foods = research_summary.get("foods_excluded_from_rankings", [])

if excluded_foods:
    st.caption(
        f"Rankings exclude foods with fewer than {MIN_TONNES:,} tonnes of imports in "
        f"{PERIOD}: {', '.join(excluded_foods)}."
    )

if findings is not None and len(findings) > 0:

    st.markdown("#### Top 5 by measure")

    short_names = {
        "Highest weighted import distance": "Import distance",
        "Highest total import Food Miles": "Total Food Miles",
        "Most source countries": "Source countries",
        "Highest average import dependency": "Import dependency",
    }

    finding_types = list(findings["finding_type"].unique())
    finding_tabs = st.tabs([short_names.get(t, t) for t in finding_types])

    for index, (tab, finding_type) in enumerate(zip(finding_tabs, finding_types)):

        with tab:

            subset = findings[findings["finding_type"] == finding_type].copy()
            unit = str(subset["unit"].iloc[0])

            fig_find = go.Figure(
                go.Bar(
                    x=subset["value"],
                    y=subset["food"],
                    orientation="h",
                    marker_color=MINT if index % 2 == 0 else CYAN,
                    text=[f"{v:,.2f}".rstrip("0").rstrip(".") for v in subset["value"]],
                    textposition="outside",
                    hovertemplate="%{y}: %{x:,.2f} " + unit + "<extra></extra>",
                )
            )
            style_fig(fig_find, height=300)
            fig_find.update_layout(
                xaxis_title=unit,
                yaxis=dict(autorange="reversed"),
                showlegend=False,
            )
            show_chart(fig_find, key=f"chart_finding_{index}")

st.markdown(f"#### Total Import Food Miles, {PERIOD}")

all_foods_trend = yearly.groupby("Year")["import_food_miles_billion"].sum()

palm_trend = (
    yearly[yearly["Item"] == "Palm oil"]
    .groupby("Year")["import_food_miles_billion"]
    .sum()
)

trend_data = pd.DataFrame({"All foods": all_foods_trend, "Palm oil": palm_trend}).fillna(0)
trend_data["All other foods"] = trend_data["All foods"] - trend_data["Palm oil"]

fig_total = go.Figure()

for column, colour in [("All foods", MINT), ("Palm oil", CYAN), ("All other foods", SLATE)]:
    fig_total.add_trace(go.Scatter(
        x=trend_data.index, y=trend_data[column],
        mode="lines", name=column, line=dict(color=colour, width=3),
        hovertemplate="%{y:,.2f} B tonne-km",
    ))

style_fig(fig_total, height=380)
fig_total.update_layout(
    hovermode="x unified",
    yaxis_title="Food Miles (billion tonne-km)",
    xaxis_title="Year",
)
show_chart(fig_total, key="chart_total_trend")

yearly_finding = research_summary["yearly_food_miles"]

st.caption(
    f"Total import Food Miles changed from "
    f"{yearly_finding['first_year_billion_tonne_km']:,.2f} billion tonne-km in "
    f"{yearly_finding['first_year']} to "
    f"{yearly_finding['last_year_billion_tonne_km']:,.2f} billion tonne-km in "
    f"{yearly_finding['last_year']}."
)

palm_effect = research_summary.get("palm_oil_effect")

if palm_effect:
    st.caption(
        f"Palm oil made up {palm_effect['share_first_year_pct']:.1f}% of import Food Miles in "
        f"{yearly_finding['first_year']} and {palm_effect['share_last_year_pct']:.1f}% in "
        f"{yearly_finding['last_year']}. Excluding palm oil, the total changed from "
        f"{palm_effect['total_excl_palm_first']:,.2f} to "
        f"{palm_effect['total_excl_palm_last']:,.2f} billion tonne-km."
    )

st.caption(
    "Food Miles combine quantity and distance, so a change can come from larger volumes, "
    "longer distances, or both. This chart does not show which."
)


# ============================================================
# 11. FOOD-WISE COMPARISON
# ============================================================

section(
    "10 · Comparison", "Compare All Foods",
    "Search, sort and filter. Click a column heading to sort."
)

filter_left, filter_right = st.columns([2, 1], gap="medium")

with filter_left:
    table_search = st.text_input(
        "Search the table",
        placeholder="Filter the table by food name",
        label_visibility="collapsed",
        key="table_search",
    )

with filter_right:
    hide_low = st.checkbox(
        "Hide low import volume foods", value=False, key="hide_low_volume"
    )

comparison = dashboard[
    [
        "Food",
        "weighted_import_distance_km",
        "import_food_miles_billion",
        "import_quantity_tonnes",
        "source_countries",
        "import_dependency_percent",
        "low_import_volume",
    ]
].copy()

comparison["low_import_volume"] = comparison["low_import_volume"].map(
    {True: "Yes", False: "No"}
)

comparison.columns = [
    "Food",
    "Import Distance (km)",
    "Import Food Miles (B tonne-km)",
    "Total Imports (tonnes)",
    "Source Countries",
    "Import Dependency (%)",
    "Low Import Volume",
]

if table_search.strip():
    comparison = comparison[
        comparison["Food"].str.contains(table_search.strip(), case=False, na=False)
    ]

if hide_low:
    comparison = comparison[comparison["Low Import Volume"] == "No"]

st.dataframe(
    comparison,
    width="stretch",
    hide_index=True,
    column_config={
        "Import Distance (km)": st.column_config.NumberColumn(format="%.0f"),
        "Import Food Miles (B tonne-km)": st.column_config.NumberColumn(format="%.2f"),
        "Total Imports (tonnes)": st.column_config.NumberColumn(format="%.0f"),
        "Source Countries": st.column_config.NumberColumn(format="%d"),
        "Import Dependency (%)": st.column_config.ProgressColumn(
            min_value=0, max_value=100, format="%.1f"
        ),
    },
)

st.caption(
    "Import dependency is blank where it cannot be calculated. Low Import Volume means "
    f"fewer than {MIN_TONNES:,} tonnes were imported in {PERIOD}."
)

st.download_button(
    "⬇ Download this table (CSV)",
    data=comparison.to_csv(index=False).encode("utf-8"),
    file_name="food_miles_comparison.csv",
    mime="text/csv",
    key="dl_comparison",
)


# ============================================================
# 12. METHODOLOGY / DATA SOURCES / LIMITATIONS
# ============================================================

section(
    "11 · About the Research", "Methodology, Data and Limitations",
    "How the numbers were produced and what they can and cannot tell you."
)

tab_method, tab_data, tab_limits = st.tabs(["Methodology", "Data sources", "Limitations"])

with tab_method:

    st.markdown(
        f"""
The project estimates Food Miles by combining international trade quantities with the
geographic distance between India and its trading partners, for the period **{PERIOD}**.

**Food Miles = Trade Quantity (tonnes) × Distance (km)**

**Weighted distance = Total Food Miles ÷ Total Quantity.** Countries supplying larger
quantities have a larger influence on the average.

Distances are straight-line (great-circle) distances between India and the partner
country's capital, calculated with the Haversine formula. They are **estimates**, not the
actual routes taken by ships, trucks or aircraft.

Trade partners that no longer exist (for example the USSR) or that have no usable
coordinates are left out of distance calculations. Foods with fewer than
{MIN_TONNES:,} tonnes of imports are not used in rankings.
"""
    )

with tab_data:

    st.markdown(
        f"""
- **International trade:** FAOSTAT *Detailed Trade Matrix* (India as reporting country),
  import and export quantities in tonnes by partner country and year.
- **Production:** FAOSTAT *Crops and Livestock Products*, national production in tonnes.
  Sugar cane, not refined sugar, is reported here.
- **Country coordinates:** CEPII GeoDist database (capital-city coordinates), used for the
  Haversine distance calculation.

The analysis period is **{PERIOD}**. State-level production data was not used in this
project.
"""
    )

with tab_limits:

    st.markdown(
        """
- Food Miles measure geographic distance and quantity. They do not measure carbon emissions.
- Distances are straight-line estimates between capital cities, not actual shipping routes.
  Large countries are represented by a single point.
- Trade data shows where food was exported from, which is not always where it was grown
  (re-exports and processing can change this).
- The partner country in trade data is the country recorded by customs. It may differ from
  the country where the food was grown. For example, the large recent soya bean imports from
  Benin, Togo and Niger should be read as recorded trade, not as proof of production there.
- Some FAOSTAT values are flagged as imputed or estimated rather than official.
- Former countries and partners without coordinates are excluded from distance calculations.
- Foods with very small import volumes are shown but not used in rankings.
- Mangoes are reported by FAO together with guavas and mangosteens. Refined sugar is not
  compared with production because production data covers sugar cane.
- Import dependency uses national annual totals and ignores stocks, seed, feed and waste. It
  is not calculated where India's production is missing in the data.
- Transport mode, fuel, storage and refrigeration are not included.
"""
    )


# ============================================================
# FOOTER
# ============================================================

render(
    '<div class="footer-note">Food Miles: Tracking the Journey of Food · '
    "M.Sc. Computer Science Data Visualization Project · Data: FAOSTAT, CEPII</div>"
)