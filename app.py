"""
Image Description AI Application
Uses Streamlit for the UI and Ollama's gpt-oss-safeguard model to describe uploaded images.
"""

import streamlit as st
from ollama import chat
from pathlib import Path
import base64

# Page configuration
st.set_page_config(
    page_title="Image Description AI",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("🖼️ Image Description AI")
    st.markdown("---")
    st.markdown("""
    ### How to use:
    1. Upload an image using the file uploader
    2. The AI will automatically describe the content
    3. View the description in the chat interface
    
    ### About:
    This application uses:
    - **Streamlit** for the user interface
    - **Ollama** with the `gpt-oss:20b` model
    - Vision capabilities to analyze images
    """)
    st.markdown("---")
    
    # Clear chat history button
    if st.button("Clear Chat History", type="secondary", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content
st.title("🖼️ Image Description AI")
st.markdown("Upload an image and let AI describe what it sees!")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message.get("avatar")):
        st.markdown(message["content"])
        # Display image if present
        if "image" in message:
            st.image(message["image"], caption="Uploaded Image", use_container_width=True)

# File uploader
uploaded_file = st.file_uploader(
    "Choose an image file",
    type=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
    help="Upload an image file (JPG, PNG, GIF, BMP, or WebP)"
)

# Process uploaded file
if uploaded_file is not None:
    # Read image bytes
    image_bytes = uploaded_file.read()
    
    # Display user message with image
    with st.chat_message("user", avatar="👤"):
        st.markdown("Please describe this image:")
        st.image(image_bytes, caption=uploaded_file.name, width='stretch')
    
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": "Please describe this image:",
        "avatar": "👤",
        "image": image_bytes
    })
    
    # Generate AI response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Analyzing image..."):
            try:
                # Call Ollama chat with image
                response = chat(
                    model='gpt-oss:20b',
                    messages=[{
                        'role': 'user',
                        'content': 'Describe this image in detail. What objects, people, or scenes do you see? What are the colors, composition, and mood?',
                        'images': [image_bytes]
                    }]
                )
                
                # Display response
                ai_response = response.message.content
                st.markdown(ai_response)
                
                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": ai_response,
                    "avatar": "🤖"
                })
                
            except Exception as e:
                error_message = f"Error: {str(e)}\n\nMake sure Ollama is running and the 'gpt-oss:20b' model is installed."
                st.error(error_message)
                
                # Add error to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "avatar": "🤖"
                })

# Instructions if no image uploaded yet
if not uploaded_file and len(st.session_state.messages) == 0:
    st.info("👆 Upload an image above to get started!")
    
    # Example section
    with st.expander("💡 Tips for best results"):
        st.markdown("""
        - **Clear images**: Upload high-quality, well-lit images for better descriptions
        - **Supported formats**: JPG, PNG, GIF, BMP, and WebP
        - **File size**: Keep files under 10MB for faster processing
        - **Content**: The AI can describe objects, people, scenes, colors, and mood
        """)
