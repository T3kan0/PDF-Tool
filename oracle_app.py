#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import streamlit as st
import pandas as pd
import time
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
#import pypdf
from streamlit_pdf_viewer import pdf_viewer
import base64
from PyPDF2 import PdfWriter
from io import BytesIO
import zipfile
import math

st.set_page_config(
    page_title="FileMerger",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)


uploaded_file = st.sidebar.file_uploader('Upload Files',
                                     type=['pdf'],
                                     accept_multiple_files=True,
                                     key='pdf')

st.sidebar.markdown('---')


if 'uploaded_file' not in st.session_state:
        st.session_state['uploaded_file'] = []

else:
    st.session_state['uploaded_file'] = uploaded_file
    
c1, c2 = st.columns([50, 50])

if len(uploaded_file) >= 0:
    with c1:
        st.markdown('<div style="text-align: center;"><img src="https://i.postimg.cc/gJzPdRYd/logio.png" alt="Alt Text" width="300"></div>', unsafe_allow_html=True)
        #st.header('Centre for Teaching and Learning')
        st.markdown('<h3 style="color:maroon;text-align: center">Centre for Teaching and Learning</h3>', unsafe_allow_html=True)       
        #st.markdown('---')
        st.info(' ')
    with c2:
        st.markdown('<h1 style="color:midnightblue;text-align: center">A_STEP: Oracle v.1.0.0</h1>', unsafe_allow_html=True)
        st.markdown('---')
        genre = st.radio(
        ":red[**How Can Oracle Help You with Your Files?**]💡",
        [":rainbow[**Combine PDF**]", ":rainbow[**Split/Separate PDF**]"],
        captions = ["Default: Stacking Files Atop One Another 📕📗📘➡️📚",
                "Separates Files: From One Document to Many 📚➡️📕📗📘"]
        )
        #st.write(' ')
        st.markdown('---')

# Set a fixed height for the iframes
iframe_height = 600

