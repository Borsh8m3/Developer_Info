# Developer_Info
This project is a comprehensive machine learning tool designed to predict property prices per square meter in the Polish market. By leveraging the power of XGBoost and processing millions of historical transaction records, the model provides highly accurate valuations based on both technical parameters and geographic data.

# Wymagania i Instalacja:

Aby uruchomić projekt lokalnie, upewnij się, że masz zainstalowanego Pythona w wersji 3.10 lub nowszej.

# Sklonuj repozytorium:

Bash

git clone https://github.com/TwojLogin/NazwaProjektu.git

cd NazwaProjektu

Zainstaluj wymagane biblioteki:

Bash
pip install xgboost joblib pandas streamlit streamlit-folium folium

# Jak odpalić aplikację?
Będąc w folderze projektu, uruchom Streamlit za pomocą komendy:

Bash

streamlit run app.py

Aplikacja otworzy się automatycznie w Twojej domyślnej przeglądarce pod adresem http://localhost:8501.

Uwaga: Upewnij się, że pliki model.joblib oraz model_metadata.joblib znajdują się w głównym folderze aplikacji.
