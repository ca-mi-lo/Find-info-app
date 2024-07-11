import streamlit as st
import re
import pandas as pd
import numpy as np
from pathlib import Path
import find_info_app.graphs as grf
###########################################################################

st.set_page_config(page_title="Classifier",
                   page_icon="📊", 
                   layout="wide"
                   )

path = "./papers/datasets/one_shot_classif.csv"
st.subheader("Búsqueda por Categoría")


# Init Session state
ss = st.session_state

if "catego" not in ss:
    ss["catego"] = []

if "file_name" not in ss:
    ss["file_name"] = []

if "df" not in ss:
    ss["df"] = pd.DataFrame()

if "skip_metadata" not in ss:
    ss["skip_metadata"] = True


#Quizás debería de vivir en prompts.py
def calculate_page_number(df, page_size=5):
  df["page_number"] = (df.reset_index(drop=True).index // page_size) + 1
  return df

def prepare_pager():
    
    #ss["skip_metadata"] = skip_metadata
    my_plot = grf.Prepare_plot(skip_metadata = ss["skip_metadata"])
    
    def comments():
        '''
        La reactividad del checkbox aun no funciona, pero está todo puesto para que ss["skip_metadata"] = True
        skip_metadata = st.sidebar.checkbox("Skip category 'Metadatos'",
                                            value = True, 
                                            on_change = my_plot.filter_metadata,
                                            args=[ss["skip_metadata"]])
        '''

    my_plot = grf.Prepare_plot(path= './papers/datasets/Murcielagos_one_shot_classif_4.csv', skip_metadata = ss["skip_metadata"])
    
    if ss["skip_metadata"]:
        ss["df"] = my_plot.filter_metadata(skip_metadata = ss["skip_metadata"])
        #ss["df"] = ss["df"][ss["df"]["category"]!="Introducción"]

    ss["df"] = my_plot.get_df()
    
    if ss["skip_metadata"]:
        ss["df"] = my_plot.filter_metadata(skip_metadata=ss["skip_metadata"])
    ss["df"]["file_name"]= ss["df"].source.apply(lambda x: Path(x).name)
    ss["df"] = ss["df"][['page_content','category','file_name', 'racional']]

    my_plot.run_plot()

    catego = pd.concat([pd.Series(['all']), ss["df"]['category']])\
                        .drop_duplicates()\
                        .dropna()

    file_name = pd.concat([pd.Series(['all']), ss["df"]['file_name']])\
                        .drop_duplicates()\
                        .dropna()

    choose_catego = st.sidebar.selectbox('Categoría:', catego) 
    choose_file = st.sidebar.selectbox('File_name:', file_name)

    if choose_catego != 'all':
        ss["df"] = ss["df"][ss["df"].category == choose_catego].reset_index(drop=True)
        ss["df_filtered"] = ss["df"]
        ss["df_filtered"] = ss["df_filtered"][ss["df"].file_name == choose_file]
        
    
    if choose_file != 'all':
        ss["df"] = ss["df"][ss["df"].file_name == choose_file].reset_index(drop=True)
        ss["df_filtered"] = ss["df"]
        ss["df_filtered"] = ss["df_filtered"][ss["df"].category == choose_catego]


    ss["df"] = calculate_page_number(ss["df"])
    page_size = 5

    current_page = st.number_input("Página:", min_value=1, max_value=int(len(ss["df"]) / page_size) + 1)

    df_filtered = ss["df"][ss["df"].page_number == current_page]
    ss["df_filtered"] = df_filtered

#def render_pager():
    
    for index, row in ss["df_filtered"].iterrows():
        header = []
        file_name = ss["df_filtered"]["file_name"].unique()
        
        if (len(file_name)==1):
            file_name =str(file_name[0])
        else: row["file_name"]

        ss["categos"] = ss["df_filtered"]["category"].unique()
        if (len(ss["categos"])==1):
            ss["categos"] ="**"+ str(ss["categos"][0])+ "**"
        else: 
            ss["categos"] = row["category"]

        text = row["page_content"]
        text = re.sub(r"\n\s*\n", "\n\n", text)  # Replace multiple newlines with a single one
        text = text.replace("\n\n",'\n')
        text = text.replace("a ´",'á').replace("e ´",'é').replace("o ´",'ó').replace("i ´",'í').replace("ı ´","í")
        text = text.replace("A ´ ",'Á').replace("E ´",'É').replace("I ´",'Í').replace("o ´",'Ó')
        
        
        header = f"**Chunk {index + 1}:** _" + 5 * "&nbsp;" + file_name + "_" + 5*"&nbsp;" + str(ss["categos"])
        st.markdown(header if isinstance(header, str) else "")#header[-1]
        #st.text(text)
        font_size = '14px'
        font_fam = 'Arial'
        text_formated = f"""<span style="font-size: {font_size}; font-family: {font_fam};"> {text} </span>"""
        st.markdown(text_formated, unsafe_allow_html=True)

        st.divider()

prepare_pager()
