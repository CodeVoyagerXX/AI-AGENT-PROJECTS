import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# 1. Setup API 
genai.configure(api_key="ENTER YOUR GEMINI API")
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="Research Assistant", layout="wide")
st.title("📄 PDF Research Assistant")

# --- SESSION STATE INITIALIZATION ---
if "messages" not in st.session_state:
    st.session_state.messages = [] 
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = "" 

# --- SIDEBAR: PDF UPLOAD & DOWNLOAD ---
with st.sidebar:
    st.header("Files & Export")
    uploaded_file = st.file_uploader("Upload your paper", type="pdf")
    
    if uploaded_file and not st.session_state.pdf_text:
        reader = PdfReader(uploaded_file)
        # Efficiently join all page text
        st.session_state.pdf_text = "".join([page.extract_text() for page in reader.pages])
        st.success("PDF Processed!")

    st.divider()

    # --- DOWNLOAD TRANSCRIPT LOGIC ---
    if st.session_state.messages:
        # Create the text content for the file
        transcript = "--- RESEARCH CHAT TRANSCRIPT ---\n\n"
        for msg in st.session_state.messages:
            role = "ASSISTANT" if msg["role"] == "assistant" else "USER"
            transcript += f"{role}:\n{msg['content']}\n\n"
            transcript += "-"*30 + "\n\n"
        
        st.download_button(
            label="💾 Download Transcript",
            data=transcript,
            file_name="research_notes.txt",
            mime="text/plain"
        )

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask something about the PDF..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # Sending context + question
        full_context = f"PDF Context: {st.session_state.pdf_text[:15000]}\n\nUser Question: {prompt}"
        
        stream = model.generate_content(full_context, stream=True)
        
        def stream_parser():
            for chunk in stream:
                yield chunk.text

        response_text = st.write_stream(stream_parser)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
