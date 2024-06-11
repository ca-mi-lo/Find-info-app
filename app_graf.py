import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

chart_data = pd.DataFrame(
   {
       "col1": list(range(20)) * 3,
       "col2": np.random.randn(60),
       "col3": ["A"] * 20 + ["B"] * 20 + ["C"] * 20,
   }
)

st.bar_chart(chart_data, x="col1", y="col2", color="col3")

df_ = pd.read_csv("./papers/datasets/one_shot_classif.csv")

#st.write(df)
st.bar_chart(df_, x="author", y="page_content" , color="category")

import matplotlib.pyplot as plt
import numpy as np



# Some example data to display
x = np.linspace(0, 2 * np.pi, 400)
y = np.sin(x ** 2)
fig, (ax1, ax2) = plt.subplots(1, 2)
fig.suptitle('Horizontally stacked subplots')
ax1.plot(x, y)
ax2.plot(x, -y)
st.pyplot(plt.gcf())


# Sample Data (replace with your actual data)
data = {'category': ['A', 'A', 'B', 'B', 'C', 'C'], 'value1': [10, 20, 30, 40, 50, 60], 'value2': [5, 15, 25, 35, 45, 55]}
df = pd.DataFrame(data)

st.bar_chart(df_[df_.author== 'Carlos Enrique Ruano Iraheta'], x= "author" ,  y="page_content" , color="category")
st.pyplot(plt.gcf())

# Create container for subplots (optional for better layout)
st.container()

# Create 3 columns for side-by-side display
#authors = df_.author.unique()
authors = [df_.author.unique()[i] for i in [0,1,3]]

#st.write(cols)

#col1, col2, col3 = st.columns(len(authors))
cols = st.columns(len(authors))

with cols[0]:
        st.bar_chart(df_[df_.author==authors[0]], x= "author" ,  y="page_content" , color="category")
with cols[1]:
        st.bar_chart(df_[df_.author==authors[0]], x= "author" ,  y="page_content" , color="category")
with cols[2]:
        st.bar_chart(df_[df_.author== '7300/166'], x= "author" ,  y="page_content" , color="category")


# Assuming you have df and authors

for author in authors:
    author_data = df[df['author'] == author]  # Filter data for each author

    # Debugging steps:
    print(f"Current author: {author}")
    print(f"Unique author names in DataFrame: {df['author'].unique()}")  # Print unique author names
    st.write(author_data)  # Display filtered DataFrame contents

    # Create the chart (assuming you've verified data)
    st.bar_chart(author_data.copy(), x="author", y="page_content", color="category")
    st.title(f"{author}'s Page Content by Category")
