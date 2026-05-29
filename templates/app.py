from __future__ import annotations
import streamlit as st
import requests
from typing import List

# -----------------------------
# CONFIG
# -----------------------------
API_BASE_URL = "http://localhost:8080"

st.set_page_config(
    page_title="MultiDocChat",
    page_icon="📄",
    layout="wide"
)


# -----------------------------
# SESSION STATE
# -----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# CUSTOM CSS
# -----------------------------
st.markdown("""
<style>
.main {
    padding-top: 0rem;
}

.chat-container {
    border-radius: 12px;
    padding: 10px;
}

.user-msg {
    background-color: #005ee1;
    color: white;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    margin-left: 25%;
}

.assistant-msg {
    background-color: #f1f3f6;
    color: black;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
    margin-right: 25%;
}

.block-container {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# SIDEBAR - FILE UPLOAD
# -----------------------------
with st.sidebar:
    st.title("📄 MultiDocChat")

    st.markdown("### Upload Documents")

    uploaded_files = st.file_uploader(
        "Choose files",
        accept_multiple_files=True
    )

    upload_btn = st.button("Upload & Index")

    if upload_btn:

        if not uploaded_files:
            st.warning("Please upload at least one file.")
        else:
            try:
                with st.spinner("Uploading and indexing documents..."):

                    files = []

                    for file in uploaded_files:
                        files.append(
                            (
                                "files",
                                (
                                    file.name,
                                    file.getvalue(),
                                    file.type
                                )
                            )
                        )

                    response = requests.post(
                        f"{API_BASE_URL}/upload",
                        files=files
                    )

                    if response.status_code == 200:
                        data = response.json()

                        st.session_state.session_id = data["session_id"]
                        st.session_state.messages = []

                        st.success("Documents indexed successfully.")

                    else:
                        st.error(response.json().get("detail", "Upload failed"))

            except Exception as e:
                st.error(f"Error: {e}")

    st.divider()

    if st.session_state.session_id:
        st.success("Session Active")

        st.code(st.session_state.session_id)

# -----------------------------
# MAIN CHAT AREA
# -----------------------------
st.title("💬 Chat With Your Documents")

if not st.session_state.session_id:
    st.info("Upload documents from the left sidebar to start chatting.")

else:

    # -----------------------------
    # DISPLAY CHAT HISTORY
    # -----------------------------
    for msg in st.session_state.messages:

        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-msg">
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            st.markdown(
                f"""
                <div class="assistant-msg">
                    {msg["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

    # -----------------------------
    # CHAT INPUT
    # -----------------------------
    prompt = st.chat_input("Ask something about your documents...")

    if prompt:

        # Add user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.spinner("Thinking..."):

                payload = {
                    "session_id": st.session_state.session_id,
                    "message": prompt
                }

                response = requests.post(
                    f"{API_BASE_URL}/chat",
                    json=payload
                )

                if response.status_code == 200:

                    answer = response.json()["answer"]

                    # Save assistant response
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer
                        }
                    )

                    # Display assistant response
                    with st.chat_message("assistant"):
                        st.markdown(answer)

                else:
                    error_msg = response.json().get("detail", "Chat failed")

                    st.error(error_msg)

        except Exception as e:
            st.error(f"Error: {e}")