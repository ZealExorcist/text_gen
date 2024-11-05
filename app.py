from groq import Groq
import streamlit as st

st.set_page_config(
    page_title="Text Generation Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.subheader("Text Generation Chatbot", divider=True)

client = Groq(api_key=st.secrets["API_KEY"])

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

models = {
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "gemma2-9b-it": {"name": "Gemma2-9b-it", "tokens": 8192, "developer": "Google"},
    "llama3-groq-70b-8192-tool-use-preview": {"name": "LLaMA3-Groq-70b-8192-Tool-Use-Preview", "tokens": 8192, "developer": "Groq"},
    "llama3-groq-8b-8192-tool-use-preview": {"name": "LLaMA3-Groq-8b-8192-Tool-Use-Preview", "tokens": 8192, "developer": "Groq"},
    "llama-3.1-70b-versatile": {"name": "LLaMA-3.1-70b-Versatile", "tokens": 8192, "developer": "Meta"},
    "llama-3.1-8b-instant": {"name": "LLaMA-3.1-8b-Instant", "tokens": 8192, "developer": "Meta"},
    "llama-3.2-1b-preview": {"name": "LLaMA-3.2-1b-Preview", "tokens": 8192, "developer": "Meta"},
    "llama-3.2-3b-preview": {"name": "LLaMA-3.2-3b-Preview", "tokens": 8192, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

model = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=0 
    )

if st.session_state.selected_model != model:
    st.session_state.messages = []
    st.session_state.selected_model = model


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def generate_response(chat):
    for chunk in chat:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.status("Generating response..."):
            stream = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages
                    ],
                    stream=True,
                )
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.stop()

    with st.chat_message("assistant"):
        gen = generate_response(stream)
        full_response = st.write_stream(gen) 

    if isinstance(full_response, str):
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response})
    
