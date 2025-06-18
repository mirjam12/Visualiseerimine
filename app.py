import streamlit as st
import pandas as pd
import folium
from folium import Choropleth, GeoJsonTooltip
from streamlit_folium import st_folium
import json
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl

# Set consistent pink-themed style and font
mpl.rcParams['font.family'] = 'Comic Sans MS'
sns.set_style("whitegrid")
sns.set_palette(["#e75480", "#ffb6c1", "#ff69b4", "#db7093", "#ffc0cb"])

# Sidebar dropdown for view selection
view = st.sidebar.radio("Vali vaade:", ("Kaebuste kaart", "KPI graafikud", "Protsessi skeem"))

if view == "Kaebuste kaart":
    st.title("Kaebuste kaart")
    complaints = pd.read_csv("complaints.csv", parse_dates=["complaint_date"])
    with open("custom.geojson", "r") as f:
        geojson_data = json.load(f)

    complaints["complaint_location_country"] = complaints["complaint_location_country"].replace({
        "United States": "United States of America"
    })
    complaints["month"] = complaints["complaint_date"].dt.to_period("M").astype(str)

    country_counts = complaints['complaint_location_country'].value_counts().reset_index()
    country_counts.columns = ['country', 'complaint_count']
    lookup = dict(zip(country_counts['country'], country_counts['complaint_count']))

    for feature in geojson_data["features"]:
        name = feature["properties"].get("name")
        feature["properties"]["complaint_count"] = lookup.get(name, 0)

    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
    Choropleth(
        geo_data=geojson_data,
        data=country_counts,
        columns=["country", "complaint_count"],
        key_on="feature.properties.name",
        fill_color="PuRd",
        fill_opacity=0.9,
        line_opacity=0.2,
        legend_name="Kaebuste arv riigi kohta",
        bins=[1, 15, 50, 100, 150, 250],
        nan_fill_color="mistyrose",
    ).add_to(m)

    folium.GeoJson(
        geojson_data,
        tooltip=GeoJsonTooltip(fields=["name", "complaint_count"], aliases=["Riik", "Kaebused"])
    ).add_to(m)

    st_folium(m, width=800, height=500)

elif view == "KPI graafikud":
    st.title("KPI graafikud")

    KPI = pd.read_csv("KPIs.csv")
    KPI['Month'] = pd.to_datetime(KPI['Month'])
    KPI['Month'] = KPI['Month'].dt.to_period('M').dt.strftime('%Y-%m')

    # 1. Grouped bar chart by Region
    st.subheader("Stage1 Sissetulnud juhtimite arv kuude ja regioonide lõikes")
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=KPI,
        x='Month',
        y='Stage1_Received_Volume',
        hue='Region'
    )
    plt.xlabel('Kuu')
    plt.ylabel('Volüüm')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()

    # 2. Dual axis: Volume + QA Score
    st.subheader("Stage1 Kaebuste Volüüm ja QA Skoorid")
    KPI['Month_dt'] = pd.to_datetime(KPI['Month'], format='%Y-%m')
    monthly_data = KPI.groupby('Month_dt', as_index=False)[['Stage1_Received_Volume', 'Stage1_QA_Pass_Rate']].mean()
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(monthly_data['Month_dt'], monthly_data['Stage1_Received_Volume'], color='#ffc0cb', alpha=0.6)
    ax1.set_xlabel('Kuu')
    ax1.set_ylabel('Stage1 Vastuvõetud Volüüm', color='#db7093')
    ax1.tick_params(axis='y', labelcolor='#db7093')

    ax2 = ax1.twinx()
    ax2.plot(monthly_data['Month_dt'], monthly_data['Stage1_QA_Pass_Rate'], color='#e75480', marker='o')
    ax2.set_ylabel('Stage1 QA Hinnang (%)', color='#e75480')
    ax2.tick_params(axis='y', labelcolor='#e75480')
    plt.title('Stage1 Kaebuste Volüüm ja QA Skoorid (Keskmine, kuude lõikes)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.clf()

    # 3. Stage1 vs Stage2 Volume
    st.subheader("Stage1 vs Stage2 Kaebuste arv ajas")
    monthly_data_stage1 = KPI.groupby('Month_dt', as_index=False)[['Stage1_Received_Volume', 'Stage1_QA_Pass_Rate']].mean()
    monthly_data_stage2 = KPI.groupby('Month_dt', as_index=False)['Stage2_Received_Volume'].mean()
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.plot(monthly_data_stage1['Month_dt'], monthly_data_stage1['Stage1_Received_Volume'], color='#ff69b4', label='Stage1 Vastuvõetud Volüüm')
    ax1.set_xlabel('Kuu')
    ax1.set_ylabel('Volüüm', color='#ff69b4')
    ax1.tick_params(axis='y', labelcolor='#ff69b4')
    plt.xticks(rotation=45)
    ax1.plot(monthly_data_stage2['Month_dt'], monthly_data_stage2, color='#ffb6c1', label='Stage2 Vastuvõetud Volüüm')
    fig.suptitle('Stage1 ja Stage2 kaebuste arv ajas')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 0.9))
    fig.tight_layout()
    st.pyplot(fig)

elif view == "Protsessi skeem":
    st.title("📋 Protsessi skeem")
    st.image(
        "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEioVCDMcr_fAMpIbI95X_VNS1d3pnmFU5WPtNK5RnYXkIw-VBHvLDUXOz-wakFmeEhSdizASE8wKk_kyM8_KvaBniRDXMSyoiojNyjGSIeNYSQm_H4LM-WrxDjOzwYoJGA0kkC969ishwzA/s1600/2016-03-07_1624.png",
        caption="Protsessi skeem",
        use_column_width=True
    )
