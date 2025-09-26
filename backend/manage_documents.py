#!/usr/bin/env python3
"""
Document Management Helper
Use this script to add and manage legal documents in the system.
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

def list_available_documents():
    """List all documents in the data directory."""
    data_dir = Path(__file__).parent.parent / "data"
    
    print("📚 Legal Documents in System")
    print("=" * 50)
    
    if not data_dir.exists():
        print("❌ Data directory not found. Creating it...")
        data_dir.mkdir(parents=True, exist_ok=True)
        return
    
    blawx_files = list(data_dir.glob("*.blawx"))
    
    if not blawx_files:
        print("📄 No documents found. Add .blawx files to the data directory.")
        return
    
    for i, blawx_file in enumerate(blawx_files, 1):
        print(f"{i}. {blawx_file.name}")
        print(f"   📁 Path: {blawx_file}")
        print(f"   📊 Size: {blawx_file.stat().st_size / 1024:.1f} KB")
        print()

def add_document(source_path: str):
    """Add a new .blawx document to the system."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    source = Path(source_path)
    
    if not source.exists():
        print(f"❌ Source file not found: {source_path}")
        return False
    
    if not source.suffix.lower() == '.blawx':
        print(f"❌ File must be a .blawx file, got: {source.suffix}")
        return False
    
    destination = data_dir / source.name
    
    if destination.exists():
        response = input(f"⚠️  Document {source.name} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Operation cancelled.")
            return False
    
    try:
        shutil.copy2(source, destination)
        print(f"✅ Added document: {source.name}")
        print(f"   📁 Copied to: {destination}")
        
        # Test parsing
        from app.services.blawx_parser import BlawxParser
        parser = BlawxParser()
        doc = parser.parse_file(str(destination))
        
        print(f"   📊 Parsed successfully:")
        print(f"      • Provisions: {len(doc.provisions)}")
        print(f"      • s(CASP) Rules: {len(doc.scasp_rules)}")
        print(f"      • Document Name: {doc.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding document: {e}")
        return False

def test_document_parsing():
    """Test parsing all documents in the system."""
    from app.services.blawx_parser import BlawxParser
    
    data_dir = Path(__file__).parent.parent / "data"
    parser = BlawxParser()
    
    print("🧪 Testing Document Parsing")
    print("=" * 50)
    
    for blawx_file in data_dir.glob("*.blawx"):
        print(f"📄 Testing: {blawx_file.name}")
        try:
            doc = parser.parse_file(str(blawx_file))
            print(f"   ✅ Success: {doc.name}")
            print(f"      • {len(doc.provisions)} provisions")
            print(f"      • {len(doc.scasp_rules)} s(CASP) rules")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        print()

def main():
    print("🏛️  Legal AI Assistant - Document Manager")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. List available documents")
        print("2. Add new document")
        print("3. Test document parsing")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            list_available_documents()
        elif choice == '2':
            path = input("Enter path to .blawx file: ").strip()
            if path:
                add_document(path)
        elif choice == '3':
            test_document_parsing()
        elif choice == '4':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please select 1-4.")

if __name__ == "__main__":
    main()