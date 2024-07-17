# Import required libraries
import pandas as pd
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Calculate max and min payload for the payload slider
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    html.Br(),

    # Dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                 ],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True
                 ),
    html.Br(),

    # Pie chart to show the total successful launches count for all sites or a specific site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # Slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=int(min_payload),
                    max=int(max_payload),
                    step=1000,
                    marks={i: str(i) for i in range(int(min_payload), int(max_payload)+1, 1000)},
                    value=[int(min_payload), int(max_payload)]
                    ),
    html.Br(),

    # Scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback function to update the pie chart based on site selection
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(spacex_df, values='class',
                     names='Launch Site',
                     title='Total Success Launches for All Sites')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(filtered_df, names='class',
                     title=f'Success vs. Failure for {selected_site}')

    return fig

# Callback function to update scatter chart based on site selection and payload range
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Launch Site',
                         title='Payload Success Rate for All Sites',
                         labels={'class': 'Success'}
                         )
    else:
        filtered_site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(filtered_site_df, x='Payload Mass (kg)', y='class',
                         title=f'Payload Success Rate for {selected_site}',
                         labels={'class': 'Success'}
                         )

    fig.update_layout(xaxis_title='Payload Mass (kg)', yaxis_title='Success')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
