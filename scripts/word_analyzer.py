#!/usr/bin/env python3
"""
Word Document Analyzer for StreamWatch Data
This script analyzes Word documents and extracts their text content.
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

def analyze_word_document(file_path):
    """Analyze Word documents and extract text content"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {os.path.basename(file_path)}")
    print(f"{'='*80}")
    
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
                    print(f"Total text length: {sum(len(text) for text in text_content):,} characters")
                    
                    # Show first few paragraphs
                    print(f"\nFirst 10 paragraphs:")
                    for i, text in enumerate(text_content[:10]):
                        print(f"{i+1:2d}. {text[:200]}{'...' if len(text) > 200 else ''}")
                        
                    if len(text_content) > 10:
                        print(f"\n... and {len(text_content) - 10} more paragraphs")
                        
                    # Show full content if it's not too long
                    if len(text_content) <= 20:
                        print(f"\n{'='*60}")
                        print("FULL DOCUMENT CONTENT:")
                        print(f"{'='*60}")
                        for i, text in enumerate(text_content, 1):
                            print(f"\n--- Paragraph {i} ---")
                            print(text)
                        
                else:
                    print("Could not find document content in Word file")
        else:
            print("File is not a .docx file")
            
    except Exception as e:
        print(f"Error analyzing Word document: {e}")

def main():
    """Main function to analyze Word documents in the data folder"""
    data_folder = "data"
    
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found!")
        return
    
    print("STREAMWATCH WORD DOCUMENT ANALYSIS")
    print("=" * 80)
    
    # Get Word documents in the data folder
    word_files = []
    for f in os.listdir(data_folder):
        if f.endswith('.docx') and os.path.isfile(os.path.join(data_folder, f)):
            word_files.append(f)
    
    print(f"\nFound {len(word_files)} Word documents:")
    for i, file in enumerate(word_files, 1):
        file_path = os.path.join(data_folder, file)
        file_size = os.path.getsize(file_path) / 1024  # KB
        print(f"  {i}. {file} ({file_size:.2f} KB)")
    
    # Analyze each Word document
    for file in word_files:
        file_path = os.path.join(data_folder, file)
        analyze_word_document(file_path)
    
    print(f"\n{'='*80}")
    print("WORD DOCUMENT ANALYSIS COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
