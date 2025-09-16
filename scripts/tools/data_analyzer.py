#!/usr/bin/env python3
"""
Data Analyzer for StreamWatch Data
This script analyzes various file types in the data folder and displays their contents.
"""

import os
import pandas as pd
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def analyze_excel_file(file_path):
    """Analyze Excel files and display sheet information and sample data"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    try:
        # Get basic file info
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"File size: {file_size:.2f} MB")
        
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        print(f"Number of sheets: {len(excel_file.sheet_names)}")
        print(f"Sheet names: {excel_file.sheet_names}")
        
        # Analyze each sheet
        for sheet_name in excel_file.sheet_names:
            print(f"\n--- Sheet: {sheet_name} ---")
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                print(f"Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"Column names: {list(df.columns)}")
                
                # Show data types
                print(f"Data types:")
                for col, dtype in df.dtypes.items():
                    print(f"  {col}: {dtype}")
                
                # Show sample data (first 5 rows)
                if not df.empty:
                    print(f"\nFirst 5 rows:")
                    print(df.head().to_string())
                else:
                    print("Sheet is empty")
                    
            except Exception as e:
                print(f"Error reading sheet {sheet_name}: {e}")
                
    except Exception as e:
        print(f"Error analyzing Excel file: {e}")

def analyze_word_document(file_path):
    """Analyze Word documents and extract text content"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    try:
        # Get basic file info
        file_size = os.path.getsize(file_path) / 1024  # KB
        print(f"File size: {file_size:.2f} KB")
        
        # Try to extract text from .docx (it's a zip file)
        if file_path.endswith('.docx'):
            with zipfile.ZipFile(file_path) as zip_file:
                # Find the main document content
                if 'word/document.xml' in zip_file.namelist():
                    xml_content = zip_file.read('word/document.xml')
                    root = ET.fromstring(xml_content)
                    
                    # Extract text from paragraphs
                    text_content = []
                    for paragraph in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                        text_elements = paragraph.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                        if text_elements:
                            paragraph_text = ''.join([elem.text for elem in text_elements if elem.text])
                            if paragraph_text.strip():
                                text_content.append(paragraph_text.strip())
                    
                    print(f"Number of paragraphs: {len(text_content)}")
                    print(f"Total text length: {sum(len(text) for text in text_content)} characters")
                    
                    # Show first few paragraphs
                    print(f"\nFirst 5 paragraphs:")
                    for i, text in enumerate(text_content[:5]):
                        print(f"{i+1}. {text[:200]}{'...' if len(text) > 200 else ''}")
                        
                    if len(text_content) > 5:
                        print(f"... and {len(text_content) - 5} more paragraphs")
                        
                else:
                    print("Could not find document content in Word file")
        else:
            print("File is not a .docx file")
            
    except Exception as e:
        print(f"Error analyzing Word document: {e}")

def analyze_pdf_file(file_path):
    """Analyze PDF files and extract basic information"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    try:
        # Get basic file info
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"File size: {file_size:.2f} MB")
        
        # Try to extract text using PyPDF2 if available
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                print(f"Number of pages: {num_pages}")
                
                # Extract text from first few pages
                print(f"\nText from first 3 pages:")
                for page_num in range(min(3, num_pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        print(f"\n--- Page {page_num + 1} ---")
                        print(text[:500] + ('...' if len(text) > 500 else ''))
                    else:
                        print(f"\n--- Page {page_num + 1} --- (No text content)")
                        
        except ImportError:
            print("PyPDF2 not available. Install with: pip install PyPDF2")
        except Exception as e:
            print(f"Error reading PDF content: {e}")
            
    except Exception as e:
        print(f"Error analyzing PDF file: {e}")

def analyze_access_database(file_path):
    """Analyze Access database files"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {os.path.basename(file_path)}")
    print(f"{'='*60}")
    
    try:
        # Get basic file info
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"File size: {file_size:.2f} MB")
        
        print("Access database (.accdb) files require Microsoft Access or specialized libraries to read.")
        print("Consider exporting tables to Excel or CSV format for analysis.")
        print("Alternatively, use pyodbc with appropriate drivers to connect to the database.")
        
    except Exception as e:
        print(f"Error analyzing Access database: {e}")

def main():
    """Main function to analyze all files in the data folder"""
    data_folder = "data"
    
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found!")
        return
    
    print("STREAMWATCH DATA ANALYSIS")
    print("=" * 60)
    
    # Get all files in the data folder
    files = [f for f in os.listdir(data_folder) if os.path.isfile(os.path.join(data_folder, f))]
    
    # Group files by type
    excel_files = [f for f in files if f.endswith(('.xlsx', '.xlsm'))]
    word_files = [f for f in files if f.endswith('.docx')]
    pdf_files = [f for f in files if f.endswith('.pdf')]
    access_files = [f for f in files if f.endswith('.accdb')]
    
    print(f"\nFound {len(files)} files:")
    print(f"Excel files: {len(excel_files)}")
    print(f"Word documents: {len(word_files)}")
    print(f"PDF files: {len(pdf_files)}")
    print(f"Access databases: {len(access_files)}")
    
    # Analyze Excel files
    for file in excel_files:
        file_path = os.path.join(data_folder, file)
        analyze_excel_file(file_path)
    
    # Analyze Word documents
    for file in word_files:
        file_path = os.path.join(data_folder, file)
        analyze_word_document(file_path)
    
    # Analyze PDF files
    for file in pdf_files:
        file_path = os.path.join(data_folder, file)
        analyze_pdf_file(file_path)
    
    # Analyze Access databases
    for file in access_files:
        file_path = os.path.join(data_folder, file)
        analyze_access_database(file_path)
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
