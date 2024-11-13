# file: file_utils.py
import streamlit as st
from pathlib import Path

def initialize_session_state():
    """Initialize session state variables"""
    # Initialize all session state variables if they don't exist
    if 'current_question' not in st.session_state:
        st.session_state.current_question = None
    if 'questions_asked' not in st.session_state:
        st.session_state.questions_asked = []
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'assessment_results' not in st.session_state:
        st.session_state.assessment_results = []
    if 'uploaded_files_content' not in st.session_state:
        st.session_state.uploaded_files_content = {}
    if 'submitted_code' not in st.session_state:
        st.session_state.submitted_code = ''

def read_file_content(uploaded_file):
    """Read and return the content of an uploaded file"""
    if uploaded_file is None:
        return None
    
    try:
        # Get the file extension
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        # Read content based on file type
        if file_extension in ['.py', '.txt', '.md', '.json', '.yaml', '.yml', '.css', '.html', '.js']:
            content = uploaded_file.getvalue().decode('utf-8')
        else:
            content = f"Unsupported file type: {file_extension}"
        
        return content
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None