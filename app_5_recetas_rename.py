import streamlit as st

default  = {
    'rice': 3.0,
    'cheese': 5.0
}

ss = st.session_state

def index_pdf_file():
    if ss.pdf_file_list:
        pdf_filename_list = [pdf_file for pdf_file in ss.pdf_file_list] # pdf_file.name
        # "acá sería  
        #if ss.filename_list_done[1] is in ss.pdf_file_list:
        if len(pdf_filename_list) > len(ss.filename_list_done[1]):
            new_doc = set(ss.pdf_file_list) - set(list(ss.filename_list_done[1].keys()))
            new_doc = list(new_doc)[0]
            ss.filename_list_done[1][new_doc] = 0.0

        elif len(ss.pdf_file_list) < len(ss.filename_list_done[1]):
            new_doc = set(list(ss.filename_list_done[1].keys())) - set(ss.pdf_file_list)
            new_doc = list(new_doc)[0]
            del ss.filename_list_done[1][new_doc]  # update default in memory


if "filename_list_done" not in ss:
    ss.filename_list_done = ["", default] #, temp_data_entered


selected_new_docs = st.multiselect('Choose new_docs for your default',
                                      ['rice', 'cheese', 'apples', 'water'],
                                      on_change=index_pdf_file,
                                      default=list(ss.filename_list_done[1].keys()),
                                      key="pdf_file_list"
)

list(ss.filename_list_done[1].keys())


for key in list(ss.filename_list_done[1].keys()):
    ss.filename_list_done[1][key] = st.number_input(key, min_value=0., value=0.0)


#ss.filename_list_done[1][key]
print("ss.pdf_file_list: ", ss.pdf_file_list)
#ss.filename_list_done[1]
#st.write(set(list(ss.filename_list_done[1].keys())))


