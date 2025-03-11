import streamlit as st
import boto3
import os
from extract_text import extract_text
from bedrockapi import query_bedrock

# AWS S3 Configuration
S3_BUCKET = "chatboatbucket-12345"
s3_client = boto3.client("s3")

os.environ["STREAMLIT_WATCH_FILE"] = "false"

st.set_page_config(page_title="Document Chatbot")

# Custom CSS for chat styling (Reduced width of chat messages)
st.markdown(
    """
    <style>
        body {
            background-color: #9833C3; 
            color: white; 
        }
        .chat-container {
            max-width: 600px; /* Reduced width */
            margin: auto;
        }
        .chat-bubble {
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            display: inline-block;
            max-width: 70%; /* Reduce message width */
            color: white;
        }
        .user {
            background-color: #9833C3;
            text-align: right;
            float: right;
            clear: both;
            margin-right: 10px;
        }
        .ai {
            background-color: #7633A3; /* Slightly darker for AI */
            text-align: left;
            float: left;
            clear: both;
            margin-left: 10px;
        }
        @media (max-width: 900px) {
            .chat-container {
                margin: 0 10px;
            }
        }
        div.stButton > button {
            background-color: #9833C3; /* Purple Background */
            color: white;  /* White text */
            border-radius: 10px; /* Rounded Corners */
            padding: 10px 20px; /* Padding for better size */
            font-size: 16px; /* Adjust font size */
            border: none; /* Remove border */
        }
        div.stButton > button:hover {
            background-color: #6C238E; /* Darker Purple on Hover */
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.write("Use the chat on the right to interact with your document.")
    st.markdown("---")
    
    uploaded_file = st.file_uploader("Upload a document (PDF or DOCX)", type=["pdf", "docx"], key="file_upload_sidebar")  # Unique key
    
    # Add "Clear Chat History" Button
    if st.button("🗑️ Clear Chat History", key="clear_chat"):
        st.session_state.chat_history = []  # Reset chat history
        st.session_state.user_query = ""  # Clear input field
        st.rerun()  # Refresh the app


st.markdown(
    "<h1 style='text-align: center;'>💬 Document Chatbot</h1>",
    unsafe_allow_html=True
)
st.write("")
st.write("")
st.write("")
st.write("")

STATIC_PATH = os.path.join(os.path.dirname(__file__), "../static")
if not os.path.exists(STATIC_PATH):
    os.makedirs(STATIC_PATH)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.file_uploaded = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "upload_message_shown" not in st.session_state:
    st.session_state.upload_message_shown = False
if "user_query" not in st.session_state:
    st.session_state.user_query = ""

# Chat Area

chat_container = st.container()

with chat_container:
    for speaker, text in st.session_state.chat_history:
        alignment = "user" if speaker == "You" else "ai"
        icon = "🧑‍💻" if speaker == "You" else "🤖 AI:"
        st.markdown(f"<div class='chat-bubble {alignment}'><strong>{icon}</strong> {text}</div>", unsafe_allow_html=True)

    st.markdown("---")

    col1, col2 = st.columns([6, 2], gap="medium")
    with col1:
        user_query = st.text_input("Type your question here:", key="user_query_input", value=st.session_state.user_query, label_visibility="collapsed")
    with col2:
        send_button = st.button("💬 Send", key="send_button")




# Upload & Process File
if uploaded_file and not st.session_state.file_uploaded:
    file_name = uploaded_file.name
    file_type = uploaded_file.type.split("/")[-1]

    # Upload file to S3
    with st.spinner("Uploading file..."):
        s3_client.upload_fileobj(uploaded_file, S3_BUCKET, file_name)

    file_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}"
    # st.success("File uploaded successfully")

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

# Handle Chat Submission
if send_button:
    if not st.session_state.file_uploaded or not st.session_state.document_text.strip():
        st.warning("⚠️ Please upload a document first")
    elif user_query:
        with st.spinner("Generating answer..."):
            answer = query_bedrock(st.session_state.document_text, user_query)

        # Append chat history
        st.session_state.chat_history.append(("You", user_query))
        st.session_state.chat_history.append(("AI", answer))

        # Clear the input field by resetting session state
        st.session_state.user_query = ""

        # **Force UI refresh to reflect the cleared input field**
        st.rerun()
    else:
        st.warning("⚠️ Please enter a question.")




