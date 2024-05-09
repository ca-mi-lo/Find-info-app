import logging
import os
import gettext

from streamlit import logger

from find_info_app import ai, feedback

_ = gettext.gettext

import streamlit as st
from langchain_community.vectorstores import Chroma

import find_info_app
from find_info_app.prompts import TASK
import find_info_app.model as model


if (
    (host := os.getenv("ES_HOST"))
    and (port := os.getenv("ES_PORT"))
    and (index := os.getenv("ES_INDEX"))
):
    feedback = feedback.ESFeedback(host, int(port), index)
else:
    feedback = feedback.BaseFeedback()

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed",
    page_title=f"{find_info_app.__app_name__} {find_info_app.__version__}",
)

# Init Session state
ss = st.session_state
ss["model"] = ai.BASE_MODEL
ss["embedding_model"] = ai.BASE_EMBEDDING_MODEL
if "debug" not in ss:
    ss["debug"] = {}

if "filename_list_done" not in ss:
    ss["filename_list_done"] = set()

if "logger" not in ss:
    ss["logger"] = find_info_app.create_logger(levelname="DEBUG")

logger: logging.Logger = ss["logger"]

if not "pdf_file_list" in ss:
    # Chicano fix para vaciado de bd
    logger.debug("Clean db")
    logger.debug(list(ss.keys()))
    store = model.init_db(ss["embedding_model"])

    all_docs = store.get()
    store.delete_collection()
    logger.debug(f"removed docs: {len(all_docs['ids'])}")

def index_pdf_file():
    if "store" not in ss:
        ss["store"] = model.init_db(ss["embedding_model"])

    store: Chroma = ss["store"]
    if ss["pdf_file_list"]:
        files_set = set([f.name for f in ss["pdf_file_list"]])
        for file in files_set - ss["filename_list_done"]:
            logger.debug(f"adding file: {file}")
            upload_file = [f for f in ss["pdf_file_list"] if f.name == file][0]
            with st.spinner(_("indexing ") + file):
                index = model.index_file(
                    store,
                    upload_file,
                    file,
                    doc_size=ss["doc_size"],
                    doc_overlap=int(ss["doc_overlap"] * ss["doc_size"]),
                )
            ss["filename_list_done"].add(file)
            logger.debug(f"file: {file}\t no_docs: {index['n_docs']}")
        for file in ss["filename_list_done"] - files_set:
            logger.debug(f"removing file: {file}")
            docs_to_delete = store.get(where={"source": file})

            store.delete(docs_to_delete["ids"])
            logger.debug(f"file: {file}\t removed_docs: {len(docs_to_delete['ids'])}")
            ss["filename_list_done"].remove(file)
    else:
        logger.debug("no items in list")
        all_docs = store.get()
        store.delete(all_docs["ids"])
        ss["filename_list_done"] = set()
        logger.debug(f"removed docs: {len(all_docs['ids'])}")


def debug_index():
    # DEPRECATED
    indices = ss["index_list"]
    debug_info = []

    for index in indices:
        d = {
            "file_hash": index["file_hash"],
            "n_docs": index["n_docs"],
            "profiling": index["profiling"],
            "file_name": index["filename"],  # new
        }
        debug_info.append(d)

    ss["debug"]["index_list"] = debug_info  # Store the list of debug info


def ui_spacer(n=2, line=False, next_n=0):
    for _ in range(n):
        st.write("")
    if line:
        st.divider()
    for _ in range(next_n):
        st.write("")


def ui_show_debug():
    st.checkbox("show debug section", key="show_debug")


def ui_pdf_file():
    disabled = not os.getenv("GOOGLE_API_KEY")
    st.write(_("## Upload or select your PDF file"))
    t1, t2 = st.tabs([_("UPLOAD"), _("SELECT")])
    with t1:

        st.file_uploader(
            _("pdf file"),
            type="pdf",
            key="pdf_file_list",
            accept_multiple_files=True,
            label_visibility="collapsed",
            on_change=index_pdf_file,
            disabled=disabled,
        )

    with t2:
        st.write(_("### Coming soon!"))


