import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df_ = pd.read_csv("./papers/datasets/one_shot_classif.csv")

authors = [df_.author.unique()[i] for i in [0,1,3]]
st.bar_chart(df_[df_.author== authors[0]], x= "author" ,  y="page_content" , color="category")

# Create container for subplots (optional for better layout)
st.container()
# Create 3 columns for side-by-side display
#authors = df_.author.unique()
authors = [str(df_.author.unique()[i]) for i in [0,1,2,3]]

#col1, col2, col3 = st.columns(len(authors))
cols = st.columns(len(authors))

with cols[0]:
        st.bar_chart(df_[df_.author==authors[0]], x= "author" ,  y="page_content" , color="category")
with cols[1]:
        st.bar_chart(df_[df_.author==authors[0]], x= "author" ,  y="page_content" , color="category")
with cols[2]:
        st.bar_chart(df_[df_.author== authors[0]], x= "author" ,  y="page_content" , color="category")


data_example = [
    ['Cat1', 5.3, None, None, None],
    ['Cat2', None, None, 12.1, None],
    ['Cat3', None, None, 3.4, 4.5],
    ['Cat4', None, 2.8, None, None],
]
df_example = pd.DataFrame(data_example
, columns=['A', 'B', 'C', 'D', 'E'])

fig, ax = plt.subplots()

df_example2 = df_[df_.author== authors[1]]

ax = df_example2.plot.bar(stacked=True)

st.set_option('deprecation.showPyplotGlobalUse', False)
col1, col2, col3 = st.columns(3)
#st.title('Matplotlib plot')
#st.pyplot()


from bokeh.plotting import figure, show

# generate some values
x = list(range(1, 50))
y = [pow(x, 2) for x in x]

# create a new plot
p = figure()
# add a line renderer and legend to the plot
p.line(x, y, legend_label="Temp.")
# show the results
#show(p)
#st.bokeh_chart(p)


#######################################################

fruits = ['Apples', 'Pears', 'Nectarines', 'Plums', 'Grapes', 'Strawberries']
years = ["2015", "2016", "2017"]
colors = ["#c9d9d3", "#718dbf", "#e84d60"]

data = {'fruits' : fruits,
        '2015'   : [2, 1, 4, 3, 2, 4],
        '2016'   : [5, 3, 4, 2, 4, 6],
        '2017'   : [3, 2, 4, 4, 5, 3]}

p = figure(x_range=fruits, height=250, title="Fruit Counts by Year",
           toolbar_location=None, tools="hover", tooltips="$name @fruits: @$name")

p.vbar_stack(years, x='fruits', width=0.9, color=colors, source=data,
             legend_label=years)
st.bokeh_chart(p)


from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool
data = df_#[df_.author == authors[0]]

# Extract data for separate bars (assuming "page_content" represents document size)
documents = data["page_content"].tolist()  # List of document sizes
categories = data["category"].tolist()  # List of categories

placeholder = "No data"  # Choose an appropriate placeholder
categories = [category if not pd.isna(category) else placeholder for category in categories]

# Create a single document size (all bars will have this height)
# You can adjust this value based on your needs
document_size = 10  # Replace with the desired height

# Create a ColumnDataSource
source = ColumnDataSource(data=dict(documents=documents, categories=categories, document_size=[document_size] * len(documents)))

# Create the Bokeh figure
p = figure(x_range=categories, y_range=(0, document_size + 1))  # Adjust y-axis range slightly

# Create stacked bars with color based on category
p.vbar_stack("documents", x="categories", source=source, color="categories", legend_label=categories)

# Optional: Add hover tool to display document size on hover
hover = HoverTool()
hover.tooltips = [("Category", "@categories"), ("Document size", "@documents")]
p.add_tools(hover)

# Display the plot
st.bokeh_chart(p)