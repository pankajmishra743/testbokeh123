import json
import random
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt

from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, HoverTool, Select
from bokeh.layouts import widgetbox, row, column
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter
from bokeh.palettes import brewer


sns.set_style('dark')
fp = ('map/Indian_States.shp')
statedata = pd.read_csv('All State.csv')
map_df = gpd.read_file(fp)

# This dictionary contains the formatting for the data in the plots
format_data = [('MMR', 0, 400,'0,0', 'Maternal Mortality Rate'),
               ('IMR', 0, 56,'0,0', 'Infant Mortality Rate'),
               ('GDP_PC', 0, 481224,'₹ 0,0', 'Gross Domestic Product Per Capita')]
 
#Create a DataFrame object from the dictionary 
format_df = pd.DataFrame(format_data, columns = ['field' , 'min_range', 'max_range', 'format', 'verbage'])

# Create a function the returns json_data for the year selected by the user
def json_data(selectedYear):
    yr = selectedYear
    state_wise_AllData = statedata[['State', 'MMR', 'IMR', 'GDP_PC', 'Year']]
    df_yr = state_wise_AllData[state_wise_AllData['Year'] == yr]
    df_yr = df_yr.replace({'State': {"A & N Islands": "Andaman & Nicobar Island", "Arunachal Pradesh": "Arunanchal Pradesh","Dadra & Nagar Haveli": "Dadara & Nagar Havelli", "Delhi": "NCT of Delhi"}}).sort_values('State')
    merged = map_df.merge(df_yr, left_on = 'st_nm', right_on = 'State', how = 'left')
    merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data

# Define the callback function: update_plot
def update_plot(attr, old, new):
    # The input yr is the year selected from the slider
    yr = slider.value
    new_data = json_data(yr)
    
    # The input cr is the criteria selected from the select box
    cr = select.value
    input_field = format_df.loc[format_df['verbage'] == cr, 'field'].iloc[0]
    
    # Update the plot based on the changed inputs
    p = make_plot(input_field, str(yr))
    
    # Update the layout, clear the old document and display the new document
    layout1 = column(widgetbox(select), widgetbox(slider))
    layout = row(layout1, p)
    curdoc().clear()
    curdoc().add_root(layout)
    
    # Update the data
    geosource.geojson = new_data 
    
# Create a plotting function
def make_plot(field_name, current_Year):    
    # Set the format of the colorbar
    min_range = format_df.loc[format_df['field'] == field_name, 'min_range'].iloc[0]
    max_range = format_df.loc[format_df['field'] == field_name, 'max_range'].iloc[0]
    field_format = format_df.loc[format_df['field'] == field_name, 'format'].iloc[0]

    # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
    color_mapper = LinearColorMapper(palette = palette, low = min_range, high = max_range)
    # Create color bar.
    format_tick = NumeralTickFormatter(format=field_format)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=14, formatter=format_tick,
    border_line_color=None, location = (0, 0), major_tick_in = int(max_range/8))

    # Create figure object.
    verbage = format_df.loc[format_df['field'] == field_name, 'verbage'].iloc[0]

    p = figure(title = verbage + ' of Indian States for the Year - '+ current_Year, 
                 plot_height = 600, plot_width = 650,
                 toolbar_location = None)
    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None
    p.axis.visible = False

    # Add patch renderer to figure. 
    p.patches('xs','ys', source = geosource, fill_color = {'field' : field_name, 'transform' : color_mapper},
            line_color = 'black', line_width = 0.25, fill_alpha = 1)

    # Specify color bar layout.
    p.add_layout(color_bar, 'right')

    # Add the hover tool to the graph
    p.add_tools(hover)
    return p

# Input geojson source that contains features for plotting for:
# initial year 2018 and initial criteria sale_price_median
geosource = GeoJSONDataSource(geojson = json_data(2017))
input_field = 'MMR'

# Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]

# Reverse color order so that dark blue is highest value.
palette = palette[::-1]

# Add hover tool
hover = HoverTool(tooltips = [ ('Year','@Year'),
                               ('State/UT','@State'),
                               ('Maternal Mortality Rate', '@MMR'),
                               ('Infant Mortality Rate', '@IMR'),
                               ('GDP Per Capita', '₹@GDP_PC{,}')])

# Call the plotting function
p = make_plot(input_field, "2017")

# Make a slider object: slider 
slider = Slider(title = 'Year',start = 2017, end = 2019, step = 1, value = 2017)
slider.on_change('value', update_plot)

# Make a selection object: select
select = Select(title='Select Criteria:', value='Maternal Mortality Rate', options=['Maternal Mortality Rate', 'Infant Mortality Rate',
                                                                               'Gross Domestic Product Per Capita'])
select.on_change('value', update_plot)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
# Display the current document
layout1 = column(widgetbox(select), widgetbox(slider))
layout = row(layout1, p)
curdoc().add_root(layout)
curdoc().title = "IMR,MMR,GDP Plot"
