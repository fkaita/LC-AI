import streamlit as st
import requests
import os

# FastAPI backend URL
API_BASE_URL = "http://127.0.0.1:8000"

# Directory to store uploaded files
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.title("🤖 AI L/C Reviewer")

# File Upload Section
st.subheader("Upload a File")
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "png", "jpg"])

if uploaded_file:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    
    # Save the uploaded file locally
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.success(f"Uploaded {uploaded_file.name} successfully!")

# List files in the upload directory
st.subheader("Select Files")
files = os.listdir(UPLOAD_DIR)

# Initialize selected files
if "selected_files" not in st.session_state:
    st.session_state.selected_files = []

if files:
    st.session_state.selected_files = st.multiselect("Select two files for processing", files, default=files[:2])
    
    for file in files:
        col1, col2 = st.columns([4, 1])
        col1.write(file)
        if col2.button("🗑️ Delete", key=file):
            os.remove(os.path.join(UPLOAD_DIR, file))
            st.success(f"Deleted {file}")
            st.rerun()

st.subheader("Review Files")
# Process selected files
if len(st.session_state.selected_files) == 2:
    if st.button("⚙️ AI Review"):
        data = {
            "lc_filepath": os.path.join(UPLOAD_DIR, st.session_state.selected_files[0]),
            "contract_filepath": os.path.join(UPLOAD_DIR, st.session_state.selected_files[1])
        }
        response = requests.post(f"{API_BASE_URL}/review/", json=data,  stream=True)

        progress_bar = st.progress(0)
        step_count = 4  # Number of processing steps

        final_response = []
        capture_final_message = False 

        for i, content in enumerate(response.iter_lines()):
            if content:
                content = content.decode("utf-8")
                print(content)
                if "progress-message: " in content:
                    content = content.replace("progress-message: ", "")
                    # Update progress bar
                    progress_bar.progress((i + 1) / step_count, text=content)

                # Capture final response
                if "final-message: " in content:
                    content = content.replace("final-message: ", "")
                    capture_final_message = True
                
                # If inside final message, accumulate lines
                if capture_final_message:
                    final_response.append(content)
                 

        st.success("🎉 Processing complete!")
        full_final_message = "\n".join(final_response)

        if full_final_message:
            st.subheader("📄 AI Review Result")
            st.markdown(full_final_message, unsafe_allow_html=True)


        # if response.status_code == 200:
        #     st.success(f"Processing Result: {response.json()['result']}")
        # else:
        #     st.error(f"Error: {response.json()['detail']}")

else:
    st.warning("No files uploaded yet.")

