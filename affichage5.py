import streamlit as st
import os, tempfile, re
from pdf2image import convert_from_bytes

# ------------ LangChain 0.2 imports (community / openai) -------------------------
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import (
    ChatPromptTemplate, SystemMessagePromptTemplate,
    MessagesPlaceholder, HumanMessagePromptTemplate
)

# ------------ Config Streamlit ---------------------------------------------------
st.set_page_config(page_title="Chat Notarial (Fichorga)", page_icon="📄", layout="wide")

def clean(txt: str) -> str:
    txt = re.sub(r"\n\s*\n", "\n\n", txt)
    txt = re.sub(r"\n", " ", txt)
    return re.sub(r"\s{2,}", " ", txt).strip()

# ------------ Mémoire & Prompt ---------------------------------------------------
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    input_key="question",
    output_key="answer"
)

prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "Tu es un assistant notarial. Tu réponds toujours en français, "
        "de manière concise et factuelle.\n\n"
        "Tu peux t'appuyer aussi bien sur le CONTEXTE (extrait du PDF) "
        "que sur l'HISTORIQUE DE LA CONVERSATION pour répondre.\n"
        "Si l'information n'est nulle part, dis simplement : 'Je ne sais pas'.\n\n"
        "CONTEXTE :\n{context}"
    ),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{question}")
])


llm = ChatOpenAI(
    model_name="deepseek",
    base_url="http://vllm:8000/v1",
    api_key="sk-no-key",
    temperature=0,
    streaming=True,
)

# ------------ Session State ------------------------------------------------------
st.session_state.setdefault("pdf_text", "")
st.session_state.setdefault("messages_ui", [])
st.session_state.setdefault("chat_ready", False)

# ------------ Sidebar : upload PDF ----------------------------------------------
with st.sidebar:
    st.header("📄 Ajouter un PDF")
    up = st.file_uploader("Déposez un PDF", type="pdf")
    

    if up:
        st.success("PDF chargé ✔️")
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, up.name)
            open(p, "wb").write(up.getvalue())
            docs = PyPDFLoader(p).load()

        st.session_state.pdf_text = "\n\n".join(clean(d.page_content) for d in docs)
        st.session_state.chat_ready = True

        st.markdown("### Aperçu")
        for i, img in enumerate(convert_from_bytes(up.getvalue(), size=(800, None))):
            st.image(img, caption=f"Page {i+1}", use_container_width=True)

# ------------ Header -------------------------------------------------------------
col1, col2 = st.columns([6, 1])
with col1:
    st.title("💬 Chat Notarial (By Fichorga)")
with col2:
    if st.button("↺ Reset"):
        memory.clear()
        st.session_state.messages_ui.clear()
        st.session_state.chat_ready = False
        st.session_state.pdf_text = ""
        st.rerun()  

# ------------ Afficher l’historique UI ------------------------------------------
for m in st.session_state.messages_ui:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ------------ Interaction --------------------------------------------------------
if st.session_state.chat_ready and (user_q := st.chat_input("Posez votre question…")):
    # 1) afficher la question
    st.session_state.messages_ui.append({"role": "user", "content": user_q})
    with st.chat_message("user"):
        st.markdown(user_q)

    # 2) construire les messages pour le LLM
    msgs = prompt.format_messages(
        context=st.session_state.pdf_text,
        question=user_q,
        chat_history=memory.buffer
    )

    # 3) streamer la réponse token par token
    answer = ""
    with st.chat_message("assistant"):
        placeholder = st.empty()                     # ✅ plus de msg_box.empty()
        for chunk in llm.stream(msgs):
            answer += chunk.content
            placeholder.markdown(answer + "▌")
        placeholder.markdown(answer)

    # 4) sauver mémoire + UI
    memory.save_context({"question": user_q}, {"answer": answer})
    st.session_state.messages_ui.append({"role": "assistant", "content": answer})

# ------------ Dark mode ----------------------------------------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"] {background:#0e1117!important;color:#fafafa!important;}
    </style>
    """,
    unsafe_allow_html=True,
)























