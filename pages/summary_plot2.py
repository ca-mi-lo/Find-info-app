import streamlit as st
import re
import pandas as pd
import numpy as np
from pathlib import Path
import os
import find_info_app.graphs as grf
import find_info_app.graphs2 as grf2
###########################################################################

st.set_page_config(page_title="Classifier",
                   page_icon="📊", 
                   layout="wide"
                   )

folder_path = Path("./datasets/by_species/")
file_list = os.listdir(folder_path)

st.subheader("Búsqueda por Categoría")

# Init Session state
ss = st.session_state

if "df" not in ss:
    ss["df"] = pd.DataFrame()

if "skip_metadata" not in ss:
    ss["skip_metadata"] = True

if "df_filtered" not in ss:
    ss["df_filtered"] = ss["df"]

def update_filter():
    ss["df_filtered"] = my_plot.filter_metadata(
                            skip_metadata= choose_metadata=="Oclutar",
                            species=choose_species,
                            catego=choose_catego,
                            file_name=choose_file
                            )

my_plot = grf2.load_data(folder_path = folder_path,  skip_metadata=False)
ss["df"] = my_plot.df

species = pd.concat([pd.Series(['all']), ss["df"]['species_folder']])\
                        .drop_duplicates()\
                        .dropna()

catego = pd.concat([pd.Series(['all']), ss["df"]['category']])\
                        .drop_duplicates()\
                        .dropna()

file_name = pd.concat([pd.Series(['all']), ss["df"]['source']])\
                    .drop_duplicates()\
                    .dropna()

choose_species = st.sidebar.selectbox('Especie:', species, on_change=update_filter)
choose_catego = st.sidebar.selectbox('Categoría:', catego, on_change=update_filter) 
choose_file = st.sidebar.selectbox('File_name:', file_name, on_change=update_filter)
choose_metadata = st.sidebar.radio("Catagoría Bibliografía",
                                   ["Ocultar", "Mostrar"], 
                                   on_change=update_filter,
                                   index =0)

choose_species, choose_catego
ss["df_filtered"]