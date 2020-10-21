#!/usr/bin/env python
# coding: utf-8

# In[10]:


import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

@st.cache(persist=True)
def load_data(path):
	weather=pd.read_csv(path)
	weather['date']=weather['date'].astype('str')
	weather['date']= pd.to_datetime(weather['date'], format='%Y%m%d')
	weather['month'] = pd.DatetimeIndex(weather['date']).month
	weather = weather.rename(columns={"PRCP": "Precipitation (inch)", "SNOW": "Snowfall (inch)", "SNWD": "Snow depth (inch)", "TMAX": "Maximum temperature (F)","TMIN": "Minimum temperature (F)", "TAVG": "Average temperature (F)","AWND": "Average daily wind speed (miles / hour)", "WSF5": "Fastest 5-second wind speed (miles / hour)", "WDF5": "Direction of fastest 5-second wind (degrees)"})
	return weather

weather=load_data("weather.csv")

#part0: map of our stations
st.title("Locations of our data gathering stations")

weather1 = weather[weather['state'] != 'MP']
weather1 = weather1[weather1['state'] != 'GU']
st.map(weather1[['latitude','longitude']],1.7)

#part1: a table with average temperature, windspeed snow, precipitation elevation, for each state, cna choose time range
st.title("Average measurement for each state")

table_weather=weather[['state','elevation','Average temperature (F)','Average daily wind speed (miles / hour)','Snowfall (inch)', "Snow depth (inch)",'Precipitation (inch)','month']]
table_weather=table_weather.dropna(subset=['month'])
table_weather['month'] = table_weather['month'].astype(int) 

#choose measurement
cols = ['state','elevation','Average temperature (F)','Average daily wind speed (miles / hour)', "Snow depth (inch)",'Snowfall (inch)','Precipitation (inch)']
st_ms = st.multiselect("Please select measurements of your interest", table_weather.columns.tolist(), default=cols)
 
#choose month
months = st.slider("Please select range of month of your interest", min(table_weather.month), max(table_weather.month), (min(table_weather.month),max(table_weather.month)))
table_weather=table_weather[(table_weather['month']<=months[1]) & (table_weather['month']>=months[0])]

#choose state
states = table_weather['state'].unique()
st_state = st.multiselect("Please select state of your interest", states)

table_weather=table_weather[st_ms]

mask_states = table_weather['state'].isin(st_state)
table_weather = table_weather[mask_states]

st.table(table_weather.groupby("state").mean())


#part 2: a lineplot with average over 12 months
st.title("Average measurement for each month")

table_month=weather[['Average temperature (F)','Minimum temperature (F)','Maximum temperature (F)',\
'Average daily wind speed (miles / hour)','Snowfall (inch)', "Snow depth (inch)",'Precipitation (inch)',\
'Fastest 5-second wind speed (miles / hour)','Direction of fastest 5-second wind (degrees)','month']]
table_month=table_month.dropna(subset=['month'])
table_month['month'] = table_month['month'].astype(int) 

#choose measurement
option = st.selectbox(
    'Which measurement are you interested in for month?',
     ['Average temperature (F)','Minimum temperature (F)','Maximum temperature (F)',\
'Average daily wind speed (miles / hour)','Snowfall (inch)', "Snow depth (inch)",'Precipitation (inch)',\
'Fastest 5-second wind speed (miles / hour)','Direction of fastest 5-second wind (degrees)'])

table_month = table_month[[option,"month"]].groupby("month").mean().reset_index()

line = alt.Chart(table_month).mark_line().encode(    
	alt.Y(option, scale=alt.Scale(zero=False)),    
	alt.X("month", scale=alt.Scale(zero=False)),    
)

st.write(line)


#part 3 average measurement for different elevation
st.title("Average measurement for different elevation")

table_elevation=weather[['Average temperature (F)','Minimum temperature (F)','Maximum temperature (F)',\
'Average daily wind speed (miles / hour)','Snowfall (inch)', "Snow depth (inch)",'Precipitation (inch)',\
'Fastest 5-second wind speed (miles / hour)','Direction of fastest 5-second wind (degrees)','elevation']]
table_elevation=table_elevation.dropna(subset=['elevation'])

#choose measurement
option = st.selectbox(
    'Which measurement are you interested in for elevation?',
     ['Average temperature (F)','Minimum temperature (F)','Maximum temperature (F)',\
'Average daily wind speed (miles / hour)','Snowfall (inch)', "Snow depth (inch)",'Precipitation (inch)',\
'Fastest 5-second wind speed (miles / hour)','Direction of fastest 5-second wind (degrees)'])

table_elevation = table_elevation[[option,"elevation"]]

table_elevation=table_elevation.groupby(pd.cut(table_elevation["elevation"], np.arange(min(table_elevation["elevation"]), max(table_elevation["elevation"]), 500))).mean().reset_index(drop=True)
table_elevation['elevation']=(table_elevation['elevation']//500*500).astype(int).astype(str)+"-"+(table_elevation['elevation']//500*500+500).astype(int).astype(str)
bar = alt.Chart(table_elevation).mark_bar().encode(    
	alt.Y(option, scale=alt.Scale(zero=False)),    
	alt.X("elevation", scale=alt.Scale(zero=False)),    
).properties(width=600,height=400)

st.write(bar)

#part 4 top 10 states
st.title("Top 10 states to travel to!")
option1 = st.selectbox(
    'Which month are you planning to travel?',
     range(min(weather.month),max(weather.month)+1))
sc = weather[weather['month'] == option1]
sc = sc[['state','Precipitation (inch)','Average temperature (F)']]
sc = sc.groupby(['state'], as_index=False).mean()

option2 = st.selectbox(
    'What is the ideal average temperature (F) for you?',
     range(int(min(sc['Average temperature (F)'])),int(max(sc['Average temperature (F)']))))
option3 = st.selectbox(
    'What is the ideal average precipitation (inch) for you?',
     np.arange(0,round(max(sc['Precipitation (inch)']),2),0.01))


sc['score'] = abs(sc['Average temperature (F)']-option2)+abs(sc['Precipitation (inch)']-option3)*100
sc = sc.sort_values(by=['score'], ascending=[True]).head(10)
sc = sc[['state','Precipitation (inch)','Average temperature (F)']]

scatter_chart = st.altair_chart(
    alt.Chart(sc)
        .mark_circle(size=60)
        .encode(x='Average temperature (F)', y='Precipitation (inch)', color='state')
        .interactive()
)