"""
Image Description AI Application
Uses Streamlit for the UI and Ollama's gpt-oss:20b model to describe uploaded images.
Allows users to ask questions about the uploaded image.
"""

import streamlit as st
from ollama import chat

# Page configuration
st.set_page_config(
    page_title="Image Description AI",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "image_uploaded" not in st.session_state:
    st.session_state.image_uploaded = False

# Sidebar
with st.sidebar:
    st.title(" Image Description AI")
    st.markdown("---")
    st.markdown("""
    ### How to use:
    1. Upload an image using the file uploader
    2. Ask questions about the image
    3. Get AI-powered responses
    
    ### About:
    This application uses:
    - **Streamlit** for the user interface
    - **Ollama** with the gpt-oss:20b model
    - Vision capabilities to analyze images
    """)
    st.markdown("---")
    
    # Clear chat history button
    if st.button("Clear Chat History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_image = None
        st.session_state.image_uploaded = False
        st.rerun()

# Main content
st.title(" Image Description AI")
st.markdown("Upload an image and ask questions about it!")

# File uploader
uploaded_file = st.file_uploader(
    "Choose an image file",
    type=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
    help="Upload an image file (JPG, PNG, GIF, BMP, or WebP)"
)

# Handle image upload
if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    
    # Check if this is a new image
    if st.session_state.current_image != uploaded_file.name:
        st.session_state.current_image = uploaded_file.name
        st.session_state.image_uploaded = True
        st.session_state.messages = []  # Clear previous conversation
        
        # Store image bytes in session state
        st.session_state.image_bytes = image_bytes
        
        # Add initial message about image upload
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"Image '{uploaded_file.name}' uploaded successfully! Ask me anything about this image."
        })

# Display current image if available
if st.session_state.image_uploaded and hasattr(st.session_state, 'image_bytes'):
    with st.container():
        st.image(st.session_state.image_bytes, caption=st.session_state.current_image, width=400)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input - only show if image is uploaded
if st.session_state.image_uploaded:
    if prompt := st.chat_input("Ask a question about the image..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Call Ollama chat with image
                    response = chat(
                        model='gpt-oss:20b',
                        messages=[{
                            'role': 'user',
                            'content': prompt,
                            'images': [st.session_state.image_bytes]
                        }]
                    )
                    
                    # Display response
                    ai_response = response.message.content
                    st.markdown(ai_response)
                    
                    # Add assistant message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                    
                except Exception as e:
                    error_message = f"Error: {str(e)}\n\nMake sure Ollama is running and the 'gpt-oss:20b' model is installed."
                    st.error(error_message)
                    
                    # Add error to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })
else:
    # Instructions if no image uploaded yet
    st.info(" Upload an image above to get started!")
    
    # Example section
    with st.expander(" Tips for best results"):
        st.markdown("""
        - **Clear images**: Upload high-quality, well-lit images for better descriptions
        - **Supported formats**: JPG, PNG, GIF, BMP, and WebP
        - **File size**: Keep files under 10MB for faster processing
        - **Ask anything**: You can ask about objects, colors, people, text, emotions, or any details in the image
        
        ### Example questions:
        - "What do you see in this image?"
        - "What colors are dominant in this picture?"
        - "Can you describe the mood or atmosphere?"
        - "Are there any people in this image?"
        - "What text can you read in this image?"
        """)
