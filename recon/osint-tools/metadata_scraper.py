"""
Document Metadata Scraper
Extracts sensitive metadata (Author, Software, OS paths) from PDF, DOCX, and XLSX files.
Useful for identifying internal naming conventions and software versions.
"""

import sys
import os
import json
import traceback

# Framework integration
current_dir = os.path.dirname(os.path.abspath(__file__))
framework_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
source_dir = os.path.join(framework_root, "source")

if source_dir not in sys.path:
    sys.path.append(source_dir)

try:
    from core.database import DatabaseManagment
    has_db = True
except ImportError:
    has_db = False

#!#!#!
name: "Metadata Scraper"
description: "Extracts hidden metadata from documents (PDF, DOCX, XLSX). Uncovers authors, internal paths, and software versions."
category: "OSINT"
author: "Donald Ford"
#!#!#!

# Optional dependencies for parsing
try:
    import PyPDF2
    has_pdf = True
except ImportError:
    has_pdf = False

try:
    from docx import Document
    has_docx = True
except ImportError:
    has_docx = False

try:
    import openpyxl
    has_xlsx = True
except ImportError:
    has_xlsx = False

def scrape_pdf(file_path):
    if not has_pdf: return {"error": "PyPDF2 not installed"}
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            info = reader.metadata
            return {str(k): str(v) for k, v in info.items()}
    except Exception as e:
        return {"error": str(e)}

def scrape_docx(file_path):
    if not has_docx: return {"error": "python-docx not installed"}
    try:
        doc = Document(file_path)
        prop = doc.core_properties
        return {
            "author": prop.author,
            "created": str(prop.created),
            "last_modified_by": prop.last_modified_by,
            "revision": prop.revision,
            "title": prop.title
        }
    except Exception as e:
        return {"error": str(e)}

def scrape_xlsx(file_path):
    if not has_xlsx: return {"error": "openpyxl not installed"}
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        prop = wb.properties
        return {
            "creator": prop.creator,
            "lastModifiedBy": prop.lastModifiedBy,
            "created": str(prop.created),
            "modified": str(prop.modified),
            "title": prop.title
        }
    except Exception as e:
        return {"error": str(e)}

def Start(args=None):
    path = ""
    if args:
        path = args[0]
    
    if not path or not os.path.exists(path):
        print("[-] Error: A valid file path or directory is required.")
        print("[*] Note: This module scans local files found in .loot or other directories.")
        return

    files_to_scan = []
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith(('.pdf', '.docx', '.xlsx')):
                    files_to_scan.append(os.path.join(root, f))
    else:
        files_to_scan.append(path)

    if not files_to_scan:
        print("[-] No supported documents found to scan.")
        return

    print(f"[*] Starting metadata extraction on {len(files_to_scan)} files...")
    
    results = {}
    for f_path in files_to_scan:
        ext = os.path.splitext(f_path)[1].lower()
        print(f"[*] Processing: {os.path.basename(f_path)}")
        
        meta = {}
        if ext == '.pdf': meta = scrape_pdf(f_path)
        elif ext == '.docx': meta = scrape_docx(f_path)
        elif ext == '.xlsx': meta = scrape_xlsx(f_path)
        
        if meta:
            results[f_path] = meta
            for k, v in meta.items():
                if v and v != 'None':
                    print(f"    - {k}: {v}")

    # No database sync for this tool yet, as it's purely for operator intelligence
    print(f"\n[+] Extraction Complete. {len(results)} files contained metadata.")

if __name__ == "__main__":
    Start(sys.argv[1:])
