# Re-import necessary libraries after reset
import pandas as pd
import json
import folium
from folium import Choropleth, GeoJsonTooltip

# Load complaints data
complaints = pd.read_csv("/mnt/data/complaints.csv", parse_dates=["complaint_date"])

# Load geojson
with open("/mnt/data/custom.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# Extract month
complaints["month"] = complaints["complaint_date"].dt.to_period("M").astype(str)

# Aggregate total complaints per country (across all months)
country_counts = complaints['complaint_location_country'].value_counts().reset_index()
country_counts.columns = ['country', 'complaint_count']
complaint_lookup = dict(zip(country_counts['country'], country_counts['complaint_count']))

# Inject counts into geojson
for feature in geojson_data["features"]:
    name = feature["properties"].get("name")
    feature["properties"]["complaint_count"] = complaint_lookup.get(name, 0)

# Create folium map
m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")

# Add choropleth
Choropleth(
    geo_data=geojson_data,
    data=country_counts,
    columns=["country", "complaint_count"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Kaebuste arv riigi kohta"
).add_to(m)

# Add tooltips
folium.GeoJson(
    geojson_data,
    name="Kaebused",
    tooltip=GeoJsonTooltip(fields=["name", "complaint_count"], aliases=["Riik", "Kaebuste arv"])
).add_to(m)

# Save map
map_path = "/mnt/data/complaints_choropleth_map.html"
m.save(map_path)
map_path
