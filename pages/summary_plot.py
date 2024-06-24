import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import find_info_app.graphs as grf
###########################################################################

st.set_page_config(page_title="Classifier", page_icon="📊", layout="wide")


#df_ = pd.read_csv("./papers/datasets/one_shot_classif.csv")
path = "./papers/datasets/one_shot_classif.csv"
st.write("is there any body ...out there?")
#find_info_app.graphs.TheHoleEnchilada(path=path)

viz_1 = st.container()
viz_2 = st.container()

my_plot = grf.Prepare_plot()
df = my_plot.get_df()
df["file_name"]= df.source.apply(lambda x: Path(x).name)
df = df[['page_content','category','file_name', 'racional']]


with viz_1:
    my_plot.run_plot()
    catego = pd.concat([pd.Series(['all']), df['category']])\
                        .drop_duplicates()\
                        .dropna()
                        
    choose_catego = st.sidebar.selectbox('Categoría:', catego) 
    if choose_catego != 'all':
        df = df[df.category == choose_catego]

    file_name = pd.concat([pd.Series(['all']), df['file_name']])\
                        .drop_duplicates()\
                        .dropna()
    choose_file = st.sidebar.selectbox('File_name:', file_name)
    if choose_file != 'all':
        df = df[df.file_name == choose_file]
    
    st.dataframe(df)

