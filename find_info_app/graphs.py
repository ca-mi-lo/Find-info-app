import streamlit as st
import pandas as pd
import numpy as np

from pathlib import Path
from collections import OrderedDict

import find_info_app

from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure, show
import bokeh.palettes as palettes
from bokeh.models import Legend, Label
#pip install --force-reinstall --no-deps bokeh==2.4.3

############################################################
class Prepare_plot():
    def __init__(self, path = "./papers/datasets/one_shot_classif.csv",  skip_metadata=True):
        print("Reading csv..")
        self.path = path
        self.skip_metadata = skip_metadata
        try:
            self.df = pd.read_csv(path)
            print("Read successfully")
            self.head_df(n=3)
        except:
            print("Pending: Add debugger")
            print(path)
    
        finally:
            self.pivot_df()

    def filter_metadata(self, skip_metadata=True):
            """Filters data based on skip_metadata flag."""
            if skip_metadata:
                self.df = self.df[self.df.category != 'Metadatos']
                self.df = self.df[self.df.category != 'Introducción']
            return self.df

    def head_df(self,n=1):
        print(self.df.head(n))
    
    def pivot_df(self):
        self.df2 = self.filter_metadata()
        self.df2 = self.df.copy().filter(['source', 'author','category','racional','page_content','page'])

        self.df2["file_name"]= self.df2.source.apply(lambda x: Path(x).name)
        self.df2 = self.df2.groupby(['file_name', 'category'])[['page_content']]\
        .count().rename({'page_content':'counts'}, axis=1)\
        .reset_index(['file_name', 'category'])
        print("df2: group & count")
        #print(self.df2.head(5))

        self.df3 = self.df2.pivot(columns=['category'],index=['file_name']).droplevel(None, axis= 1)
        self.df3.index = [name[:-10] for name in self.df3.index] # Delete ", aaaa.pdf" sufix for clarity
        print("df3: pivot")
        self.column_names = self.df3.columns.to_list()
        self.data = {'index': self.df3.index.to_list(), 
                     **{col: self.df3[col].fillna(0).to_list() for col in self.column_names}  # Dictionary unpacking
                     }
        print("data: Bokeh Ready!")

    # Rename argument to '_self', because it should not be hashable
    # If the only parameter is not hashable, does the
    @st.cache_data
    def get_df(_self):
        return _self.df    
    
    def run_plot(self):
        
        n_catego = len(self.column_names)
        original_palette = palettes.Category20[n_catego]

        '''
        gray_color = "#F0F0F0" #"#E0E0E0"
        category_colors = {
            category: color
            for category, color in zip(self.column_names, original_palette)
            if category != "Metadatos"
        }
        
        if not self.skip_metadata:
            category_colors["Metadatos"] = gray_color
        
        custom_palette = tuple(category_colors[category] for category in OrderedDict(sorted(category_colors.items())))
        '''

        source = ColumnDataSource(self.data)

        p = figure(x_range= self.data.get('index'), width=800, height=800)
        p.add_layout(Legend(), place='right')  #'below'
        p.xaxis.major_label_orientation = -45
        p.xaxis.major_label_text_align='center'
        p.legend.click_policy='mute' #'hide' 

        p.vbar_stack(
            stackers=self.column_names, 
            x='index', 
            source=source,
            color = original_palette,
            #color = custom_palette,
            muted_alpha=0.2,
            legend_label = [cat[:39] for cat in self.column_names]
            )
        st.bokeh_chart(p) #show(p)