import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import json
with open('./GIS_data/Scotland_Councils10_wgs84.geojson') as myfile:
    councils =  json.load(myfile)

df = pd.read_csv('./Derived_Data/SIMD_2020_Ranks_and_Domain_Ranks.csv')

# Launch the application
app=dash.Dash()

#returns a series with the total counts of datazones per council
datazones_per_council = df.Council_area.value_counts()
datazones_per_council.rename('Total_datazones', inplace=True)

# deprivation options for dropdown boxes
deprv_features = ['20% least deprived',
                  '5% most deprived',
                  '10% most deprived',
                  '15% most deprived',
                  '20% most deprived',
                  '30% most deprived',
                  '40% most deprived']
deprv_options = [{'label': i, 'value': i} for i in deprv_features]

# domain options for dropdown boxes
domain_options = [{'label': i.replace('_', ' '), 'value': i}
                  for i in df.columns[2:]]

# share options for dropdown boxes
share_options = [{'label': 'local share', 'value': 'local_share'},
                 {'label': 'national share', 'value': 'national_share'}]

# Dash layout with several components: Div,Graph and Dropdown
app.layout = html.Div([
    html.Div(
        id='my-div',
        children=[
            dcc.Graph(id='bar_share', figure=dict(data=[], layout={})),
            dcc.Graph(id='map', figure=dict(data=[], layout={}))
        ]
    ),
    dcc.Dropdown(id='deprv_label', options=deprv_options, value='5% most deprived'),
    dcc.Dropdown(id='domain_rank', options=domain_options, value='SIMD2020_Rank'),
    dcc.Dropdown(id='share_label', options=share_options, value='local_share')
])

# Create a Dash callback with three inputs and two outputs

@app.callback([Output('bar_share', 'figure'),
               Output('map', 'figure')],
              [Input('deprv_label', 'value'),
               Input('domain_rank', 'value'),
               Input('share_label', 'value')])
def update_figures(deprv_label, domain_rank, share_label):

    # filters a subdataframe based on the chosen deprivation label
    # rounded values. The official values are floored
    if deprv_label == '20% least deprived':
        deprv_by_domain = df.nlargest(round(6976 * 20 / 100), domain_rank)
    else:
        deprv_level = deprv_label[:deprv_label.find('%')]
        deprv_level = int(deprv_level)
        deprv_by_domain = df.nsmallest(round(6976 * deprv_level / 100),
                                        domain_rank)

    # returns a series with the domain/depr level's counts of dz per council
    domain_dz_per_council = deprv_by_domain.Council_area.value_counts()
    domain_dz_per_council.rename(deprv_label, inplace=True)

    # dataset for the chosen domain/depr level with local and national shares
    df_domain = pd.concat([datazones_per_council, domain_dz_per_council],
                          axis=1)
    df_domain.fillna(0, inplace=True)
    df_domain = df_domain.astype('int64')

    if share_label == 'local_share':
        df_domain[share_label] = df_domain[deprv_label]* 100 / \
                                 df_domain['Total_datazones']
    else:
        df_domain[share_label] = df_domain[deprv_label] * 100 / \
                                  df_domain[deprv_label].sum()

    df_domain = df_domain.round({share_label: 1})
    df_domain.sort_values(by=share_label, ascending=False, inplace=True)
#-------------------------------------------------------------------------------
#######
# This is a grouped bar chart showing two traces
# (national and local shares) for each Council
######
    data = [go.Bar(
        x = df_domain.index,
        y = df_domain[share_label],
        name = share_label.replace('_', ' '),
        marker_color='rgb(26, 118, 255)'
    )]

    layout = go.Layout(
        title = dict(text='SIMD 2020 - local and national share by Council\
                     <br><sub><b>Deprivation level:</b> {}\
                     <b>Domain rank:</b> {}\
                     <b>Share:</b> {}</sub></br>'\
                     .format(deprv_label, domain_rank, share_label)
                     ),
        yaxis=dict(ticksuffix="%")
    )

    data1 = [
        go.Choroplethmapbox(
            geojson=councils,
            locations=df_domain.index,
            z=df_domain[share_label],
            featureidkey="properties.Name",
            marker_opacity=0.6,
            colorscale='Blues'
            )
        ]

    layout1 = go.Layout(
        #title='blabla',
        #xaxis='blabla',
        mapbox_style='carto-positron',#"open-street-map",
        mapbox_zoom=6,
        mapbox_center = {"lat": 57.834, "lon": -3.406},
        margin={"r":0,"t":0,"l":0,"b":0} # sets the margins in px. default:80
        )
    return [{'data': data, 'layout': layout},
            {'data': data1, 'layout': layout1}]

#-------------------------------------------------------------------------------
# server clause
if __name__ == '__main__':
    app.run_server(debug=True)
