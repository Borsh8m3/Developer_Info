import streamlit as st
import xgboost as xgb
import joblib
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Kalkulator Nieruchomości 2026", layout="wide")

# --- ŁADOWANIE MODELU I METADANYCH ---
@st.cache_resource
def load_assets():
    model = joblib.load('model.joblib')
    meta = joblib.load('model_metadata.joblib')
    return model, meta

try:
    model, meta = load_assets()
except Exception as e:
    st.error(f"Błąd ładowania modelu: {e}")
    st.stop()

# --- INICJALIZACJA HISTORII W SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- SIDEBAR: PARAMETRY TECHNICZNE ---
with st.sidebar:
    st.header("⚙️ Parametry mieszkania")
    powierzchnia = st.number_input("Powierzchnia (m2)", 15.0, 250.0, 50.0)
    rynek = st.selectbox("Rynek", [0, 1], format_func=lambda x: "Pierwotny" if x==1 else "Wtórny")
    sprzedajacy = st.selectbox("Sprzedający", [0, 1], format_func=lambda x: "Firma" if x==1 else "Osoba prywatna")
    
    # Dodatkowe parametry z Kroku VI 
    bud_rodzaj = st.selectbox("Rodzaj budynku", ["Wielorodzinny", "Jednorodzinny", "Inny"])
    nier_prawo = st.selectbox("Prawo", ["Własność", "Użytkowanie wieczyste"])
    
    st.divider()
    rok = 2026
    miesiac = 4
    teryt = st.text_input("Kod TERYT (opcjonalnie)", "0264011")

# --- GŁÓWNY PANEL: MAPA ---
st.title("🏠 Inteligentna Wycena Nieruchomości")
st.subheader("Kliknij na mapie, aby wybrać lokalizację")

col_map, col_res = st.columns([2, 1])

with col_map:
    # Mapa wycentrowana na Polskę
    m = folium.Map(location=[52.2297, 21.0122], zoom_start=6)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=450, use_container_width=True)

    lat, lon = 52.2297, 21.0122 # domyślne
    if map_data and map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']
        st.success(f"Wybrano lokalizację: {lat:.4f}, {lon:.4f}")

# --- PREDYKCJA ---
with col_res:
    st.write("### Twoja Wycena")
    if st.button("🚀 Oblicz wartość", use_container_width=True):
        # Budowanie słownika z danymi wejściowymi
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
        
        # Filtrujemy tylko te cechy, których faktycznie wymaga model
        input_dict = {k: [v] for k, v in raw_data.items() if k in meta['features']}
        input_df = pd.DataFrame(input_dict)
        
        # Konwersja na kategorie (jeśli model tego wymaga)
        for col in input_df.columns:
            if col in ['bud_rodzaj', 'nier_prawo', 'wojewodztwo', 'typ_gminy']:
                input_df[col] = input_df[col].astype('category')

        prediction = model.predict(input_df)[0]
        
        # Zapis do historii
        calc_entry = {
            "Czas": datetime.now().strftime("%H:%M:%S"),
            "Lokalizacja": f"{lat:.2f}, {lon:.2f}",
            "Metraż": powierzchnia,
            "Cena": round(prediction, 2)
        }
        st.session_state.history.insert(0, calc_entry)
        
        st.metric("Szacowana Cena", f"{prediction:,.2f} PLN")
        st.caption("Mediana błędu modelu: 22,000 PLN")

# --- SEKCIJA PORÓWNAWCZA I HISTORIA ---
st.divider()
st.header("📊 Historia i Porównanie")

if st.session_state.history:
    df_hist = pd.DataFrame(st.session_state.history)
    
    tab1, tab2 = st.tabs(["🕒 Historia kalkulacji", "⚖️ Porównywarka"])
    
    with tab1:
        st.table(df_hist)
        if st.button("Wyczyść historię"):
            st.session_state.history = []
            st.rerun()
            
    with tab2:
        if len(st.session_state.history) >= 2:
            st.write("Porównanie dwóch ostatnich wycen:")
            c1, c2 = st.columns(2)
            h1 = st.session_state.history[0]
            h2 = st.session_state.history[1]
            
            c1.metric(f"Wycena A ({h1['Lokalizacja']})", f"{h1['Cena']:,} PLN", 
                      delta=round(h1['Cena'] - h2['Cena'], 2))
            c2.metric(f"Wycena B ({h2['Lokalizacja']})", f"{h2['Cena']:,} PLN", 
                      delta=round(h2['Cena'] - h1['Cena'], 2))
            
            # Wykres słupkowy porównawczy
            st.bar_chart(df_hist.head(5).set_index('Lokalizacja')['Cena'])
        else:
            st.info("Zrób co najmniej dwie wyceny, aby odblokować porównywarkę.")
else:
    st.info("Brak historii. Wykonaj pierwszą kalkulację, aby zobaczyć dane.")