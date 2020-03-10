import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html

df = pd.read_csv('./Derived_Data/SIMD_2020_Ranks_and_Domain_Ranks.csv')

#print(df.dtypes)

#returns a series with the total counts of datazones per council
datazones_per_council = df.Council_area.value_counts()
datazones_per_council.rename('Total_datazones', inplace=True)

#5% most deprived - rounded value. The official values are floored
deprv5_by_health = df.nsmallest(round(6976 * .05), 'SIMD2020_Health_Domain_Rank')

# returns a series with the domain/depr level's counts of dz per council
health5_dz_per_council = deprv5_by_health.Council_area.value_counts()
health5_dz_per_council.rename('5%_most_deprived', inplace=True)

# dataset for the chosen domain/depr level with local and national shares
df_health = pd.concat([datazones_per_council, health5_dz_per_council], axis=1)
df_health.fillna(0, inplace=True)
df_health = df_health.astype('int64')
df_health.sort_values(by=['5%_most_deprived'], ascending=False, inplace=True)
df_health['local_share'] = df_health['5%_most_deprived']* 100 / \
                           df_health['Total_datazones']
df_health['national_share'] = df_health['5%_most_deprived'] * 100 / \
                              df_health['5%_most_deprived'].sum()

df_health = df_health.round({'local_share': 1, 'national_share': 1})
print(df_health)

#-------------------------------------------------------------------------------
#######
# This is a grouped bar chart showing two traces
# (national and local shares) for each Council
######

trace1 = go.Bar(
    x = df_health.index,
    y = df_health.national_share,
    name = 'National share',
    marker_color='rgb(26, 118, 255)'
)

trace2 = go.Bar(
    x = df_health.index,
    y = df_health.local_share,
    name = 'Local share',
    marker_color='rgb(55, 83, 109)'
)

data = [trace1, trace2]
layout = go.Layout(
    title = dict(text='SIMD 2020 - local and national share by Council \
                 <br><sub><b>Deprivation level:</b> 5% most deprived; \
                 <b>Domain rank:</b> Health</sub>'),
    barmode = 'group',
    yaxis=dict(ticksuffix="%")
)
fig = go.Figure(data=data, layout=layout)

fig.show()
#-------------------------------------------------------------------------------
#Dash

app=dash.Dash()

app.layout = html.Div([
    dcc.Graph(
        id='bar_share',
        figure=dict(data=data, layout=layout)
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
