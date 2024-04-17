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

if "filename_list_done" not in ss:
    ss["filename_list_done"] = []


def index_pdf_file():

    if len(ss["pdf_file_list"]) > 0:

        pdf_filename_list = [pdf_file.name for pdf_file in ss.pdf_file_list]

        # New elements detected (elements nots contained in memory)
        print("FLAG: pdf_filename_list", pdf_filename_list)
        print("FLAG: filename_list_done", ss["filename_list_done"])
        print(
            "FLAG: is_new:",
            not set(pdf_filename_list).issubset(set(ss["filename_list_done"])),
        )
        if not set(pdf_filename_list) <= set(ss.get("filename_list_done", [])):

            new_files = [
                filename
                for filename in pdf_filename_list
                if filename not in set(ss.get("filename_list_done", []))
            ]
            print("FLAG: new_files", new_files)
            for pdf_file in ss["pdf_file_list"]:
                if pdf_file.name in new_files:
                    filename = pdf_file.name

                    with st.spinner(_("indexing ") + filename):
                        index = model.index_file(
                            pdf_file,
                            filename,
                            doc_size=ss["doc_size"],
                            doc_overlap=int(ss["doc_overlap"] * ss["doc_size"]),
                        )
                        # Update session state with lists
                        if "index_list" not in ss:
                            ss["index_list"] = []

                        ss["index_list"].append(index)

                        if "filename_list" not in ss:
                            ss["filename_list"] = []
                        ss["filename_list"].append(filename)
                        debug_index()
                        ss["filename_list_done"].append(filename)

        # list is smaller: some drops are in order
        elif set(pdf_filename_list).issubset(set(ss["filename_list_done"])):
            drop_files = list(set(ss["filename_list_done"]) - set(pdf_filename_list))
            print("FLAG: drop_files", drop_files)

            for filename in drop_files:
                ss["filename_list_done"].remove(filename)
                if filename in ss["index_list"]:
                    index_to_remove = ss["index_list"].index(
                        filename
                    )  # Find index of filename
                    del ss["index_list"][
                        index_to_remove
                    ]  # Remove entry from index_list

                if filename in ss["filename_list"]:
                    filename_to_remove = ss["filename_list"].index(
                        filename
                    )  # Find index of filename
                    del ss["filename_list"][
                        filename_to_remove
                    ]  # Remove entry from filename_list

                # all docs where the pdf is filename
                docs_to_delete = model.store.get(where={"source": filename})

                # Optional code: Debug & Print
                metadata_list = docs_to_delete.get("metadatas")
                sources_list = [metadata["source"] for metadata in metadata_list]
                sources_list = list(set(sources_list))
                print("FLAG: Files to delete", sources_list)

                # Delete docs from DB
                model.store.delete(docs_to_delete["ids"])
        # --------------------------------------------------
    else:
        print("FLAG: ss['pdf_file_list']) == 0")
        del ss["pdf_file_list"]
        del ss["filename_list_done"]
        del ss["filename_list"]
        ss.pop("index_list")
        ss["debug"].pop("index_list")


def debug_index():
    indices = ss["index_list"]
    debug_info = []

    for index in indices:
        d = {
            "file_hash": index["file_hash"],
            "n_docs": index["n_docs"],
            "summary": index["summary"],
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


# modified
def ui_pdf_file():
    disabled = not os.getenv("GOOGLE_API_KEY")
    st.write(_("## Upload or select your PDF file"))
    t1, t2 = st.tabs([_("UPLOAD"), _("SELECT")])
    with t1:
        st.file_uploader(
            _("pdf file"),
            type="pdf",
            key="pdf_file_list",  # new key name
            accept_multiple_files=True,  # New parameter
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
        _("What are you looking for in:")
        + "\n"
        + (f"{filename_text} ?" if filename_text else "")
    )

    disabled = not ss.get("index_list")

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
    disabled = not ss.get("index_list")
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
        index = ss.get("index_list", [])[0] if ss.get("index_list") else {}

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
        st.rerun()  # it is necessary to enable feedback buttons


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
