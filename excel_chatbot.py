#Import Libraries
import os
import openai
import tempfile
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
import tempfile
from embedchain import App


st.set_page_config(page_title="LangChain: Chat with Excel", page_icon="🦜")
st.title("🦜 LangChain: Chat with Excel Documents")
#Loads environment variables such as API-KEY.
_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")


@st.cache_resource
def parse_docs(files):
    """
    Parse a list of files and add them to the application.

    Args:
        files (List[str]): A list of file paths to be parsed.

    Returns:
        App: The application object with the parsed files added.

    This function uses the `App.from_config` method to create an application object
    using the configuration file specified by `config_path`. It then iterates over
    each file in the `files` list and adds it to the application using the `add`
    method with the `data_type` parameter set to "excel_file". Finally, it returns
    the application object.

    Note:
        This function is decorated with `@st.cache_resource`, which means that the
        result of this function will be cached and reused if the same input is passed
        again.
    """
    app = App.from_config(config_path="config.yaml")
    for file in files:
        app.add(file, data_type="excel_file")
        
    return app

@st.cache_resource(experimental_allow_widgets=True)       
def request_files(): 
    """
    Caches the function `request_files` using the `@st.cache_resource` decorator.
    This function prompts the user to enter their OpenAI API key and uploads Excel files.
    
    Returns:
        qa_app (App): The application object with the parsed Excel files added.
    """
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
    st.sidebar.info("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")
    if not openai_api_key:
        st.sidebar.info("Please add your OpenAI API key to continue.")
        st.stop()    
    def upload_files():
        uploaded_files = st.sidebar.file_uploader(
        label="Upload Excel files", type=["xlsx", "xls"], accept_multiple_files=True
    )

        if uploaded_files:
            temp_files = []
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(uploaded_file.getvalue())
                    temp_files.append(temp_file.name)
            return temp_files
        st.sidebar.warning(f"Please upload all your documents here")
        st.stop()
    rfp_files = upload_files()
    
    qa_app = parse_docs(rfp_files)
    return qa_app

# Setup memory for contextual conversation
msgs = StreamlitChatMessageHistory()

qa = request_files()

#This function clears chat messages. This function clears chat blocks.
if len(msgs.messages) == 0 or st.sidebar.button("Clear message history"):
    msgs.clear()
    msgs.add_ai_message("How can I help you?")

# AI assistant and user messages start here.
avatars = {"human": "user", "ai": "assistant"}
for msg in msgs.messages:
    st.chat_message(avatars[msg.type]).write(msg.content)

#Query/Prompt Variable
if user_query := st.chat_input(placeholder="Ask me anything!"):
    st.chat_message("user").write(user_query)
    msgs.add_user_message(user_query)
    
    #AI Assistant message
    with st.chat_message("assistant"):
        response = qa.query(user_query)
        st.write(response)
        msgs.add_ai_message(response)
        