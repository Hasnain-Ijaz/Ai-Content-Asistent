import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(page_title="AI Content Assistant", page_icon="✍️", layout="centered")

st.title("✍️ AI Content Assistant")
st.write("Generate tailored posts, captions, and relevant hashtags using Groq LLM.")

# Sidebar - API Key Configuration
st.sidebar.header("🔑 API Settings")
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# Form Inputs
with st.form("content_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        content_type = st.selectbox(
            "Content Type",
            ["Social Media Post", "Blog Intro", "Product Description", "Newsletter Entry", "Ad Copy"]
        )
        platform = st.selectbox(
            "Target Platform",
            ["LinkedIn", "Twitter/X", "Instagram", "Facebook", "Medium"]
        )
        tone = st.selectbox(
            "Tone of Voice",
            ["Professional", "Casual & Friendly", "Persuasive", "Informative", "Humorous", "Inspirational"]
        )
        
    with col2:
        topic = st.text_input("Topic / Main Focus", placeholder="e.g., AI in Web Development")
        target_audience = st.text_input("Target Audience", placeholder="e.g., Developers, Freelancers")

    submit_btn = st.form_submit_button("Generate Content 🚀")

# Function to generate content via Groq API
def generate_content(api_key, content_type, platform, topic, target_audience, tone):
    client = Groq(api_key=api_key)
    
    prompt = f"""
    You are an expert digital content creator.
    Generate a complete post based on these specifications:
    - Content Type: {content_type}
    - Target Platform: {platform}
    - Topic: {topic}
    - Target Audience: {target_audience}
    - Tone: {tone}

    Format the response clearly with three dedicated sections:
    1. **Post Content** (Optimized for {platform})
    2. **Catchy Caption**
    3. **Relevant Hashtags** (Provide 5 to 10 relevant hashtags)
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000,
    )
    return response.choices[0].message.content

# Processing output
if submit_btn:
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar to proceed.")
    elif not topic or not target_audience:
        st.warning("Please fill in both Topic and Target Audience.")
    else:
        with st.spinner("Crafting your content..."):
            try:
                result = generate_content(api_key, content_type, platform, topic, target_audience, tone)
                
                st.success("Content Generated Successfully!")
                st.subheader("📝 Your Output:")
                st.markdown(result)
                
                # Download button for generated post
                st.download_button(
                    label="📥 Download Content as Text File",
                    data=result,
                    file_name=f"{platform.lower().replace('/', '_')}_post.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Error generating content: {e}")
