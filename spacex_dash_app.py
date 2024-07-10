import pandas as pd
import dash
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv')
launch_sites_list = spacex_df['Launch Site'].unique().tolist()

# Create a dash application
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Get the layout of the application and adjust it.
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center',
                   'color': '#503D36',
                   'font-size': 24}),
    
    # Dropdown to select launch site
    html.Div([
        dcc.Dropdown(id='site-dropdown',
                     options=[{'label': 'All Sites', 'value': 'ALL'}] +
                             [{'label': site, 'value': site} for site in launch_sites_list],
                     value='ALL',  # Default value
                     placeholder='Select a Launch Site here',
                     searchable=True,
                     style={'width': '80%',
                            'font-size': '20px'})
    ], style={'display': 'flex', 'justify-content': 'center'}),
    
    # Pie chart for success vs failure counts
    html.Div([
         dcc.Graph(id='success-pie-chart',
                  className='chart-grid',
                  style={'display': 'flex',
                         'flex-direction': 'column',
                         'align-items': 'center'}
                  )
    ]),
    
    # Range slider for payload selection
    html.Div([
        dcc.RangeSlider(id='payload-slider',
                        min=0, max=10000, step=1000,
                        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                        value=[0, 10000]
        ),
        html.Div(id='output-container-range-slider')
    ]),
    
    # Scatter plot for success vs payload
    html.Div([
        dcc.Graph(id='success-payload-scatter-chart',
                  className='chart-grid',
                  style={'display': 'flex',
                         'flex-direction': 'column',
                         'align-items': 'center'}
                  )
    ])
])

# Callback function to update both charts
@app.callback(
    [Output(component_id='success-pie-chart', component_property='figure'),
     Output(component_id='success-payload-scatter-chart', component_property='figure')],
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_charts(entered_site, payload_range):
    if entered_site == 'ALL':
        # Pie chart for all sites
        data_pie = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig_pie = px.pie(data_pie, values='class', names='Launch Site', title='Total Successful Launches by Site')
        
        # Scatter plot for all sites
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig_scatter = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                                 title='Payload Success Rate for All Launch Sites')
    else:
        # Pie chart for selected site
        data_pie = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_count = data_pie[data_pie['class'] == 1].shape[0] # Success is represented by 1
        failure_count = data_pie[data_pie['class'] == 0].shape[0] # Failure is represented by 0
        fig_pie = px.pie(values=[success_count, failure_count], names=['Success', 'Failure'],
                         title=f'Total Launch Outcomes for site {entered_site}')
        
        # Scatter plot for selected site
        filtered_df = spacex_df[(spacex_df['Launch Site'] == entered_site) &
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        fig_scatter = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                                 title=f'Payload Success Rate for {entered_site}')
    
    fig_scatter.update_layout(xaxis_title='Payload Mass (kg)', yaxis_title='Class (1: Success, 0: Failure)')
    
    return fig_pie, fig_scatter

if __name__ == '__main__':
    app.run_server()
