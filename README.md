# AI Resume Parser

---

## 📄 Overview

The **AI Resume Parser** is a powerful Streamlit application designed to efficiently extract key information from resumes. Leveraging the advanced capabilities of **OpenAI's GPT-4o model**, it can parse resumes from various formats, including **plain text, single or multiple PDF files, and CSV batches**. This tool is ideal for recruiters, HR professionals, and anyone needing to quickly process and organize applicant data.

---

## ✨ Features

* **Multi-format Input**: Process resumes from:
    * **Text Input**: Paste raw resume text directly.
    * **Single PDF Upload**: Upload and parse individual PDF resumes.
    * **Multiple PDF Uploads**: Batch process numerous PDF resumes simultaneously.
    * **CSV Batch Processing**: Upload a CSV file containing resume texts in a dedicated column (`Resume_str`).
* **AI-Powered Extraction**: Utilizes **OpenAI's GPT-4o** to accurately extract:
    * **Name**
    * **Email**
    * **Skills** (as a list)
    * **Years of Experience**
* **Secure API Key Handling**: Your OpenAI API key is securely handled and **not stored**; it's only used for the current session.
* **Progress Tracking**: Monitor the processing of multiple files with real-time progress bars.
* **Results Dashboard**: View all processed data in a clean, interactive table.
* **Data Export**: Download extracted information in **JSON** or **CSV** formats.
* **Summary Statistics**: Get quick insights such as average experience, total candidates, and most common skills.
* **Source File Tracking**: Each processed resume from file uploads includes its original filename for easy reference.

---

## 🚀 Getting Started

### Prerequisites

* An **OpenAI API Key**. You can obtain one from the [OpenAI Platform](https://platform.openai.com/account/api-keys).

### Installation

1.  **Clone the repository**:

    ```bash
    git clone [https://github.com/samolubukun/AI-Resume-Parser.git](https://github.com/samolubukun/AI-Resume-Parser.git)
    cd AI-Resume-Parser
    ```

2.  **Install the required libraries**:

    ```bash
    pip install streamlit openai pandas PyPDF2 pdfplumber
    ```

### How to Run

1.  **Run the Streamlit application** from your terminal within the cloned repository directory:

    ```bash
    streamlit run resumeparser.py
    ```

2.  The application will open in your web browser.

---

## 🖥️ Usage

1.  **Enter your OpenAI API Key** in the sidebar on the left.
2.  **Select a tab** in the main content area based on your input type:
    * **Text Input**: Paste a resume and click "Extract Details."
    * **PDF Upload**: Upload a single PDF and click "Extract from PDF."
    * **Multiple PDFs**: Upload multiple PDF files and click "Process All PDFs."
    * **CSV Batch**: Upload a CSV file (with a `Resume_str` column) and select the number of rows to process, then click "Process Batch."
3.  **Navigate to the "Results" tab** to view the extracted data, download the results, or clear the session data.

---

## 🛠️ Technical Details

The application uses:

* **Streamlit**: For creating the interactive web interface.
* **OpenAI Python Client**: To interact with the GPT-4o model for resume parsing.
* **`pdfplumber` and `PyPDF2`**: For robust text extraction from PDF files, with `pdfplumber` as the primary method and `PyPDF2` as a fallback for better compatibility.
* **Pandas**: For handling CSV data and presenting results in a structured DataFrame.
* **JSON**: For structured data output and export.


