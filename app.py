import streamlit as st
import xgboost as xgb
import joblib
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Property Calculator 2026", layout="wide")

# --- LOAD MODEL AND METADATA ---
@st.cache_resource
def load_assets():
    model = joblib.load('model.joblib')
    meta = joblib.load('model_metadata.joblib')
    return model, meta

try:
    model, meta = load_assets()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

# --- INITIALIZE HISTORY IN SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR: TECHNICAL PARAMETERS ---
with st.sidebar:
    st.header("⚙️ Apartment Parameters")
    powierzchnia = st.number_input("Area (m2)", 15.0, 250.0, 50.0)
    rynek = st.selectbox("Market", [0, 1], format_func=lambda x: "Primary" if x==1 else "Secondary")
    sprzedajacy = st.selectbox("Seller", [0, 1], format_func=lambda x: "Company" if x==1 else "Private individual")

    # Additional parameters from Step VI
    bud_rodzaj = st.selectbox("Building type", ["Multi-family", "Single-family", "Other"])
    nier_prawo = st.selectbox("Legal title", ["Ownership", "Perpetual usufruct"])

    st.divider()
    rok = 2026
    miesiac = 4
    teryt = st.text_input("TERYT code (optional)", "0264011")

# --- MAIN PANEL: MAP ---
st.title("🏠 Smart Property Valuation")
st.subheader("Click on the map to select a location")

col_map, col_res = st.columns([2, 1])

with col_map:
    # Mapa wycentrowana na Polskę
    m = folium.Map(location=[52.2297, 21.0122], zoom_start=6)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=450, use_container_width=True)

    lat, lon = 52.2297, 21.0122 # default
    if map_data and map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.success(f"Location selected: {lat:.4f}, {lon:.4f}")

# --- PREDICTION ---
with col_res:
    st.write("### Your Valuation")
    if st.button("🚀 Calculate value", use_container_width=True):
        # Build a dictionary with the input data
        raw_data = {
            'bud_pow_uzyt': powierzchnia,
            'RynekPierwotny': rynek,
            'Sprzedajacy': sprzedajacy,
            'teryt': int(teryt),
            'rok': rok,
            'miesiac': miesiac,
            'lon': lon,
            'lat': lat,
            'bud_rodzaj': bud_rodzaj,
            'nier_prawo': nier_prawo
        }
        
        # Keep only the features the model actually requires
        input_dict = {k: [v] for k, v in raw_data.items() if k in meta['features']}
        input_df = pd.DataFrame(input_dict)

        # Convert to category dtype (if the model requires it)
        for col in input_df.columns:
            if col in ['bud_rodzaj', 'nier_prawo', 'wojewodztwo', 'typ_gminy']:
                input_df[col] = input_df[col].astype('category')

        prediction = model.predict(input_df)[0]

        # Save to history
        calc_entry = {
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Location": f"{lat:.2f}, {lon:.2f}",
            "Area": powierzchnia,
            "Price": round(prediction, 2)
        }
        st.session_state.history.insert(0, calc_entry)

        st.metric("Estimated Price", f"{prediction:,.2f} PLN")
        st.caption("Model error median: 22,000 PLN")

# --- HISTORY AND COMPARISON SECTION ---
st.divider()
st.header("📊 History and Comparison")

if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)

    tab1, tab2 = st.tabs(["🕒 Calculation history", "⚖️ Comparison"])

    with tab1:
        st.table(df_hist)
        if st.button("Clear history"):
            st.session_state.history = []
            st.rerun()

    with tab2:
        if len(st.session_state.history) >= 2:
            st.write("Comparison of the last two valuations:")
            c1, c2 = st.columns(2)
            h1 = st.session_state.history[0]
            h2 = st.session_state.history[1]

            c1.metric(f"Valuation A ({h1['Location']})", f"{h1['Price']:,} PLN",
                      delta=round(h1['Price'] - h2['Price'], 2))
            c2.metric(f"Valuation B ({h2['Location']})", f"{h2['Price']:,} PLN",
                      delta=round(h2['Price'] - h1['Price'], 2))

            # Comparison bar chart
            st.bar_chart(df_hist.head(5).set_index('Location')['Price'])
        else:
            st.info("Make at least two valuations to unlock the comparison tool.")
else:
    st.info("No history yet. Run your first calculation to see data here.")