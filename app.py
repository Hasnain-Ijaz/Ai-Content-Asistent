import re
import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(
    page_title="AI Content Assistant",
    page_icon="✍️",
    layout="centered"
)

# Title Header
st.title("✍️ AI Content Assistant")
st.write("Generate high-converting, ultra-clean social media posts in seconds.")

# Input Form
with st.form("content_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        content_type = st.selectbox(
            "Content Type",
            ["Social Media Post", "Educational Thread", "Promotional / Ad Copy", "Product Launch", "Short Article Summary"]
        )
        
        platform = st.selectbox(
            "Target Platform",
            ["LinkedIn", "Instagram", "Twitter / X", "Facebook", "YouTube Shorts / Reels Script"]
        )
        
        tone = st.selectbox(
            "Tone of Voice",
            ["Professional & Authoritative", "Casual & Friendly", "Direct & High-Impact", "Witty & Humorous", "Persuasive & Energetic"]
        )

    with col2:
        topic = st.text_input(
            "Topic / Main Idea",
            placeholder="e.g. 5 tips for learning MERN Stack"
        )
        
        target_audience = st.text_input(
            "Target Audience",
            placeholder="e.g. Beginner developers, college students"
        )

    submit_button = st.form_submit_button("✨ Generate Post")

# Generation Logic
if submit_button:
    # Reading variable GROQ_API_KEY from Secrets
    api_key = st.secrets.get("GROQ_API_KEY", "")

    if not api_key:
        st.error("API Key missing in Secrets! Please check app settings.")
    elif not topic:
        st.error("Please enter a topic.")
    else:
        # Simple spinner text
        with st.spinner("Generating your content..."):
            try:
                client = Groq(api_key=api_key)

                # Fetch dynamic live text models
                models_data = client.models.list()
                active_models = [m.id for m in models_data.data if hasattr(m, 'id')]
                text_models = [
                    m for m in active_models 
                    if not any(x in m.lower() for x in ["whisper", "guard", "vision"])
                ]

                if not text_models:
                    st.error("Service temporarily unavailable. Please try again.")
                else:
                    prompt = f"""
                    You are an expert social media content creator and copywriter.
                    Generate a high-performing post based on these exact constraints:

                    - Content Type: {content_type}
                    - Platform: {platform}
                    - Topic: {topic}
                    - Target Audience: {target_audience if target_audience else "General Audience"}
                    - Tone: {tone}

                    Requirements:
                    1. Include a compelling hook on the first line.
                    2. Clean body content formatted with short, scannable paragraphs and bold bullet points.
                    3. Clear Call-To-Action (CTA).
                    4. A dedicated section at the bottom with 5-8 relevant hashtags.
                    5. Do NOT write internal thoughts, reasoning steps, or <think> tags.

                    Format output in clean Markdown.
                    """

                    raw_output = None

                    for model_id in text_models:
                        try:
                            response = client.chat.completions.create(
                                model=model_id,
                                messages=[
                                    {"role": "system", "content": "You are a professional content creation assistant."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.6,
                                max_tokens=1200
                            )
                            raw_output = response.choices[0].message.content
                            break
                        except Exception:
                            continue

                    if raw_output:
                        # Clean reasoning tags
                        clean_content = re.sub(r'<think>.*?</think>', '', raw_output, flags=re.DOTALL).strip()

                        # Display success notification
                        st.success("Content generated successfully!")
                        st.markdown("---")
                        
                        # Direct clean output (No tabs or sections)
                        st.markdown(clean_content)
                        st.markdown("---")

                        # Character count & Download button
                        st.caption(f"📊 Character Count: {len(clean_content)} characters")

                        st.download_button(
                            label="📥 Download Post (.txt)",
                            data=clean_content,
                            file_name="generated_post.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("Unable to generate content right now. Please try again.")

            except Exception as e:
                st.error("An error occurred while generating content. Please try again.")
