import streamlit as st
import re
import pandas as pd
import numpy as np
from pathlib import Path
import find_info_app.graphs as grf
###########################################################################

st.set_page_config(page_title="Classifier", page_icon="📊", layout="wide")

#df_ = pd.read_csv("./papers/datasets/one_shot_classif.csv")
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

def calculate_page_number(df=ss["df"], page_size=5):
  df["page_number"] = (df.index // page_size) + 1
  return df

with st.form(key='my_form'):
    my_plot = grf.Prepare_plot()
    ss["df"] = my_plot.get_df()
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
    if choose_catego != 'all':
        ss["df"] = ss["df"][ss["df"].category == choose_catego]
        

    choose_file = st.sidebar.selectbox('File_name:', file_name)
    if choose_file != 'all':
        ss["df"] = ss["df"][ss["df"].file_name == choose_file]



    ss["df"] = calculate_page_number(ss["df"])  # .copy() Apply calculation to a copy to avoid modifying original DataFrame
    page_size = 5
    current_page = st.number_input("Página:", min_value=1, max_value=int(len(ss["df"]) / page_size) + 1)
    df_filtered = ss["df"][ss["df"].page_number == current_page]

    for index, row in df_filtered.iterrows():

        text = row["page_content"]
        text = re.sub(r"\n\s*\n", "\n\n", text)  # Replace multiple newlines with a single one
        text = text.replace("\n\n",'\n')
        text = text.replace("a ´",'á').replace("e ´",'é').replace("o ´",'ó').replace("i ´",'í').replace("ı ´","í")
        text = text.replace("A ´ ",'Á').replace("E ´",'É').replace("I ´",'Í').replace("o ´",'Ó')
        
        header = f"**Chunk {index + 1}:**"
        #with st.container(): 
        st.markdown(header)
        st.text(text)
        st.divider()
    
    st.form_submit_button("pícale aquí")

ss["df"] #= st.dataframe(ss["df"])
############################################################################