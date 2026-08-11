import os
import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="Kalkulator Wykończeniowy", page_icon="🏗️")

st.title("🏗️ Agent Wycen: Malowanie, Gipsy, Płytki")
st.write("Wpisz zakres prac lub zapytanie od klienta, a agent przeliczy koszt robocizny i materiałów.")

# Bezpieczne pobieranie klucza z sekretów Streamlit
API_KEY = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

def wycen_prace_glazurnicze(plytki_m2: float = 0, wielki_format_m2: float = 0, hydroizolacja_m2: float = 0) -> str:
    stawka_plytki = 120.0
    stawka_wielki_format = 180.0
    stawka_hydro = 45.0
    koszt = (plytki_m2 * stawka_plytki) + (wielki_format_m2 * stawka_wielki_format) + (hydroizolacja_m2 * stawka_hydro)
    return f"WYCENA GLAZURNICZA: Płytki ({plytki_m2}m²): {plytki_m2*stawka_plytki:.2f} PLN. Wielki format ({wielki_format_m2}m²): {wielki_format_m2*stawka_wielki_format:.2f} PLN. Hydroizolacja ({hydroizolacja_m2}m²): {hydroizolacja_m2*stawka_hydro:.2f} PLN. Łącznie robocizna: {koszt:.2f} PLN."

def wycen_prace_gipsowe_i_malarskie(gruntowanie_m2: float = 0, gladz_m2: float = 0, malowanie_m2: float = 0) -> str:
    stawka_grunt = 10.0
    stawka_gladz = 50.0
    stawka_malowanie = 25.0
    koszt = (gruntowanie_m2 * stawka_grunt) + (gladz_m2 * stawka_gladz) + (malowanie_m2 * stawka_malowanie)
    return f"WYCENA MALOWANIE/GIPSY: Gruntowanie ({gruntowanie_m2}m²): {gruntowanie_m2*stawka_grunt:.2f} PLN. Gładź ({gladz_m2}m²): {gladz_m2*stawka_gladz:.2f} PLN. Malowanie 2x ({malowanie_m2}m²): {malowanie_m2*stawka_malowanie:.2f} PLN. Łącznie robocizna: {koszt:.2f} PLN."

def oblicz_zuzycie_materialu(powierzchnia_m2: float, typ_materialu: str) -> str:
    typ = typ_materialu.lower().strip()
    if "farba" in typ:
        litry = (powierzchnia_m2 / 10.0) * 2
        return f"Zużycie farby na {powierzchnia_m2}m²: ok. {litry:.1f} l (koszt: {litry*45:.2f} PLN)."
    elif "gładź" in typ or "gladz" in typ:
        kg = powierzchnia_m2 * 1.2
        worki = kg / 20.0
        return f"Zużycie gładzi na {powierzchnia_m2}m²: ok. {kg:.1f} kg ({worki:.1f} worków 20kg, koszt: {worki*75:.2f} PLN)."
    elif "klej" in typ:
        kg = powierzchnia_m2 * 4.5
        worki = kg / 25.0
        return f"Zużycie kleju na {powierzchnia_m2}m²: ok. {kg:.1f} kg ({worki:.1f} worków 25kg, koszt: {worki*60:.2f} PLN)."
    return f"Brak przelicznika dla materiału: {typ_materialu}"

st.subheader("Wybierz przykładowe zlecenie:")
col1, col2 = st.columns(2)
opcja = None
if col1.button("📐 Łazienka (Płytki + Hydroizolacja)"):
    opcja = "Łazienka: 20 m2 płytki standardowe, 10 m2 hydroizolacji pod prysznicem. Podaj wycenę robocizny i ile kleju potrzeba."
if col2.button("🎨 Pokój (Gładź + Malowanie)"):
    opcja = "Remont pokoju: Ściany 40 m2. Potrzebne gruntowanie, gładź gipsowa oraz malowanie 2 razy. Oblicz koszty robocizny i materiału."

if opcja:
    with st.spinner("Agent wylicza wycenę..."):
        try:
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model='gemini-flash-lite-latest',
                contents=f"Przygotuj szczegółowy kosztorys robocizny i materiałów na podstawie zapytania:\n{opcja}",
                config=types.GenerateContentConfig(
                    system_instruction="Jesteś precyzyjnym kosztorysantem prac wykończeniowych.",
                    tools=[wycen_prace_glazurnicze, wycen_prace_gipsowe_i_malarskie, oblicz_zuzycie_materialu]
                )
            )
            st.success("Wycena gotowa!")
            st.markdown("---")
            st.markdown(response.text)
        except Exception as e:
            st.error(f"Wystąpił błąd: {e}")
