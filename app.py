import streamlit as st
from openai import OpenAI
import database as db
import os

# Automatically fetch API key from Streamlit secrets or system environment
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

# Initialize database schema on app start
db.init_db()

st.set_page_config(page_title="PARASA CHATBOT", page_icon="🤖", layout="wide")

# Ensure an active session ID exists
sessions = db.get_all_sessions()
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = sessions[0]["id"] if sessions else db.create_session()
    sessions = db.get_all_sessions()

# --- SIDEBAR: CHAT MANAGEMENT ---
with st.sidebar:
    st.title("💬 Chat Sessions")
    
    # Only show the input box if no key is configured in secrets
    if not api_key:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    else:
        st.caption("🔒 *API Key securely loaded from secrets*")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.current_session_id = db.create_session()
        st.rerun()

    st.divider()
    st.subheader("Previous Chats")

    for s in sessions:
        col1, col2 = st.columns([0.82, 0.18])
        is_active = (s["id"] == st.session_state.current_session_id)
        label = f"👉 {s['title']}" if is_active else s["title"]

        with col1:
            if st.button(label, key=f"session_{s['id']}", use_container_width=True):
                st.session_state.current_session_id = s["id"]
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"del_{s['id']}"):
                db.delete_session(s["id"])
                if st.session_state.current_session_id == s["id"]:
                    remaining = db.get_all_sessions()
                    st.session_state.current_session_id = remaining[0]["id"] if remaining else db.create_session()
                st.rerun()

# --- MAIN CHAT WINDOW ---
st.title("🤖 PARASA CHATBOT")

current_session_id = st.session_state.current_session_id
messages = db.get_session_messages(current_session_id)

# Render chat history
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt
if prompt := st.chat_input("Type your message here..."):
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()

    client = OpenAI(api_key=api_key)

    # Automatically set title from the first question
    if len(messages) == 0:
        title = prompt[:25] + ("..." if len(prompt) > 25 else "")
        db.update_session_title(current_session_id, title)

    # 1. Save user prompt & display it
    db.save_message(current_session_id, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Build history context for OpenAI
    system_instruction = {
        "role": "system",
        "content": "You are PARASA CHATBOT, a helpful, polite, and intelligent AI assistant."
    }
    api_messages = [system_instruction] + [{"role": m["role"], "content": m["content"]} for m in messages]
    api_messages.append({"role": "user", "content": prompt})

    # 3. Stream AI response & display it
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=api_messages,
            stream=True,
        )
        response_text = st.write_stream(stream)

    # 4. Save response & refresh sidebar title
    db.save_message(current_session_id, "assistant", response_text)
    st.rerun()