# utils/map_utils.py
import pandas as pd
import folium
import plotly.express as px

def load_metadata(csv_path):
    return pd.read_csv(csv_path)

def generate_map(df):
    # Create a Folium map centered globally
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    for _, row in df.iterrows():
        popup = f"Sample: {row['SampleID']}<br>Mutations: {row['MutationCount']}"
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=6,
            color='red',
            fill=True,
            fill_opacity=0.7,
            popup=popup
        ).add_to(m)
    
    return m._repr_html_()

def generate_timeline(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df_sorted = df.sort_values('Date')
    
    fig = px.line(df_sorted, x='Date', y='MutationCount', hover_name='SampleID',
                  title='Mutation Accumulation Over Time')
    
    return fig.to_html(full_html=False)
