# Import Library
import pandas as pd
import numpy as np
import streamlit as st
import datetime

# Loading data set
df = pd.read_excel("nuclear_explosions.xlsx")

# checking Null values
df.isnull().sum()

# Creating dictionary For rename header
df = df.rename(columns={
   "Data.Source": "Source",
   "Location.Cordinates.Latitude": "Latitude",
   "Location.Cordinates.Longitude": "Longitude",
   "Data.Magnitude.Body": "Magnitude_Body",
   "Data.Magnitude.Surface": "Magnitude_Surface",
   "Location.Cordinates.Depth": "Depth",
   "Data.Yeild.Lower": "Yeild_Lower",
   "Data.Yeild.Upper": "Yeild_Upper",
   "Data.Purpose": "Purpose",
   "Data.Name": "Name",
   "Data.Type": "Type",
   "Date.Day": "Day",
   "Date.Month": "Month",
   "Date.Year": "Year"
})

print(df.head(5))



# Extract Week number of year from date
df['Date'] = pd.to_datetime(df[['Day', 'Month', 'Year']])
df['Week_of_Year'] = df['Date'].dt.isocalendar().week

# Dispaly data set
st.title("Nuclear Explosions(1945 - 1998) Analysis")
st.write("An Overview of the Dataset")
st.write(df.head())

# Side bar
st.sidebar.title("Filter Option")
location = df['WEAPON DEPLOYMENT LOCATION']
select_location = st.sidebar.multiselect("Select Deployment Location",location,default=["Hiroshima"])

#year
year_min =int(df['Year'].min())
year_max =int(df['Year'].max())
year_range = st.sidebar.slider("Year Range",year_min,year_max,(year_max,year_min))

# yeild
yield_min = int(df['Yeild_Lower'].min())
yield_max = int(df['Yeild_Lower'].max())
yield_range = st.sidebar.slider("Yeild Range",yield_max,yield_min,(yield_min,yield_max))

#Depth Selection
depth_selction = ["Above Ground", "Underground","All"]
select_depth = st.sidebar.radio("Select Depth",depth_selction)

# Part secound 
def filter_data(df,location,year_range,yield_range,depth):
    filter_data = df[df["WEAPON DEPLOYMENT LOCATION"].isin(location)]
    
    filter_data = filter_data[(filter_data["Year"]>=year_range[0])&
                                (filter_data["Year"]<=year_range[1])]
    
    
    filter_data = filter_data[(filter_data["Yeild_Lower"]>=yield_range[0])&
                                (filter_data["Yeild_Lower"]<=yield_range[1])]
    
    if depth != "All":
        if depth == "Above Ground":
            filter_data = filter_data[filter_data['Depth'] < 0]
        elif depth == "Underground":
            filter_data = filter_data[filter_data['Depth'] > 0]
    return filter_data

filter_data = filter_data(df,select_location,year_range,yield_range,select_depth)
st.write("Filtered Data",filter_data)

# Ploting
import matplotlib.pyplot as plt

st.subheader("number Of Nuclear Explosions by Deployment Location")

if filter_data.empty:
    st.write("No Data Available")
else:
    location_count = filter_data['WEAPON DEPLOYMENT LOCATION'].value_counts()

    fig, ax = plt.subplots()
    location_count.plot(kind = 'bar',ax = ax)
    ax.set_ylabel("Number of Explosions")
    ax.set_title("Nucler Explosions by deployment Location")
    st.pyplot(fig)
    
    
# Line plot
import  plotly.express as px

st.subheader("Yeild of Nuclear Explosions Over Time")
fig = px.line(filter_data, x= "Year",y = "Yeild_Upper",color = 'WEAPON DEPLOYMENT LOCATION',title = "Yield of Nuclears Explosion Over time")
fig.update_layout(yaxis_title = "yield")
st.plotly_chart(fig)
        
    
 # pie plot
st.subheader("Distributions of Explosion Purposes")
purpose_count = filter_data['Purpose'].value_counts()
fig = px.pie(names=purpose_count.index,values=purpose_count,title="Explosion Purpses Distrubution")
st.plotly_chart(fig)

# Map Disply
from streamlit_folium import st_folium
import folium
st.subheader("Geographical distribution of Nuclear Explosions")
if filter_data.empty:
    st.write("No Data Available")
else:
    map_center = [20,0]
    m = folium.Map(location=map_center, zoom_start=2)
    for _, row in filter_data.iterrows():
        folium.Marker(
            location = [row['Latitude'],row['Longitude']],
            popup = f"{row["Name"]} - Yield{row['Yeild_Upper']}kt",
            icon = folium.Icon(color = "blue"if row['Depth']< 0 else "blue")
            ).add_to(m)
        
    st_folium(m,width=700,key = "unique_map_for_explosions")

# Download Csv
csv = filter_data.to_csv(index = False)
st.download_button(f"Download Filtered Data  as csv", data =csv ,file_name="Filtered_Data",mime = 'text/csv')

# Add error handling to prevent issues when loading or filtering data.

try:
    data = pd.read_excel("nuclear_explosions.xlsx")
except FileNotFoundError:
    st.error("The data file could not be found.")
except Exception as e:
    st.error(f"An error occurred: {e}")