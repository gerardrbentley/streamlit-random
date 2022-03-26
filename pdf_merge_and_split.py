import tempfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import streamlit as st
import streamlit_pydantic as sp
from typing import Optional, List
from streamlit_pydantic.types import FileContent
from pydantic import BaseModel, Field
from PyPDF2 import PdfFileWriter, PdfFileReader
from PIL import Image

# Make folder for storing user uploads
destination_folder = Path('downloads')
destination_folder.mkdir(exist_ok=True, parents=True)

# Defines what options are in the form
class PDFMergeRequest(BaseModel):
    pdf_uploads: Optional[List[FileContent]] = Field(
        None,
        alias="PDF File to Split",
        description="PDF that needs to be split",
    )

class PDFSplitRequest(BaseModel):
    pages_per_pdf: int = Field(
        1,
        alias="Pages per Split",
        description="How many pages will be in each output pdf. Should evenly divide the total number of pages.",
    )
    pdf_upload: Optional[FileContent] = Field(
        None,
        alias="PDF File to Split",
        description="PDF that needs to be split",
    )

def stack_images(images):
    """adapted from: https://note.nkmk.me/en/python-pillow-concat-images/"""
    first_image = images[0]
    output_image = Image.new('RGB', (first_image.width, sum((image.height for image in images))))
    output_image.paste(first_image, (0, 0))
    starting_y_value = first_image.height
    for image in images[1:]:
        output_image.paste(image, (0, starting_y_value))
        starting_y_value += image.height
    return output_image

pdf_output = '.pdf'
jpg_output = '.jpg'
png_output = '.png'
output_suffix = st.radio('Output File Type', [pdf_output, jpg_output, png_output], key='output_format')
merge = 'Merge Multiple PDFs into One'
split = 'Split One PDF into Multiple'
view_choice = st.radio('PDF Function', (merge, split), key='view_choice')
if view_choice == merge:
    # Get the data from the form, stop running if user hasn't submitted pdfs yet
    data = sp.pydantic_form(key="pdf_merge_form", model=PDFMergeRequest)
    if data is None or data.pdf_uploads is None or len(data.pdf_uploads) < 2:
        st.warning("Upload at least 2 PDFs and press Submit")
        st.stop()

    # Save Uploaded PDFs
    uploaded_paths = []
    for pdf_data in data.pdf_uploads:
        input_pdf_path = destination_folder / f"input_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}.pdf"
        input_pdf_path.write_bytes(pdf_data.as_bytes())
        uploaded_paths.append(input_pdf_path)

    pdf_writer = PdfFileWriter()
    for path in uploaded_paths:
        pdf_reader = PdfFileReader(str(path))
        for page in range(pdf_reader.getNumPages()):
            # Add each page to the writer object
            pdf_writer.addPage(pdf_reader.getPage(page))

    # Write out the merged PDF
    output_pdf_path = destination_folder / f"output_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}.pdf"
    with open(str(output_pdf_path), 'wb') as out:
        pdf_writer.write(out)
    output_path = output_pdf_path
    # Convert to stacked / merged image
    if output_suffix in (png_output, jpg_output):
        # requires poppler on mac? https://stackoverflow.com/questions/43064124/how-to-convert-multipage-pdf-to-list-of-image-objects-in-python
        from pdf2image import convert_from_path

        images = convert_from_path(output_pdf_path)
        stacked_image = stack_images(images)
        output_path = destination_folder / f"output_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}{output_suffix}"
        stacked_image.save(output_path)  # format inferred

    # Allow download
    if output_suffix == pdf_output:
        output_mime = 'application/pdf'
    elif output_suffix == jpg_output:
        output_mime = 'image/jpeg'
    elif output_suffix == png_output:
        output_mime = 'image/png'
    st.download_button('Download Merged Document', output_path.read_bytes(), f"output_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}{output_suffix}", mime=output_mime)
elif view_choice == split:
    # Get the data from the form, stop running if user hasn't submitted pdf yet
    data = sp.pydantic_form(key="pdf_split_form", model=PDFSplitRequest)
    if data is None or data.pdf_upload is None:
        st.warning("Upload a PDF and press Submit")
        st.stop()
    # Save Uploaded PDF
    input_pdf_path = destination_folder / f"input_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}.pdf"
    input_pdf_path.write_bytes(data.pdf_upload.as_bytes())
    # Get PDF Reader
    pdf = PdfFileReader(BytesIO(input_pdf_path.read_bytes()))

    if pdf.numPages % data.pages_per_pdf != 0:
        st.warning(f"Cannot divide pdf with {pdf.numPages} pages into pdfs with {data.pages_per_pdf} pages per")
        st.stop()

    # Split pdf every pages per pdf. Save each split pdf to file
    downloads = []
    for letter_start in range(0, pdf.numPages, data.pages_per_pdf):
        output = PdfFileWriter()
        output_path = input_pdf_path.with_name(f"output_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}.pdf")
        for letter_page in range(data.pages_per_pdf):
            output.addPage(pdf.getPage(letter_start + letter_page))

        with open(output_path, "wb") as f:
            output.write(f)

        # Convert to stacked / merged image
        if output_suffix in (png_output, jpg_output):
            # Requires poppler on mac? https://stackoverflow.com/questions/43064124/how-to-convert-multipage-pdf-to-list-of-image-objects-in-python
            from pdf2image import convert_from_path

            images = convert_from_path(output_path)
            stacked_image = stack_images(images)
            output_path = destination_folder / f"output_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}{output_suffix}"
            stacked_image.save(output_path)  # format inferred

        downloads.append(output_path)
        st.success(f"Saved file {str(output_path)} (original start page {letter_start + 1 } / {pdf.numPages})")

    # Make zip file of all split pdfs
    zip_path = destination_folder / f"output_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}.zip"
    output_zip = ZipFile(str(zip_path), "w")
    for download_path in downloads:
        output_zip.write(str(download_path), arcname=download_path.name)
    output_zip.close()

    # Provide download button of the zip of split pdfs
    st.download_button(f"Download {str(zip_path)}", zip_path.read_bytes(), str(zip_path), mime='application/zip', key=str(zip_path))