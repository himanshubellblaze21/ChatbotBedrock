import streamlit as st
import boto3
import os
from extract_text import extract_text
from bedrockapi import query_bedrock

# AWS S3 Configuration
S3_BUCKET = "chatboatbucket-12345"
s3_client = boto3.client("s3")

os.environ["STREAMLIT_WATCH_FILE"] = "false"

st.title("💬 Document Chatbot")
STATIC_PATH = os.path.join(os.path.dirname(__file__), "../static")
if not os.path.exists(STATIC_PATH):
    os.makedirs(STATIC_PATH)
# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.file_uploaded = False
if "user_query" not in st.session_state:
    st.session_state.user_query = ""
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "upload_message_shown" not in st.session_state:
    st.session_state.upload_message_shown = False

# Display chat area
st.subheader("🗨️ Chat")
chat_container = st.container()

with chat_container:
    for speaker, text in st.session_state.chat_history:
        alignment = "right" if speaker == "You" else "left"
        icon = "🧑‍💻" if speaker == "You" else "🤖 AI:"
        st.markdown(f"<div style='text-align: {alignment}; margin-bottom: 10px;'><strong>{icon} {text}</strong></div>", unsafe_allow_html=True)
    
    st.markdown("---")  # Separator for better spacing
    
    col1, col2 = st.columns([6, 2], gap="medium")  # Adjust spacing
    with col1:
        user_query = st.text_input("Type your question here:", key="user_query_input", value=st.session_state.user_query, label_visibility="collapsed")
    with col2:
        send_button = st.button("💬 Send", key="send_button")
    
    st.markdown("---")  # Separator before file uploader
    
    uploaded_file = st.file_uploader("📂 Upload a document (PDF or DOCX)", type=["pdf", "docx"], key="file_uploader")
    
    if uploaded_file and not st.session_state.file_uploaded:
        file_name = uploaded_file.name
        file_type = uploaded_file.type.split("/")[-1]
        
        # Upload file to S3
        with st.spinner("Uploading file..."):
            s3_client.upload_fileobj(uploaded_file, S3_BUCKET, file_name)
        file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}"
        st.success("File uploaded successfully")
        
        # Extract text from the document stored in S3
        with st.spinner("Extracting text..."):
            document_text = extract_text(file_name, file_type, s3_bucket=S3_BUCKET)
        
        if not document_text.strip():
            st.error("The uploaded document contains no text. Please try another file.")
        else:
            st.session_state.document_text = document_text
            st.session_state.file_uploaded = True
            if not st.session_state.upload_message_shown:
                st.session_state.chat_history.append(("AI", f"File '{file_name}' uploaded successfully! What would you like to search?"))
                st.session_state.upload_message_shown = True
            st.rerun()
    
    if send_button:
        if not st.session_state.file_uploaded or not st.session_state.document_text.strip():
            st.warning("⚠️ Please upload a document first")
        elif user_query:
            with st.spinner("Generating answer..."):
                answer = query_bedrock(st.session_state.document_text, user_query)
            st.session_state.chat_history.append(("You", user_query))
            st.session_state.chat_history.append(("AI", answer))
            
            # Clear the input field
            st.session_state.user_query = ""
            st.rerun()
        else:
            st.warning("⚠️ Please enter a question.")
