import streamlit as st
import pandas as pd
import numpy as np
import os

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

class load_data():

    def __init__(self, folder_path = "./datasets/by_species/sdfnmksdfajkldf",  skip_metadata=True):
        print("Reading csv's..")
        self.folder_path = "./datasets/by_species/"
        self.skip_metadata = skip_metadata
        self.df = pd.DataFrame()
        self.file_list = []
        
        for root, _, files in os.walk(folder_path):
            for file in files:
                print(f"Reading {file}")
                self.full_path = os.path.join(root, file)
                self.df = pd.concat([self.df, pd.read_csv(self.full_path)], ignore_index = True)
                self.file_list.append(self.full_path)
        
        self.df = self.df.filter(['source','species_folder', 'author','category','racional','page_content','page'])

    def filter_metadata(self, skip_metadata=True, 
                        species = 'Melipona_beecheii',
                        catego='all',
                        file_name='all'
                        ):

        """Filters data based on skip_metadata flag."""
        if skip_metadata:
            self.df = self.df[self.df.category != 'Metadatos']
            self.df = self.df[self.df.category != 'Introducción']
        
        if species == 'all':
            self.df = self.df
        else:
            self.df = self.df[self.df.species_folder == species]
        #----------------------------------------------------
        if catego == 'all':
            self.df = self.df
        else: 
            self.df = self.df[self.df.category == catego]
        #----------------------------------------------------
        if file_name == 'all':
            self.df = self.df
        else: 
            self.df = self.df[self.df.source == file_name]
                
        return self.df
    
    def pivot_df(self):
        self.df2 = self.filter_metadata()
        self.df2 = self.df.copy().filter(['source','species_folder', 'author','category','racional','page_content','page'])

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

    
    def run_plot(self):
        
        n_catego = len(self.column_names)
        original_palette = palettes.Category20[n_catego]

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
    
