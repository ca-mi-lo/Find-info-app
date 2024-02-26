import os
import gettext

from find_info_app import ai, feedback

_ = gettext.gettext

import streamlit as st
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
    layout="centered",
    page_title=f"{find_info_app.__app_name__} {find_info_app.__version__}",
)
ss = st.session_state
ss["model"] = ai.BASE_MODEL
ss["embedding_model"] = ai.BASE_EMBEDDING_MODEL
if "debug" not in ss:
    ss["debug"] = {}


def index_pdf_file():
    if ss["pdf_file"]:
        ss["filename"] = ss["pdf_file"].name
        if ss["filename"] != ss.get("filename_done"):
            with st.spinner(_("indexing ") + ss["filename"]):
                index = model.index_file(
                    ss["pdf_file"],
                    ss["filename"],
                    doc_size=ss["doc_size"],
                    doc_overlap=int(ss["doc_overlap"] * ss["doc_size"]),
                )
                ss["index"] = index
                debug_index()
                ss["filename_done"] = ss["filename"]
    else:
        ss.pop("index")
        ss.pop("filename")
        ss["debug"].pop("index")


def debug_index():
    index = ss["index"]
    d = {
        "file_hash": index["file_hash"],
        "n_docs": index["n_docs"],
        "first_doc": index["docs"][0],
        "summary": index["summary"],
        "profiling": index["profiling"],
    }
    ss["debug"]["index"] = d


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
            key="pdf_file",
            label_visibility="collapsed",
            on_change=index_pdf_file,
            disabled=disabled,
        )
    with t2:
        st.write(_("### Coming soon!"))


def ui_context():
    st.write(
        _("## What are you looking for")
        + (f" in {ss.filename}" if ss.get("filename") else "")
    )
    disabled = not ss.get("index")
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
    disabled = not ss.get("index")
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
        index: dict = ss.get("index", {})
        with st.spinner(_("preparing answer")):
            resp = model.query(
                question,
                task,
                index,
                temperature=ss["temperature"],
                max_frags=ss["max_frags"],
            )
            ss["debug"]["executed_response"] = True
            ss["debug"]["answer"] = resp

        q = question.strip()
        a = resp["text"].strip()

        output_add(q, a)


def ui_output():
    output = ss.get("output", "")
    st.write(output)


def output_add(q, a):
    if "output" not in ss:
        ss["output"] = ""
    new_resp = f"### {q}\n{a}\n\n"
    ss["output"] = new_resp + ss["output"]


def ui_debug():
    if ss.get("show_debug"):
        st.write("## Debug")
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
        st.write("**Answering options**")
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
