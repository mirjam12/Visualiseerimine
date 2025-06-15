import streamlit as st
import pandas as pd
import folium
from folium import Choropleth, GeoJsonTooltip
from streamlit_folium import st_folium
import json

# Load data
complaints = pd.read_csv("complaints.csv", parse_dates=["complaint_date"])
with open("custom.geojson", "r") as f:
    geojson_data = json.load(f)

# Preprocess
# Replace country name to match GeoJSON
complaints["complaint_location_country"] = complaints["complaint_location_country"].replace({
    "United States": "United States of America"
})

complaints["month"] = complaints["complaint_date"].dt.to_period("M").astype(str)
country_counts = complaints['complaint_location_country'].value_counts().reset_index()
country_counts.columns = ['country', 'complaint_count']
lookup = dict(zip(country_counts['country'], country_counts['complaint_count']))

# Inject counts into geojson
for feature in geojson_data["features"]:
    name = feature["properties"].get("name")
    feature["properties"]["complaint_count"] = lookup.get(name, 0)

# Create map
m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
Choropleth(
    geo_data=geojson_data,
    data=country_counts,
    columns=["country", "complaint_count"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",
    fill_opacity=0.9,
    line_opacity=0.2,
    legend_name="Kaebuste arv riigi kohta",
    bins=[1, 15, 50, 100, 150, 250],  # You can tweak these manually
    nan_fill_color="lightgray",
).add_to(m)


folium.GeoJson(
    geojson_data,
    tooltip=GeoJsonTooltip(fields=["name", "complaint_count"], aliases=["Riik", "Kaebused"])
).add_to(m)

# Render in Streamlit
st.title("Kaebuste kaart")
st_data = st_folium(m, width=800, height=500)
