import os
import gettext
from typing import Iterable

from langchain_core.documents import Document
import streamlit as st

from find_info_app import feedback

_ = gettext.gettext

if (
    (host := os.getenv("ES_HOST"))
    and (port := os.getenv("ES_PORT"))
    and (index := os.getenv("ES_INDEX"))
):
    feedback = feedback.ESFeedback(host, int(port), index)
else:
    feedback = feedback.BaseFeedback()


def display_docs(docs: Iterable[Document]):
    for idx, doc in enumerate(docs):
        st.markdown(
                _("**Page:** ")
                + str(doc.metadata["page"] + 1)
                + ";"
                + 5 * "&nbsp;"
                + _("**File:** _")
                + doc.metadata["source"]
                + "_"
                )
        st.markdown(doc.page_content)
        b1, b2 = st.columns(2)

        if b1.button(":thumbsup:", use_container_width=True, key=f"feedback_up_{idx}"):
            if feedback.send(1, doc):
                st.toast(_(":white_check_mark: Thanks!"))
            else:
                st.toast(_(":exclamation: Failed to send feedback"))
        if b2.button(
                ":thumbsdown:", use_container_width=True, key=f"feedback_down_{idx}"
                ):
            if feedback.send(-1, doc):
                st.toast(_(":white_check_mark: Thanks!"))
            else:
                st.toast(_(":exclamation: Failed to send feedback"))

        st.divider()

