# file: main.py
import streamlit as st
from audio_utils import AudioManager
from file_utils import read_file_content, initialize_session_state
from assessment import analyze_code, evaluate_answer
from report_generator import generate_report
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Set page configuration
    st.set_page_config(
        page_title="Code Assessment Interview",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Add modern UI styling
    st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;
        }
        .css-1d391kg {
            padding: 2rem 1rem;
        }
        .stButton>button {
            border-radius: 20px;
        }
        .stProgress>div>div {
            background-color: #1e88e5;
        }
        .question-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #1e88e5;
            margin-bottom: 20px;
        }
        .evaluation-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state at the very beginning
    initialize_session_state()
    
    # Initialize AudioManager
    audio_manager = AudioManager()
    
    st.title("🎓 Code Assessment Interview")
    
    # Check for API key before proceeding
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        st.error("""
        OpenAI API key not found. Please follow these steps:
        1. Create a .env file in your project directory
        2. Add your OpenAI API key to the .env file like this:
           OPENAI_API_KEY=your-api-key-here
        3. Restart the application
        """)
        return
    
    with st.sidebar:
        st.markdown("### Instructions")
        st.markdown("""
        1. Submit your main code in the text area
        2. Upload any additional related files (optional)
        3. Click 'Start Assessment' to begin
        4. Listen to the questions (automatic)
        5. Click 'Record Answer' to start recording immediately
        6. Wait for AI evaluation
        7. View your report at the end
        """)
    
    # Main code input
    st.markdown("### Main Code")
    code = st.text_area("Submit your main code here:", height=200)
    
    # File upload section
    st.markdown("### Additional Files (Optional)")
    uploaded_files = st.file_uploader("Upload related files:", 
                                    accept_multiple_files=True,
                                    type=['py', 'txt', 'md', 'json', 'yaml', 'yml', 'css', 'html', 'js'])
    
    # Process uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            content = read_file_content(uploaded_file)
            if content is not None:  # Only add if content was successfully read
                st.session_state.uploaded_files_content[uploaded_file.name] = content
    
    if st.button("Start Assessment", type="primary") and code:
        with st.spinner("Analyzing code..."):
            st.session_state.submitted_code = code
            st.session_state.questions_asked = analyze_code(
                code,
                st.session_state.uploaded_files_content
            )
            st.session_state.assessment_results = []
            if st.session_state.questions_asked:
                st.session_state.current_question = 0
                # Initialize current_question_id to None to ensure first question is read
                st.session_state.current_question_id = None
                st.rerun()
    
    # Assessment process
    if st.session_state.submitted_code and st.session_state.current_question is not None:
        st.markdown("### Assessment in Progress")
        
        progress = st.progress((st.session_state.current_question + 1) / len(st.session_state.questions_asked))
        
        current_q = st.session_state.questions_asked[st.session_state.current_question]
        
        # Display question in a card-like container
        st.markdown(
            f"""
            <div class="question-card">
                <h3 style="color: #1e88e5;">Question {st.session_state.current_question + 1}</h3>
                <p>{current_q}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Initialize current_question_id if not present
        if 'current_question_id' not in st.session_state:
            st.session_state.current_question_id = None
            
        # Play question audio when question changes or is first question
        if st.session_state.current_question_id != st.session_state.current_question:
            with st.spinner("Speaking question..."):
                audio_file = audio_manager.text_to_speech(current_q)
                audio_manager.play_audio(audio_file)
            st.session_state.current_question_id = st.session_state.current_question
        
        if st.button("Record Answer", type="primary"):
            answer = audio_manager.record_audio()
            if answer:
                st.markdown(
                    f"""
                    <div class="evaluation-card">
                        <h4>Your Answer:</h4>
                        <p>{answer}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                with st.spinner("Evaluating answer..."):
                    evaluation = evaluate_answer(
                        current_q, 
                        answer, 
                        st.session_state.submitted_code,
                        st.session_state.uploaded_files_content
                    )
                
                if evaluation['assessment'] != 'ERROR':
                    st.markdown(
                        f"""
                        <div class="evaluation-card">
                            <h4>Evaluation:</h4>
                            <p>{evaluation['explanation']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.session_state.assessment_results.append({
                        'question': current_q,
                        'answer': answer,
                        'evaluation': evaluation
                    })
                    
                    if st.session_state.current_question < len(st.session_state.questions_asked) - 1:
                        st.session_state.current_question += 1
                        st.rerun()
                    else:
                        st.success("🎉 Assessment completed!")
                        report = generate_report()
                        st.markdown(report)
                        
                        report_filename = f"assessment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                        st.download_button(
                            label="📥 Download Report",
                            data=report,
                            file_name=report_filename,
                            mime="text/markdown"
                        )
                        
                        st.session_state.current_question = None

if __name__ == "__main__":
    main()