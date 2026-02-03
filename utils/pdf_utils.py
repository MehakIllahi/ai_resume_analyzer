from pdfminer.high_level import extract_text
import streamlit as st

def extract_pdf_text(uploaded_file):
    try:
        extracted_text = extract_text(uploaded_file)
        return extracted_text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return "Could not extract text from the PDF file."

def extract_pdf_text(uploaded_file):
    try:
        return extract_text(uploaded_file)
    except Exception:
        return ""
