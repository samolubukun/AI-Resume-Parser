import streamlit as st
import openai
import json
import pandas as pd
import io
import PyPDF2
import pdfplumber
from typing import List, Dict, Any

# Set page configuration
st.set_page_config(
    page_title="CV Parser App",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = []
if 'api_key_set' not in st.session_state:
    st.session_state.api_key_set = False

def extract_applicant_details(resume_text: str, client) -> Dict[str, Any]:
    """Extract details from a given resume text using OpenAI API."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a resume-parsing assistant."},
                {"role": "user", "content": f"Extract the name, email, skills, and years of experience from this resume:\n\n{resume_text}"}
            ],
            functions=[
                {
                    "name": "extract_details",
                    "description": "Extract applicant details from a resume",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "skills": {"type": "array", "items": {"type": "string"}},
                            "experience_years": {"type": "number"}
                        },
                        "required": ["name", "email", "skills", "experience_years"]
                    }
                }
            ],
            function_call={"name": "extract_details"}
        )
        return json.loads(response.choices[0].message.function_call.arguments)
    except Exception as e:
        st.error(f"Error extracting details: {str(e)}")
        return None

def process_single_resume(resume_text: str, client) -> Dict[str, Any]:
    """Process a single resume text."""
    return extract_applicant_details(resume_text, client)

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file using multiple methods for better accuracy."""
    try:
        # Method 1: Try pdfplumber first (better for complex layouts)
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        if text.strip():
            return text
        
        # Method 2: Fallback to PyPDF2 if pdfplumber fails
        pdf_file.seek(0)  # Reset file pointer
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def process_multiple_pdfs(pdf_files: List, client) -> List[Dict[str, Any]]:
    """Process multiple PDF files."""
    extracted_details = []
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, pdf_file in enumerate(pdf_files):
        status_text.text(f'Processing PDF {i+1} of {len(pdf_files)}: {pdf_file.name}')
        progress_bar.progress((i + 1) / len(pdf_files))
        
        # Extract text from PDF
        resume_text = extract_text_from_pdf(pdf_file)
        
        if resume_text.strip():
            details = extract_applicant_details(resume_text, client)
            if details:
                details['source_file'] = pdf_file.name  # Add source file info
                extracted_details.append(details)
        else:
            st.warning(f"⚠️ Could not extract text from {pdf_file.name}")
    
    status_text.text('PDF processing complete!')
    return extracted_details

def process_resumes_from_dataframe(df: pd.DataFrame, client, num_rows: int = 5) -> List[Dict[str, Any]]:
    """Process multiple resumes from a DataFrame."""
    extracted_details = []
    
    # Check if the required column exists
    if 'Resume_str' not in df.columns:
        st.error("The column 'Resume_str' was not found in the CSV file.")
        return []
    
    # Select the specified number of resumes
    resumes = df['Resume_str'].head(num_rows).tolist()
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, resume in enumerate(resumes):
        status_text.text(f'Processing resume {i+1} of {len(resumes)}...')
        progress_bar.progress((i + 1) / len(resumes))
        
        details = extract_applicant_details(resume, client)
        if details:
            extracted_details.append(details)
    
    status_text.text('Processing complete!')
    return extracted_details

def main():
    st.title("📄 CV Parser Application")
    st.markdown("---")
    
    # Sidebar for API key input
    with st.sidebar:
        st.header("🔑 OpenAI Configuration")
        api_key = st.text_input(
            "Enter your OpenAI API Key:",
            type="password",
            help="Your API key is not stored and only used for this session."
        )
        
        if api_key:
            try:
                client = openai.OpenAI(api_key=api_key)
                st.success("✅ API Key set successfully!")
                st.session_state.api_key_set = True
            except Exception as e:
                st.error(f"❌ Invalid API Key: {str(e)}")
                st.session_state.api_key_set = False
        else:
            st.warning("⚠️ Please enter your OpenAI API key to continue.")
            st.session_state.api_key_set = False
    
    # Main content area
    if st.session_state.api_key_set:
        client = openai.OpenAI(api_key=api_key)
        
        # Tab selection
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Text Input", "📄 PDF Upload", "📊 Multiple PDFs", "📋 CSV Batch", "📈 Results"])
        
        with tab1:
            st.header("Text Input Processing")
            
            # Text area for manual resume input
            resume_text = st.text_area(
                "Paste resume text here:",
                height=300,
                placeholder="Enter the resume text you want to analyze..."
            )
            
            if st.button("🔍 Extract Details", key="single_process"):
                if resume_text.strip():
                    with st.spinner("Processing resume..."):
                        details = process_single_resume(resume_text, client)
                        if details:
                            st.success("✅ Resume processed successfully!")
                            
                            # Display results
                            col1, col2 = st.columns(2)
                            with col1:
                                st.subheader("📋 Extracted Information")
                                st.write(f"**Name:** {details.get('name', 'N/A')}")
                                st.write(f"**Email:** {details.get('email', 'N/A')}")
                                st.write(f"**Experience:** {details.get('experience_years', 'N/A')} years")
                            
                            with col2:
                                st.subheader("🛠️ Skills")
                                skills = details.get('skills', [])
                                if skills:
                                    for skill in skills:
                                        st.write(f"• {skill}")
                                else:
                                    st.write("No skills extracted")
                            
                            # Add to session results
                            st.session_state.processed_data.append(details)
                else:
                    st.warning("⚠️ Please enter resume text to process.")
        
        with tab2:
            st.header("Single PDF Upload")
            
            # PDF file uploader
            uploaded_pdf = st.file_uploader(
                "Upload a single PDF resume",
                type=['pdf'],
                help="Upload a PDF file containing a resume to extract information"
            )
            
            if uploaded_pdf is not None:
                st.success(f"✅ PDF uploaded: {uploaded_pdf.name}")
                
                # Show PDF info
                st.info(f"📄 File size: {len(uploaded_pdf.getvalue()) / 1024:.1f} KB")
                
                if st.button("🔍 Extract from PDF", key="pdf_process"):
                    with st.spinner("Extracting text from PDF..."):
                        resume_text = extract_text_from_pdf(uploaded_pdf)
                        
                        if resume_text.strip():
                            st.success("✅ Text extracted successfully!")
                            
                            # Show extracted text preview
                            with st.expander("📄 View Extracted Text"):
                                st.text_area("Extracted Text:", resume_text, height=200, disabled=True)
                            
                            # Process the extracted text
                            with st.spinner("Processing resume with AI..."):
                                details = process_single_resume(resume_text, client)
                                if details:
                                    details['source_file'] = uploaded_pdf.name
                                    st.success("✅ Resume processed successfully!")
                                    
                                    # Display results
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.subheader("📋 Extracted Information")
                                        st.write(f"**Name:** {details.get('name', 'N/A')}")
                                        st.write(f"**Email:** {details.get('email', 'N/A')}")
                                        st.write(f"**Experience:** {details.get('experience_years', 'N/A')} years")
                                        st.write(f"**Source:** {details.get('source_file', 'N/A')}")
                                    
                                    with col2:
                                        st.subheader("🛠️ Skills")
                                        skills = details.get('skills', [])
                                        if skills:
                                            for skill in skills:
                                                st.write(f"• {skill}")
                                        else:
                                            st.write("No skills extracted")
                                    
                                    # Add to session results
                                    st.session_state.processed_data.append(details)
                        else:
                            st.error("❌ Could not extract text from PDF. Please try a different file.")
        
        with tab3:
            st.header("Multiple PDF Processing")
            
            # Multiple PDF file uploader
            uploaded_pdfs = st.file_uploader(
                "Upload multiple PDF resumes",
                type=['pdf'],
                accept_multiple_files=True,
                help="Upload multiple PDF files to process them in batch"
            )
            
            if uploaded_pdfs:
                st.success(f"✅ {len(uploaded_pdfs)} PDF files uploaded")
                
                # Show uploaded files
                st.subheader("📁 Uploaded Files:")
                for i, pdf in enumerate(uploaded_pdfs, 1):
                    st.write(f"{i}. {pdf.name} ({len(pdf.getvalue()) / 1024:.1f} KB)")
                
                if st.button("🚀 Process All PDFs", key="multiple_pdf_process"):
                    with st.spinner("Processing multiple PDFs..."):
                        batch_results = process_multiple_pdfs(uploaded_pdfs, client)
                        if batch_results:
                            st.session_state.processed_data.extend(batch_results)
                            st.success(f"✅ Successfully processed {len(batch_results)} out of {len(uploaded_pdfs)} PDFs!")
                        else:
                            st.error("❌ Failed to process PDFs.")
        
        with tab4:
            st.header("CSV Batch Processing")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Upload CSV file with resumes",
                type=['csv'],
                help="CSV file should contain a 'Resume_str' column with resume text"
            )
            
            if uploaded_file is not None:
                try:
                    # Read the uploaded file
                    df = pd.read_csv(uploaded_file)
                    
                    st.success(f"✅ File uploaded successfully! Found {len(df)} resumes.")
                    
                    # Show preview
                    st.subheader("📊 Data Preview")
                    st.dataframe(df.head())
                    
                    # Number of rows to process
                    num_rows = st.slider(
                        "Number of resumes to process:",
                        min_value=1,
                        max_value=min(len(df), 20),
                        value=min(5, len(df))
                    )
                    
                    if st.button("🚀 Process Batch", key="batch_process"):
                        with st.spinner("Processing batch..."):
                            batch_results = process_resumes_from_dataframe(df, client, num_rows)
                            if batch_results:
                                st.session_state.processed_data.extend(batch_results)
                                st.success(f"✅ Successfully processed {len(batch_results)} resumes!")
                            else:
                                st.error("❌ Failed to process resumes.")
                
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
        
        with tab5:
            st.header("Processing Results")
            
            if st.session_state.processed_data:
                st.success(f"📊 Total processed resumes: {len(st.session_state.processed_data)}")
                
                # Display results in a table
                results_df = pd.DataFrame(st.session_state.processed_data)
                st.dataframe(results_df, use_container_width=True)
                
                # Download options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Download as JSON
                    json_data = json.dumps(st.session_state.processed_data, indent=2)
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_data,
                        file_name="extracted_resumes.json",
                        mime="application/json"
                    )
                
                with col2:
                    # Download as CSV
                    csv_data = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name="extracted_resumes.csv",
                        mime="text/csv"
                    )
                
                with col3:
                    # Clear results
                    if st.button("🗑️ Clear Results"):
                        st.session_state.processed_data = []
                        st.rerun()
                
                # Summary statistics
                st.subheader("📈 Summary Statistics")
                if results_df is not None and not results_df.empty:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_experience = results_df['experience_years'].mean()
                        st.metric("Average Experience", f"{avg_experience:.1f} years")
                    with col2:
                        total_candidates = len(results_df)
                        st.metric("Total Candidates", total_candidates)
                    with col3:
                        # Most common skills
                        all_skills = []
                        for skills_list in results_df['skills']:
                            if isinstance(skills_list, list):
                                all_skills.extend(skills_list)
                        if all_skills:
                            most_common_skill = max(set(all_skills), key=all_skills.count)
                            st.metric("Most Common Skill", most_common_skill)
            
            else:
                st.info("🔍 No processed resumes yet. Use the other tabs to process resumes.")
    
    else:
        st.info("🔑 Please enter your OpenAI API key in the sidebar to get started.")
        
        # Instructions
        st.markdown("""
        ## How to use this app:
        
        1. **Enter your OpenAI API Key** in the sidebar
        2. **Choose processing mode:**
           - **Text Input**: Paste and analyze resume text directly
           - **PDF Upload**: Upload a single PDF resume
           - **Multiple PDFs**: Upload and process multiple PDF resumes
           - **CSV Batch**: Upload a CSV file with multiple resume texts
        3. **View and download results** in the Results tab
        
        ### Supported Formats:
        - **Text**: Direct text input
        - **PDF**: Single or multiple PDF files
        - **CSV**: File with 'Resume_str' column containing resume text
        
        ### Features:
        - ✅ Secure API key handling (not stored)
        - ✅ PDF text extraction with fallback methods
        - ✅ Extract name, email, skills, and experience
        - ✅ Batch processing with progress tracking
        - ✅ Export results as JSON or CSV
        - ✅ Summary statistics and insights
        - ✅ Source file tracking for uploaded documents
        """)

if __name__ == "__main__":
    main()