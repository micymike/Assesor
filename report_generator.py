# file: report_generator.py
import streamlit as st
from datetime import datetime

def generate_report():
    """Generate a comprehensive report of the assessment in markdown format"""
    report_content = []
    
    # Add date
    report_content.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Add the submitted code section
    report_content.append("# Submitted Code\n")
    report_content.append(st.session_state.submitted_code + "\n")
    
    # Calculate overall score
    total_score = sum(result['evaluation']['score'] for result in st.session_state.assessment_results)
    average_score = total_score / len(st.session_state.assessment_results) if st.session_state.assessment_results else 0
    
    # Add overall score section
    report_content.append("# Overall Score\n")
    report_content.append(f"Average Score: {average_score:.2f}/10\n")
    
    # Add question breakdown section
    report_content.append("# Question-by-Question Breakdown\n")
    
    # Add individual question results
    for i, result in enumerate(st.session_state.assessment_results, 1):
        report_content.append(f"## Question {i}\n")
        report_content.append(f"{i}. {result['question']}\n")
        report_content.append(f"Student's Answer: {result['answer']}\n")
        report_content.append(f"Evaluation: {result['evaluation']['explanation']}\n")
        report_content.append(f"Score: {result['evaluation']['score']}/10\n")
        
        if result['evaluation']['followup']:
            report_content.append(f"Follow-up Question: {result['evaluation']['followup']}\n")
    
    # Join all content with newlines
    return "\n".join(report_content)