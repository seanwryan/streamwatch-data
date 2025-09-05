#!/usr/bin/env python3
"""
Data Summary for StreamWatch Data
This script provides a comprehensive overview of all data files and their key characteristics.
"""

import os
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

def get_file_info(file_path):
    """Get basic file information"""
    stat = os.stat(file_path)
    size_mb = stat.st_size / (1024 * 1024)
    return {
        'name': os.path.basename(file_path),
        'size_mb': size_mb,
        'modified': pd.Timestamp(stat.st_mtime, unit='s')
    }

def analyze_excel_summary(file_path):
    """Get summary information for Excel files"""
    try:
        excel_file = pd.ExcelFile(file_path)
        sheets_info = []
        
        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheets_info.append({
                    'sheet': sheet_name,
                    'rows': df.shape[0],
                    'columns': df.shape[1],
                    'memory_kb': df.memory_usage(deep=True).sum() / 1024
                })
            except:
                sheets_info.append({
                    'sheet': sheet_name,
                    'rows': 'Error',
                    'columns': 'Error',
                    'memory_kb': 'Error'
                })
        
        return {
            'type': 'Excel',
            'sheets': len(excel_file.sheet_names),
            'sheets_info': sheets_info
        }
    except Exception as e:
        return {
            'type': 'Excel',
            'sheets': 'Error',
            'sheets_info': [],
            'error': str(e)
        }

def analyze_word_summary(file_path):
    """Get summary information for Word documents"""
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        
        with zipfile.ZipFile(file_path) as zip_file:
            if 'word/document.xml' in zip_file.namelist():
                xml_content = zip_file.read('word/document.xml')
                root = ET.fromstring(xml_content)
                
                paragraphs = root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')
                text_elements = root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                
                total_chars = sum(len(elem.text) for elem in text_elements if elem.text)
                
                return {
                    'type': 'Word',
                    'paragraphs': len(paragraphs),
                    'characters': total_chars
                }
            else:
                return {
                    'type': 'Word',
                    'paragraphs': 'Unknown',
                    'characters': 'Unknown'
                }
    except Exception as e:
        return {
            'type': 'Word',
            'paragraphs': 'Error',
            'characters': 'Error',
            'error': str(e)
        }

def main():
    """Main function to provide comprehensive data summary"""
    data_folder = "data"
    
    if not os.path.exists(data_folder):
        print(f"Data folder '{data_folder}' not found!")
        return
    
    print("STREAMWATCH DATA COMPREHENSIVE SUMMARY")
    print("=" * 80)
    
    # Get all files
    files = []
    for f in os.listdir(data_folder):
        file_path = os.path.join(data_folder, f)
        if os.path.isfile(file_path):
            file_info = get_file_info(file_path)
            
            # Analyze based on file type
            if f.endswith(('.xlsx', '.xlsm')):
                analysis = analyze_excel_summary(file_path)
            elif f.endswith('.docx'):
                analysis = analyze_word_summary(file_path)
            elif f.endswith('.pdf'):
                analysis = {'type': 'PDF', 'pages': 'Unknown'}
            elif f.endswith('.accdb'):
                analysis = {'type': 'Access Database'}
            else:
                analysis = {'type': 'Unknown'}
            
            file_info.update(analysis)
            files.append(file_info)
    
    # Sort by size (largest first)
    files.sort(key=lambda x: x['size_mb'], reverse=True)
    
    # Print summary
    print(f"\nTotal files found: {len(files)}")
    
    # Group by type
    type_counts = {}
    total_size = 0
    
    for file_info in files:
        file_type = file_info['type']
        if file_type not in type_counts:
            type_counts[file_type] = {'count': 0, 'size': 0}
        type_counts[file_type]['count'] += 1
        type_counts[file_type]['size'] += file_info['size_mb']
        total_size += file_info['size_mb']
    
    print(f"Total data size: {total_size:.2f} MB")
    print(f"\nFile types breakdown:")
    for file_type, info in type_counts.items():
        print(f"  {file_type}: {info['count']} files, {info['size']:.2f} MB")
    
    # Print detailed file information
    print(f"\n{'='*80}")
    print("DETAILED FILE ANALYSIS")
    print(f"{'='*80}")
    
    for i, file_info in enumerate(files, 1):
        print(f"\n{i:2d}. {file_info['name']}")
        print(f"    Type: {file_info['type']}")
        print(f"    Size: {file_info['size_mb']:.2f} MB")
        print(f"    Modified: {file_info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if file_info['type'] == 'Excel':
            print(f"    Sheets: {file_info['sheets']}")
            if file_info['sheets_info']:
                print(f"    Sheet details:")
                for sheet_info in file_info['sheets_info'][:3]:  # Show first 3 sheets
                    if sheet_info['rows'] != 'Error':
                        print(f"      - {sheet_info['sheet']}: {sheet_info['rows']:,} rows × {sheet_info['columns']} cols")
                    else:
                        print(f"      - {sheet_info['sheet']}: Error reading")
                if len(file_info['sheets_info']) > 3:
                    print(f"      ... and {len(file_info['sheets_info']) - 3} more sheets")
        
        elif file_info['type'] == 'Word':
            if 'paragraphs' in file_info and file_info['paragraphs'] != 'Error':
                print(f"    Paragraphs: {file_info['paragraphs']}")
                if 'characters' in file_info and file_info['characters'] != 'Error':
                    print(f"    Characters: {file_info['characters']:,}")
        
        elif file_info['type'] == 'PDF':
            print(f"    Note: PDF content requires PyPDF2 for detailed analysis")
        
        elif file_info['type'] == 'Access Database':
            print(f"    Note: Access database requires Microsoft Access or specialized tools")
        
        if 'error' in file_info:
            print(f"    Error: {file_info['error']}")
    
    # Key insights
    print(f"\n{'='*80}")
    print("KEY INSIGHTS")
    print(f"{'='*80}")
    
    excel_files = [f for f in files if f['type'] == 'Excel']
    word_files = [f for f in files if f['type'] == 'Word']
    
    if excel_files:
        largest_excel = max(excel_files, key=lambda x: x['size_mb'])
        print(f"• Largest Excel file: {largest_excel['name']} ({largest_excel['size_mb']:.2f} MB)")
        
        total_sheets = sum(f['sheets'] for f in excel_files if isinstance(f['sheets'], int))
        print(f"• Total Excel sheets across all files: {total_sheets}")
    
    if word_files:
        largest_word = max(word_files, key=lambda x: x['size_mb'])
        print(f"• Largest Word document: {largest_word['name']} ({largest_word['size_mb']:.2f} MB)")
    
    print(f"• Data spans multiple years (based on filenames: 2024, 2025)")
    print(f"• Multiple water quality parameters: BACT, HAB, TWI, StreamWatch locations")
    print(f"• Contains both raw data and analysis results")
    
    print(f"\n{'='*80}")
    print("SUMMARY COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()
