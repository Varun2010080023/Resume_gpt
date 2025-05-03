import streamlit as st
import requests
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import PyPDF2

# Set page config
st.set_page_config(
    page_title="Resume & Cover Letter Customizer",
    page_icon="📄",
    layout="wide"
)

# Initialize session state variables
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

if 'last_response' not in st.session_state:
    st.session_state.last_response = ""

def text_to_pdf(text, filename):
    """Convert text content to a PDF file"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Split text into paragraphs and add to PDF
    for para in text.split("\n"):
        if para.strip():  # Skip empty lines
            p = Paragraph(para, styles["Normal"])
            story.append(p)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def extract_text_from_pdf(uploaded_file):
    """Extract text content from uploaded PDF file"""
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def call_deepseek_api(prompt, model="deepseek-chat", max_tokens=2000):
    """Function to call DeepSeek API"""
    headers = {
        "Authorization": f"Bearer {st.session_state.api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload))
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"API call failed: {str(e)}"

def resume_optimizer():
    st.subheader("Resume Optimization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        resume_text = st.text_area(
            "Paste your resume content",
            height=400,
            placeholder="Paste your resume text here..."
        )
        
        uploaded_file = st.file_uploader(
            "Or upload a file (txt, pdf, docx)",
            type=["txt", "pdf", "docx"]
        )
        
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                resume_text = extract_text_from_pdf(uploaded_file)
            else:
                resume_text = uploaded_file.getvalue().decode("utf-8")
    
    with col2:
        job_description = st.text_area(
            "Paste the job description",
            height=200,
            placeholder="Paste the job description here..."
        )
        
        optimization_options = st.multiselect(
            "Optimization options",
            ["ATS Optimization", "Keyword Enhancement", 
             "Achievement Highlighting", "Formatting Cleanup"],
            default=["ATS Optimization", "Keyword Enhancement"]
        )
        
        if st.button("Optimize Resume"):
            if not st.session_state.api_key:
                st.error("Please enter your DeepSeek API key in the sidebar")
                return
            
            if not resume_text:
                st.error("Please provide your resume content")
                return
            
            prompt = f"""
            Optimize the following resume for this job description:
            
            Job Description:
            {job_description}
            
            Resume:
            {resume_text}
            
            Optimization tasks to perform:
            {', '.join(optimization_options)}
            
            Provide the optimized resume with clear before/after comparisons 
            and explanations of changes made.
            """
            
            with st.spinner("Optimizing your resume..."):
                response = call_deepseek_api(prompt)
                st.session_state.last_response = response
            
            st.subheader("Optimized Resume")
            st.write(response)
            
            # Create download buttons for both TXT and PDF
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download as TXT",
                    data=response,
                    file_name="optimized_resume.txt",
                    mime="text/plain"
                )
            with col2:
                pdf_buffer = text_to_pdf(response, "optimized_resume.pdf")
                st.download_button(
                    label="Download as PDF",
                    data=pdf_buffer,
                    file_name="optimized_resume.pdf",
                    mime="application/pdf"
                )

def cover_letter_generator():
    st.subheader("Cover Letter Generator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        resume_text = st.text_area(
            "Paste your resume content (for reference)",
            height=300,
            placeholder="Paste your resume text here...",
            key="cl_resume"
        )
        
        your_name = st.text_input("Your full name")
        your_email = st.text_input("Your email")
        your_phone = st.text_input("Your phone number")
        company_name = st.text_input("Company name")
        hiring_manager = st.text_input("Hiring manager name (if known)")
    
    with col2:
        job_description = st.text_area(
            "Paste the job description",
            height=300,
            placeholder="Paste the job description here...",
            key="cl_job_desc"
        )
        
        tone = st.selectbox(
            "Select tone",
            ["Professional", "Enthusiastic", "Conservative", "Innovative"],
            index=0
        )
        
        length = st.select_slider(
            "Letter length",
            options=["Short", "Medium", "Long"],
            value="Medium"
        )
        
        if st.button("Generate Cover Letter"):
            if not st.session_state.api_key:
                st.error("Please enter your DeepSeek API key in the sidebar")
                return
            
            if not resume_text or not job_description:
                st.error("Please provide both resume content and job description")
                return
            
            prompt = f"""
            Generate a professional cover letter based on the following information:
            
            Applicant Information:
            - Name: {your_name}
            - Email: {your_email}
            - Phone: {your_phone}
            
            Company Information:
            - Company Name: {company_name}
            - Hiring Manager: {hiring_manager if hiring_manager else 'Hiring Manager'}
            
            Job Description:
            {job_description}
            
            Resume Content (for reference):
            {resume_text}
            
            Additional Instructions:
            - Tone: {tone}
            - Length: {length}
            
            The cover letter should highlight relevant skills and experiences from the resume 
            that match the job requirements. It should be personalized and compelling.
            """
            
            with st.spinner("Generating your cover letter..."):
                response = call_deepseek_api(prompt)
                st.session_state.last_response = response
            
            st.subheader("Generated Cover Letter")
            st.write(response)
            
            # Create download buttons for both TXT and PDF
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download as TXT",
                    data=response,
                    file_name=f"cover_letter_{company_name or 'application'}.txt",
                    mime="text/plain"
                )
            with col2:
                pdf_buffer = text_to_pdf(response, f"cover_letter_{company_name or 'application'}.pdf")
                st.download_button(
                    label="Download as PDF",
                    data=pdf_buffer,
                    file_name=f"cover_letter_{company_name or 'application'}.pdf",
                    mime="application/pdf"
                )

def main():
    st.title("📄 Resume & Cover Letter Customizer")
    st.markdown("Optimize your resume and cover letters using AI powered by DeepSeek")
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("Settings")
        st.session_state.api_key = st.text_input(
            "Enter your DeepSeek API key",
            type="password",
            value=st.session_state.api_key
        )
        
        model_choice = st.selectbox(
            "Select model",
            ["deepseek-chat", "deepseek-coder"],
            index=0
        )
        
        temperature = st.slider(
            "Creativity (temperature)",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        
      
    
    # Main tabs
    tab1, tab2 = st.tabs(["Resume Optimizer", "Cover Letter Generator"])
    
    with tab1:
        resume_optimizer()
    
    with tab2:
        cover_letter_generator()

if __name__ == "__main__":
    main()