if st.session_state['uploaded_file'] is not None:
    if genre == ":rainbow[**Combine PDF**]":

        # Sidebar with columns inside
        with st.sidebar:
            c0, c01 = st.columns([50, 50])
    
        with c0:
            aggreg = st.button(':red[Combine PDF]')    
        with c01:
            st.empty()
            if aggreg:
                if len(uploaded_file) == 0:
                        st.warning('Upload PDF to continue!', icon="⚠️")
        
        # Limit to the first two files
        for i, pdf_file in enumerate(st.session_state['uploaded_file'][:2]):
            binary_data = pdf_file.getvalue()

        
            # Display the files in the respective columns
            if i == 0:
                with c1:                
                    pdf_viewer(input=binary_data, width=700, height = iframe_height)
            elif i == 1:
                with c2:
                    pdf_viewer(input=binary_data, width=700, height = iframe_height)
        st.markdown('---')
        if aggreg:
            if len(uploaded_file) >= 1:                
                merger = PdfWriter()
                output_pdf = BytesIO()
            
                for j in uploaded_file:
                    pdf_reader = PdfReader(j)
                    for page in range(len(pdf_reader.pages)):
                        merger.add_page(pdf_reader.pages[page])
                
                merger.write(output_pdf)
                merger.close()
                output_pdf.seek(0)            
                st.success('Files Successfully Edited!', icon="✅")
                if aggreg:
                    with c01:
                        btn = st.download_button(
                            label=":red[Download]",
                            data=output_pdf,
                            file_name='merged-pdf.pdf',
                            mime="application/pdf",
                            key="download_concat"
                        )

            
    else:          
        # Limit to the first two files
        for i, pdf_file in enumerate(st.session_state['uploaded_file'][:1]):
            #num_chunks = st.sidebar.text_input("Pages", "50")
            num_chunks = st.sidebar.number_input("Number of chunks", min_value=1, value=2)
            # Sidebar with columns inside
            with st.sidebar:
                c0, c01 = st.columns([35, 65])
    
            with c0:
                split = st.button(':red[Split PDF]')
   
            with c01:
                if split:
                    st.success('Files Successfully Edited!', icon="✅")
                        

            pages_to_remove = st.sidebar.text_input("Pages to remove (comma-separated, e.g., 1,3,5)")
            rem = st.sidebar.button(':red[Remove PDF]')
   
            
            binary_data = pdf_file.getvalue()
            # Convert binary data to a file-like object
            pdf_stream = BytesIO(binary_data)
            # Extract information from the uploaded file
            pdf_reader = PdfReader(pdf_stream)
            num_pages = len(pdf_reader.pages)
            title = pdf_reader.metadata.get('/Title', 'Unknown Title')
            author = pdf_reader.metadata.get('/Author', 'Unknown Author')
            with c1:    
                pdf_viewer(input=binary_data, width=700, height = iframe_height)
            with c2:
                st.markdown("<h2 style='color:midnightblue;text-align: Center;'>PDF Intel</h2>", unsafe_allow_html=True)
                st.markdown('---')
                st.write(f":blue[Title:] {title}")
                st.write(f":blue[Author:] {author}")
                st.write(f":blue[Number of pages in the PDF file:] {num_pages}")

            # Convert page_chunk to an integer
            try:
                pages_per_chunk = int(num_chunks)
            except ValueError:
                st.error("Please enter a valid number for pages per chunk.")
                num_chunks = 50  # Fallback to default value
            if split:
                chunks = []
                pages_per_chunk = math.ceil(num_pages / num_chunks)                
                chunk_counter = 1  # Initialize chunk counter
                
                for i in range(0, num_pages, pages_per_chunk):
                    writer = PdfWriter()
                    # Add pages to the writer object
                    for j in range(i, min(i + pages_per_chunk, num_pages)):
                        page = pdf_reader.pages[j]
                        writer.add_page(page)

                    # Save the chunk to a BytesIO object
                    output_pdf = BytesIO()
                    writer.write(output_pdf)
                    output_pdf.seek(0)

                    # Append the chunk to the list of chunks
                    chunk_name = f"chunk_{chunk_counter}.pdf"
                    chunks.append((chunk_name, output_pdf))
             

                    chunk_counter += 1  # Increment chunk counter

                # Debugging output to check the number of chunks created
                st.write(f"Total chunks created: {len(chunks)}")

                # Create a zip file in memory
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for chunk_name, output_pdf in chunks:
                        output_pdf.seek(0)  # Ensure we're at the start of the BytesIO object       
                        # Write each PDF chunk to the zip file
                        zip_file.writestr(chunk_name, output_pdf.read())
                zip_buffer.seek(0)
                # Provide download button for the zip file
                if split:
                        with c2:
                            st.download_button(
                                label=":blue[Download All PDFs as Zip]",
                                data=zip_buffer,
                                file_name="pdf_chunks.zip",
                                mime="application/zip",
                                key="d_zip"
                            )

    

            if rem:
                try:
                    pages_to_remove = [int(page.strip()) - 1 for page in pages_to_remove.split(",")]
                    pdf_reader = PdfReader(pdf_file)
                    pdf_writer = PdfWriter()

                    for page_num in range(len(pdf_reader.pages)):
                        if page_num not in pages_to_remove:
                            pdf_writer.add_page(pdf_reader.pages[page_num])                        

                            output_pd = BytesIO()
                            pdf_writer.write(output_pd)
                            output_pd.seek(0)
                        
                            st.success('Pages Successfully Removed!', icon="✅")

                except Exception as e:
                    st.error(f"Error processing PDF: {e}")
                with c2:
                # Provide download button for the edited PDF
                    dwnld = st.download_button(
                        label=":blue[Download Edited PDF]",
                        data=output_pd,
                        file_name="removed_pages.pdf",
                        mime="application/pdf",
                        key="load_buttn"
                )
                        
                
            st.info("Upload a PDF file to get started.")    


    
