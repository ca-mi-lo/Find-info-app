import streamlit as st
import pandas as pd
import numpy as np
import find_info_app.graphs as grf

#df_ = pd.read_csv("./papers/datasets/one_shot_classif.csv")
path = "./papers/datasets/one_shot_classif.csv"
print("is there any body ...out there?")
#find_info_app.graphs.TheHoleEnchilada(path=path)

my_instance = grf.Prepare_plot()
my_instance.run_plot()
