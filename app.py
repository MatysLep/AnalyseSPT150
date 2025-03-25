import streamlit as st
import pandas as pd
from datetime import datetime


measure_units = {0:"mg/m3" , 1:"g/m3", 2:"µg/m3", 3:"%"}


st.set_page_config(
    page_title="Analyse du SPT150",
    page_icon="🔍",
    layout="wide"
)

st.title("Analyse du SPT150")
uploaded_file = st.file_uploader("Choisir un fichier csv", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding="UTF-16", delimiter="\t", skiprows=1)
    unit = measure_units[df['Unité de mesure'].iloc[0]]

    df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Heure'], dayfirst=True)
    df.set_index('Datetime', inplace=True)
    df.index = df.index.strftime('%d/%m/%Y %H:%M:%S')
    df['DateTimeFormat'] = pd.to_datetime(df['Date'] + ' ' + df['Heure'], dayfirst=True)

    df['Heure'] = pd.to_datetime(df['Heure'], format='%H:%M:%S').dt.time

    df['DateFormat'] = pd.to_datetime(df['Date'])
    df['Date'] = pd.to_datetime(df['Date'])
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

    # Variable

    col_to_display = ['Date', 'Heure','Mesure instantannée','Mesure moyennée sur 1 min.','Mesure moyennée sur X min.']



    st.divider()

    st.write(f"Analyse des données disponible entre **{df.index[0]}** et **{df.index[-1]}**.")
    col1,col2 = st.columns(2)
    start_date = col1.date_input("Date de Début", value=df["DateFormat"].iloc[0], min_value=df["DateFormat"].iloc[0], max_value=df["DateFormat"].iloc[-1], format="DD/MM/YYYY")
    start_time = col1.time_input("Heure de début", value="00:00")
    end_date = col2.date_input("Date de Fin", value=df["DateFormat"].iloc[-1], min_value=start_date, max_value=df["DateFormat"].iloc[-1], format="DD/MM/YYYY")
    end_time = col2.time_input("Heure de Fin", value="23:59")

    colSeuil1, colSeuil2 = st.columns(2)
    with_seuil = colSeuil1.toggle("Avec valeur de seuil")



    start_datetime = datetime.combine(start_date, start_time)
    end_datetime = datetime.combine(end_date, end_time)
    df_filtered = df[(df['DateTimeFormat'] >= start_datetime) & (df['DateTimeFormat'] <= end_datetime)]

    st.divider()

    st.write("## Visualisation des données")
    st.dataframe(df_filtered[col_to_display])

    st.divider()

    moyenne_value = df_filtered['Mesure moyennée sur 1 min.'].mean().round(3)
    dernier_facteur = df_filtered['Facteur de calibration'].iloc[-1]
    facteur_utilise = 1 if dernier_facteur == 0 else dernier_facteur
    valeur_ref = (moyenne_value / facteur_utilise).round(3)

    if with_seuil:
        num_seuil = colSeuil2.number_input("Valeur du seuil ")
        nb_seuil_depasse = df_filtered[df_filtered['Mesure instantannée'] > num_seuil]['Mesure instantannée'].count()


    # Partie sur les statistiques

    st.write("## Statistiques")
    col3,col4 = st.columns(2)
    col3.write(f"**Moyenne des mesures moyennées sur 1 min :** {moyenne_value} {unit}")
    col4.write(f"**Valeur de référence pour calibration manuelle :** {valeur_ref}")

    if with_seuil:
        st.write(f"**Nombre de fois où le seuil est dépassé :** {nb_seuil_depasse}")

    st.divider()

    # Partie sur les graphes

    chart_data = df_filtered[[
        'Mesure instantannée',
        'Mesure moyennée sur 1 min.',
        'Mesure moyennée sur X min.'
    ]]
    st.line_chart(data=chart_data.tail(10000))