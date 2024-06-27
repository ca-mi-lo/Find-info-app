import streamlit as st
import pandas as pd
from pathlib import Path
import find_info_app.graphs as grf
import re
###########################################################################

st.set_page_config(page_title="Classifier", page_icon="📊", layout="wide")


#df_ = pd.read_csv("./papers/datasets/one_shot_classif.csv")
path = "./papers/datasets/one_shot_classif.csv"
st.write("is there any body ...out there?")
#find_info_app.graphs.TheHoleEnchilada(path=path)

my_plot = grf.Prepare_plot()
df = my_plot.get_df()

# Add a new column named 'page_number'
def calculate_page_number(df, page_size=5):
  df["page_number"] = (df.index // page_size) + 1
  return df

df = calculate_page_number(df.copy())  # Apply calculation to a copy to avoid modifying original DataFrame

page_size = 5
current_page = st.number_input("Página:", min_value=1, max_value=int(len(df) / page_size) + 1)

df_filtered = df[df.page_number == current_page]

for index, row in df_filtered.iterrows():

    text = row["page_content"]
    #text = re.sub(r"\n\s*\n", "\n\n", text)  # Replace multiple newlines with a single one
    text = text.replace("\n\n",'\n')
    header = f"**Chunk {index + 1}:**"
    with st.container(): 
        st.markdown(header)
        st.text(text)
        st.divider()