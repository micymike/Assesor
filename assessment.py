# file: assessment.py
import streamlit as st
import openai
import os
from dotenv import load_dotenv

def get_openai_client():
    """Initialize and return OpenAI client with error handling"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    return openai.OpenAI(api_key=api_key)

def analyze_code(code, additional_files=None):
    """Analyze code and generate initial questions"""
    try:
        client = get_openai_client()
    except ValueError as e:
        st.error(str(e))
        return []

    context = f"Main code:\n{code}\n\n"
    if additional_files:
        context += "Additional files:\n"
        for filename, content in additional_files.items():
            context += f"\n{filename}:\n{content}\n"
    
    prompt = f"""
    Analyze this code and related files, then generate 2-3 relevant questions to test the student's understanding:
    {context}
    
    Generate questions that test both basic understanding and deeper concepts.
    Consider the relationships between files when generating questions.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        questions = [q.strip() for q in response.choices[0].message.content.split('\n') if q.strip()]
        return questions
    except Exception as e:
        st.error(f"Error analyzing code: {str(e)}")
        return []

def evaluate_answer(question, answer, code_context, additional_files=None):
    """Evaluate student's answer and decide on follow-up"""
    try:
        client = get_openai_client()
    except ValueError as e:
        st.error(str(e))
        return {
            'assessment': 'ERROR',
            'explanation': str(e),
            'followup': None,
            'score': 0
        }

    context = f"Main code:\n{code_context}\n\n"
    if additional_files:
        context += "Additional files:\n"
        for filename, content in additional_files.items():
            context += f"\n{filename}:\n{content}\n"
            
    prompt = f"""
    Context: Student submitted this code and related files:
    {context}
    
    Question asked: {question}
    Student's answer: {answer}
    
    Evaluate the answer considering:
    1. Correctness
    2. Completeness
    3. Understanding of concepts
    4. Understanding of file relationships (if applicable)
    
    Provide your response in exactly this format (including the score number):
    ASSESSMENT_TYPE|Explanation text|Follow-up question text|X
    where:
    - ASSESSMENT_TYPE is either GOOD or NEEDS_FOLLOWUP
    - X is a number from 0 to 10
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content.strip()
        parts = content.split('|')
        
        if len(parts) != 4:
            return {
                'assessment': 'ERROR',
                'explanation': 'Invalid response format from evaluation',
                'followup': None,
                'score': 0
            }
            
        try:
            score = float(parts[3].strip())
        except (ValueError, TypeError):
            score = 0
            
        return {
            'assessment': parts[0].strip(),
            'explanation': parts[1].strip(),
            'followup': parts[2].strip() if parts[2].strip().lower() != 'none' else None,
            'score': score
        }
    except Exception as e:
        st.error(f"Error evaluating answer: {str(e)}")
        return {
            'assessment': 'ERROR',
            'explanation': 'There was an error evaluating the answer.',
            'followup': None,
            'score': 0
        }