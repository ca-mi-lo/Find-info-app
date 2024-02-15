import gettext
_ = gettext.gettext
from time import time

import streamlit as st
import find_info_app
from find_info_app.prompts import TASK
import find_info_app.model as model

st.set_page_config(layout="centered", 
                   page_title=f'{find_info_app.app_name} {find_info_app.__version__}')
ss = st.session_state
if 'debug' not in ss: ss['debug'] = {}

def index_pdf_file():
    if ss['pdf_file']:
        ss['filename'] = ss['pdf_file'].name
        if ss['filename'] != ss.get('filename_done'):
            with st.spinner(_('indexing ')+ ss['filename']):
                index = model.index_file(ss['pdf_file'], ss['filename'], 
                                         doc_size=500)
                ss['index'] = index
                debug_index()
                ss['filename_done'] = ss['filename']

def debug_index():
    index = ss['index']
    d = {
        'file_hash': index['file_hash'],
        'n_docs': index['n_docs'],
        'first_doc': index['docs'][0],
        'summary': index['summary'],
        'profiling': index['profiling']
    }
    ss['debug']['index'] = d

def ui_spacer(n=2, line=False, next_n=0):
	for _ in range(n):
		st.write('')
	if line:
		st.tabs([' '])
	for _ in range(next_n):
		st.write('')

def ui_show_debug():
	st.checkbox('show debug section', key='show_debug')

def ui_pdf_file():
    st.write(_("## Upload or select your PDF file"))
    t1, t2 = st.tabs([_("UPLOAD"), _("SELECT")])
    with t1:
        st.file_uploader(_('pdf file'), type='pdf', key='pdf_file', 
                         label_visibility="collapsed", on_change=index_pdf_file)
    with t2:
        st.write(_('### Coming soon!'))

def ui_context():
    st.write(_('## What are you looking for')+(f' in {ss.filename}' 
                                                        if ss.get('filename')
                                                        else ''))
    disabled = False
    st.text_area('question', key='question', height=100, 
                 placeholder=_('Enter question here'), 
                 help='', label_visibility='collapsed', disabled=disabled)

def b_ask():
    disabled = True
    if st.button(_('get_answer'), disabled=disabled, type='primary'):
        question = ss.get('question', '')
        temperature = 0.1
        task = TASK['V1']
        max_frags = 1
        n_before = 1
        n_after = 0 
        index = {}
        with st.spinner(_('preparing answer')):
            resp = model.query()


def ui_debug():
    if ss.get('show_debug'):
        st.write('## Debug')
        st.write(ss.get('debug', {}))


st.title("Find info App")

ui_pdf_file()
ui_context()
b_ask()
ui_show_debug()
ui_debug()
