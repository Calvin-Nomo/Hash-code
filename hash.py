# python -m streamlit run hash.py
import hashlib
import streamlit as st

st.header('Hash Code Generator')

# Upload file
file = st.file_uploader('Load a file to be hashed [png, pdf, jpeg, jpg, xls, docx]', type=["png", "pdf", "jpeg", "jpg", "xls", "docx"])

def hash_code_generator(uploaded_file):
    # Read the file content as bytes
    file_content = uploaded_file.read()
    h = hashlib.sha256()
    h.update(file_content)
    hash_code = h.hexdigest()
    return hash_code

st.write('Press the Generate button below')

if st.button('Generate'):
    if not file:
        st.warning('Please upload a file')
    else:
        hash_code = hash_code_generator(file)
        st.code(hash_code, language='text')
        st.success('The hash code is generated successfully')