def ui_context():

    filename_text = ""
    if ss.get("filename_list", ""):
        filename_text = ",  ".join(ss["filename_list"])

    elif ss.get("filename"):
        filename_text = ss.filename

    st.write(
        _("### What are you looking for in:")
        + "\n"
        + (f"{filename_text} ?" if filename_text else "")
    )

    disabled = not ss.get("filename_list_done")

    st.text_area(
        "question",
        key="question",
        height=100,
        placeholder=_("Enter question here"),
        help="",
        label_visibility="collapsed",
        disabled=disabled,
    )


def b_ask():
    disabled = not ss.get("filename_list_done")
    c1, c2, c3 = st.columns([2, 1, 1])
    if c2.button(":thumbsup:", use_container_width=True, disabled=not ss.get("output")):
        if feedback.send(1, ss):
            st.toast(_(":white_check_mark: Thanks!"))
        else:
            st.toast(_(":exclamation: Failed to send feedback"))
    if c3.button(
        ":thumbsdown:", use_container_width=True, disabled=not ss.get("output")
    ):
        if feedback.send(-1, ss):
            st.toast(_(":white_check_mark: Thanks!"))
        else:
            st.toast(_(":exclamation: Failed to send feedback"))

    if c1.button(
        _("get answer"), use_container_width=True, disabled=disabled, type="primary"
    ):
        question = ss.get("question", "")
        task = TASK[ss["task"]]

        # (debugg-mode) hard code for dim=1.
        # index = ss.get("index_list", [])[0] if ss.get("index_list") else {}

        with st.spinner(_("preparing answer")):
            resp = model.query(
                ss["store"],
                question,
                task,
                temperature=ss["temperature"],
                max_frags=ss["max_frags"],
            )
            ss["debug"]["executed_response"] = True
        ss["debug"]["answer"] = resp

        q = question.strip()
        a = resp["text"].strip()
        # ss["resp"] = resp  #new

        # output_add(q, a)
        st.rerun()  # it is necessary to enable feedback buttons


def ui_output():
    if "answer" in ss["debug"].keys():
        st.write(_("### May be you can find your answer in the following excerpts:"))
        for i, doc in enumerate(
                ss["debug"].get("answer", "" ).get("selected_docs_raw", "")
                ):
            # st.markdown("TOP " + str(i + 1) + ":\n")
            st.markdown(_("**Page:** ") + str(doc.metadata["page"]+1)+";" \
                        + 5*"&nbsp;" + _("**File:** _") + doc.metadata["source"]+"_")
            st.markdown(doc.page_content)
            st.divider()

def ui_debug():
    if ss.get("show_debug"):
        st.write("### Debug")
        st.write(ss.get("debug", {}))


with st.sidebar:
    st.write(
        f"""
    # {find_info_app.__app_name__}
    version ({find_info_app.__version__})

    {_("Question answering system built on top of Gemini Pro")}
    """
    )
    ui_spacer()
    if st.selectbox(_("Choose you language"), ["en", "es"], key="language"):
        lang = ss.get("language", "en")
        ss["debug"]["language"] = lang
        localizator = gettext.translation(
            "messages", localedir="locale", languages=[lang], fallback=True
        )
        localizator.install()
        _ = localizator.gettext
    with st.expander(_("Advanced settings")):
        st.write(_("**Indexing options**"))
        st.select_slider(
            _("Document size"),
            options=[200, 500, 1000, 1500],
            value=1000,
            key="doc_size",
            disabled=True,
        )
        st.select_slider(
            _("Overlap ratio"),
            options=[0.05, 0.1, 0.15, 0.2],
            value=0.1,
            format_func=lambda x: f"{x:2.0%}",
            key="doc_overlap",
            disabled=True,
        )
        st.write(_("**Answering options**"))
        st.slider(
            _("Temperature"),
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.1,
            format="%1.1f",
            key="temperature",
            disabled=True,
        )
        st.slider(
            _("No. of frag retrieved"),
            min_value=1,
            max_value=10,
            value=5,
            step=1,
            key="max_frags",
            disabled=True,
        )
        st.selectbox(
            _("Task"),
            TASK.keys(),
            key="task",
            help=_("Base prompt used to generate the answer to the question"),
            disabled=True,
        )

if not os.getenv("GOOGLE_API_KEY"):
    st.error(_("Google API Key was not provided"), icon="🚨")


ui_pdf_file()
ui_context()
b_ask()
ui_output()
ui_show_debug()
ui_debug()
