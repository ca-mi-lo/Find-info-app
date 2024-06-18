import streamlit as st
import pandas as pd
import numpy as np

from pathlib import Path
from collections import OrderedDict

import find_info_app

'''
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure, show
import bokeh.palettes as palettes
from bokeh.models import Legend, Label

df_ = pd.read_csv("./papers/datasets/one_shot_classif.csv")


def prepare_data():
    df2 = df_.copy().filter(['source', 'author','category','racional','page_content'])
    df2["file_name"]= df2.source.apply(lambda x: Path(x).name)
    df2 = df2.groupby(['file_name', 'category'])\
            [['page_content']]\
            .count().rename({'page_content':'counts'},axis=1)\
            .reset_index(['file_name', 'category'])

    df3 = df2.pivot(columns=['category'],index=['file_name']).droplevel(None, axis= 1)
    df3.index = [name[:-10] for name in df3.index] # sin terminación ", aaaa.pdf"

    column_names = df3.columns.to_list()
    data = {'index': df3.index.to_list(),
        **{col: df3[col].fillna(0).to_list() for col in column_names}  # Dictionary unpacking
    }
    source = ColumnDataSource(data)


n_catego = len(column_names)
original_palette = palettes.Category20[n_catego]
gray_color = "#F0F0F0" #"#E0E0E0"
category_colors = {
    category: color
    for category, color in zip(column_names, original_palette)
    if category != "Metadatos"
}
category_colors["Metadatos"] = gray_color
custom_palette = tuple(category_colors[category] for category in OrderedDict(sorted(category_colors.items())))

#mapper = factor_cmap('category', palette="Category10_8", factors=column_names) 
source = ColumnDataSource(data)

p = figure(x_range= data.get('index'))
#p.plot_height=400
#p.plot_width=1000

p.legend.orientation = "horizontal"
p.add_layout(Legend(), place='right')  #'below'
p.xaxis.major_label_orientation = -45
p.xaxis.major_label_text_align='center'
p.legend.click_policy='hide' #"mute" 

p.vbar_stack(
    stackers=column_names, 
    x='index', 
    source=source,
    color = custom_palette,
    legend_label = [cat[:39] for cat in column_names]
    )
st.bokeh_chart(p)
'''

#####################################################################################

class DataProcessor:
    def __init__(self, path):
        self.path = path
        #self.df = None

    def read_file(self):
        try:
            df = pd.read_csv(self.path)
            print(f'File read: {self.path}')
        except:
            df = pd.read_csv("./papers/datasets/one_shot_classif.csv")
            print(f'Default file loaded: "./papers/datasets/one_shot_classif.csv"')

    def df_pivoted(self):
        df2 = self.df.copy().filter(['source', 'author','category','racional','page_content'])
        df2["file_name"]= df2.source.apply(lambda x: Path(x).name)
        df2 = df2.groupby(['file_name', 'category'])\
            [['page_content']]\
            .count().rename({'page_content':'counts'},axis=1)\
            .reset_index(['file_name', 'category'])\
            .pivot(columns=['category'],index=['file_name']).droplevel(None, axis= 1)

        
    