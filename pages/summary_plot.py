import streamlit as st
import re
import pandas as pd
import numpy as np
from pathlib import Path
import os
import find_info_app.graphs as grf
###########################################################################

st.set_page_config(page_title="Classifier",
                   page_icon="📊", 
                   layout="wide",
                    initial_sidebar_state="expanded"
                   )

# Init Session state
ss = st.session_state
folder_path = Path("./datasets/by_species/")
file_list = os.listdir(folder_path)

def ss_init():
    if "my_plot" not in ss:
        ss["my_plot"] = grf.load_data(folder_path = folder_path,  skip_metadata=True)
    
    if "df" not in ss:
        ss["df"] = ss["my_plot"].df

    if "df_filtered" not in ss:
        ss["df_filtered"] = ss["df"]
    
    if "df" not in ss:
        ss["df"] = pd.DataFrame()

    if "skip_metadata" not in ss:
        ss["skip_metadata"] = True

    if "current_page" not in ss:
        ss["current_page"]=1
    
    if "page_size" not in ss:
        ss["page_size"]=5
ss_init()

def filter_metadata(df, skip_metadata=True, 
                    species = 'all',
                    catego='all',
                    file_name='all',
                    #current_page=1
                    ):

    ss["df"] = calculate_page_number(ss["df"])
    if skip_metadata or skip_metadata=='Ocultar':
        df = df[df.category != 'Metadatos']
        df = df[df.category != 'Introducción']
    
    if species == 'all':
        df = df
    else:
        df = df[df.species_folder == species]
    #----------------------------------------------------
    if catego == 'all':
        df = df
    else: 
        df = df[df.category == catego]
    #----------------------------------------------------
    if file_name == 'all':
        df = df
    else: 
        df = df[df.source == file_name]
    #----------------------------------------------------        
    #df = df[df.page_number == current_page]

    return df

def update_filter():
    ss["df"] = calculate_page_number(ss["df"])
    ss["df_filtered"] = filter_metadata(
                            ss["df"],
                            skip_metadata= choose_metadata=="Ocultar",
                            species=choose_species,
                            catego=choose_catego,
                            file_name=choose_file,
                            #current_page=ss["current_page"]
                            )
    ss["df_filtered"] = calculate_page_number(ss["df_filtered"])
    ss["df_filtered"] = ss["df_filtered"][ss["df_filtered"].page_number == ss["current_page"]]

def calculate_page_number(df, page_size=5):
  df["page_number"] = (df.reset_index(drop=True).index // page_size) + 1
  return df

def page_render():
    update_filter()    
    for index, row in ss["df_filtered"].iterrows():
        header = []
        file_name = ss["df_filtered"]["source"].unique()
        
        if (len(file_name)==1):
            file_name =str(file_name[0])
        else: row["source"]

        ss["categos"] = ss["df_filtered"]["category"].unique()
        if (len(ss["categos"])==1):
            ss["categos"] ="**"+ str(ss["categos"][0])+ "**"
        else: 
            ss["categos"] = row["category"]

        page = row['page']
        text = row["page_content"]
        text = re.sub(r"\n\s*\n", "\n\n", text)  # Replace multiple newlines with a single one
        text = text.replace("\n\n",'\n')
        text = text.replace("a ´",'á').replace("e ´",'é').replace("o ´",'ó').replace("i ´",'í').replace("ı ´","í")
        text = text.replace("A ´ ",'Á').replace("E ´",'É').replace("I ´",'Í').replace("o ´",'Ó')
        
        
        header = f"**Page {page}:** _" + 5 * "&nbsp;" + file_name + "_" + 5*"&nbsp;" + str(ss["categos"])
        st.markdown(header if isinstance(header, str) else "")#header[-1]
        #st.text(text)
        font_size = '14px'
        font_fam = 'Arial'
        text_formated = f"""<span style="font-size: {font_size}; font-family: {font_fam};"> {text} </span>"""
        st.markdown(text_formated, unsafe_allow_html=True)

        st.divider()

def setup_comboboxes():
    species = pd.concat([pd.Series(['all']), ss["df"]['species_folder']])\
                            .drop_duplicates().dropna()

    catego = pd.concat([pd.Series(['all']), ss["df"]['category']])\
                            .drop_duplicates().dropna()

    file_name = pd.concat([pd.Series(['all']), ss["df"]['source']])\
                            .drop_duplicates().dropna()

    choose_species = st.selectbox('Especie:', species) #, on_change=update_filter
    
    choose_catego = st.sidebar.selectbox('Categoría:', catego) 
    choose_file = st.sidebar.selectbox('File_name:', file_name)
    choose_metadata = st.sidebar.radio("Categoría Bibliografía",
                ["Ocultar", "Mostrar"], index =0)
    return choose_species, choose_catego, choose_file, choose_metadata

#########################################################################
# Main
st.subheader("Seleccione la especie para el análisis por categoría")
choose_species, choose_catego, choose_file, choose_metadata = setup_comboboxes()
update_filter()
my_df = grf.df_byspecies(df=ss["df"],species=choose_species, skip_metadata=choose_metadata).get_df()
my_plot = grf.plot()
my_plot.prepare(df=my_df)
my_plot.run_plot()
choose_metadata
ss["current_page"] = st.number_input("Hoja:", min_value=1, max_value=int(len(ss["df"]) / ss["page_size"]) + 1)
page_render()