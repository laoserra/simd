import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
with open('./GIS_data/Scotland_Councils10_wgs84.geojson') as myfile:
    councils =  json.load(myfile)

print(councils['features'][0]['properties']['Name'])

df = pd.read_csv('deprv5_by_total.csv')
print(df.head())

data = [
    go.Choroplethmapbox(
        geojson=councils,
        locations=df['Council'],
        z=df['local_share'],
        featureidkey="properties.Name",
        marker_opacity=0.6,
        colorscale='Blues'
        )
    ]

layout = go.Layout(
    title='blabla',
    #xaxis='blabla',
    mapbox_style='carto-positron',#"open-street-map",
    mapbox_zoom=6,
    mapbox_center = {"lat": 57.834, "lon": -3.406},
    margin={"r":0,"t":0,"l":0,"b":0} # sets the margins in px. default:80
    )

fig = go.Figure(data=data, layout=layout)

fig.show()
