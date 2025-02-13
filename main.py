"""
PDF Document Analysis Tool
This script processes PDF documents and generates various analysis outputs including
markdown content, layout analysis, and content structure.
"""

import os
from typing import Tuple
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

def setup_directories(output_dir: str, images_dir: str) -> None:
    """Create necessary output directories if they don't exist."""
    os.makedirs(images_dir, exist_ok=True)

def get_writers(pdf_dir: str) -> Tuple[FileBasedDataWriter, FileBasedDataWriter]:
    """Initialize file writers for images and markdown content.
    
    Args:
        pdf_dir: Directory containing the source PDF
    
    Returns:
        Tuple containing image_writer and markdown_writer
    """
    images_dir = os.path.join(pdf_dir, "images")
    return FileBasedDataWriter(images_dir), FileBasedDataWriter(pdf_dir)

def process_pdf(pdf_path: str) -> None:
    """Process a PDF file and generate analysis outputs.
    
    Args:
        pdf_path: Path to the PDF file to process
    """
    try:
        # Get PDF directory and base filename
        pdf_dir = os.path.dirname(pdf_path)
        name_without_suff = os.path.splitext(os.path.basename(pdf_path))[0]
        images_dir = os.path.join(pdf_dir, "images")
        
        # Setup directories
        setup_directories(pdf_dir, images_dir)
        
        # Initialize writers
        image_writer, md_writer = get_writers(pdf_dir)
        
        # Read PDF content
        reader = FileBasedDataReader("")
        pdf_bytes = reader.read(pdf_path)
        
        # Create and process dataset
        ds = PymuDocDataset(pdf_bytes)
        
        # Determine processing mode and get results
        if ds.classify() == SupportedPdfParseMethod.OCR:
            infer_result = ds.apply(doc_analyze, ocr=True)
            pipe_result = infer_result.pipe_ocr_mode(image_writer)
        else:
            infer_result = ds.apply(doc_analyze, ocr=False)
            pipe_result = infer_result.pipe_txt_mode(image_writer)

        # Generate output files
        output_files = {
            "model": f"{name_without_suff}_model.pdf",
            "layout": f"{name_without_suff}_layout.pdf",
            "spans": f"{name_without_suff}_spans.pdf",
            "markdown": f"{name_without_suff}.md",
            "content_list": f"{name_without_suff}_content_list.json",
            "middle_json": f"{name_without_suff}_middle.json"
        }
        
        # Save analysis results
        infer_result.draw_model(os.path.join(pdf_dir, output_files["model"]))
        pipe_result.draw_layout(os.path.join(pdf_dir, output_files["layout"]))
        pipe_result.draw_span(os.path.join(pdf_dir, output_files["spans"]))
        
        # Generate and save content
        image_dir = "images"  # Relative path to images
        pipe_result.dump_md(md_writer, output_files["markdown"], image_dir)
        pipe_result.dump_content_list(md_writer, output_files["content_list"], image_dir)
        pipe_result.dump_middle_json(md_writer, output_files["middle_json"])
        
        print(f"Successfully processed {pdf_path}")
        print(f"Output files saved in {pdf_dir}")
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise

def main():
    """Main entry point of the script."""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python main.py <pdf_file_path>")
        sys.exit(1)
        
    pdf_file_path = sys.argv[1]
    process_pdf(pdf_file_path)

if __name__ == "__main__":
    main()