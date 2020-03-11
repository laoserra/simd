import pandas as pd
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

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


# Dash layout with several components: Div,Graph and Dropdown
app.layout = html.Div([
    dcc.Graph(id='bar_share'),
    dcc.Dropdown(id='deprv_label', options=deprv_options, value='5% most deprived'),
    dcc.Dropdown(id='domain_rank', options=domain_options, value='SIMD2020_Rank')
])

# Create a Dash callback with two inputs
@app.callback(Output('bar_share', 'figure'),
              [Input('deprv_label', 'value'),
               Input('domain_rank', 'value')])
def update_figure(deprv_label, domain_rank):

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
    df_domain['local_share'] = df_domain[deprv_label]* 100 / \
                               df_domain['Total_datazones']
    df_domain['national_share'] = df_domain[deprv_label] * 100 / \
                                  df_domain[deprv_label].sum()

    df_domain = df_domain.round({'local_share': 1, 'national_share': 1})
    df_domain.sort_values(by='local_share', ascending=False, inplace=True)
    print(df_domain)
    #df_domain.to_csv('deprv5_by_total.csv', index_label='Council')

#-------------------------------------------------------------------------------
#######
# This is a grouped bar chart showing two traces
# (national and local shares) for each Council
######
    trace1 = go.Bar(
        x = df_domain.index,
        y = df_domain.national_share,
        name = 'National share',
        marker_color='rgb(26, 118, 255)'
    )

    trace2 = go.Bar(
        x = df_domain.index,
        y = df_domain.local_share,
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

    return {
        'data': data,
        'layout': layout
    }

#-------------------------------------------------------------------------------
# server clause
if __name__ == '__main__':
    app.run_server(debug=True)
