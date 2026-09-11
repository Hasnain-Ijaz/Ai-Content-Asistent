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
        # Clean spinner text without API key mention
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
                    You are an elite copywriter. Generate content strictly following these rules:
                    Do NOT write internal thoughts, reasoning steps, or <think> tags.

                    ### OUTPUT FORMAT REQUIREMENTS:
                    Create TWO distinct sections separated clearly:

                    SECTION 1: METADATA
                    ## 📌 Post Overview
                    - **Platform:** {platform}
                    - **Target Audience:** {target_audience if target_audience else "General Audience"}
                    - **Tone:** {tone}
                    - **Type:** {content_type}

                    SECTION 2: POST CONTENT
                    ## ✍️ Post Content

                    [Write post here]:
                    1. HOOK: Single attention-grabbing first line.
                    2. SPACING: Short, scannable paragraphs (1-2 sentences).
                    3. BULLETS: Bold key points for easy reading.
                    4. VALUE: Zero filler words. Pinpoint exact facts.
                    5. CTA: Clear action step at the bottom.
                    6. HASHTAGS: 5-8 relevant hashtags at the end.

                    Constraints:
                    - Topic: {topic}
                    - Platform: {platform}
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

                        # Separate overview and post content
                        sections = clean_content.split("## ✍️ Post Content")
                        
                        metadata_part = sections[0].strip() if len(sections) > 1 else "## 📌 Post Overview"
                        post_part = sections[1].strip() if len(sections) > 1 else clean_content

                        # Display success notification
                        st.success("Content generated successfully!")

                        # UI Tabs (Same exact layout)
                        tab1, tab2, tab3 = st.tabs(["👁️ Formatted View", "📋 Copy Code", "📊 Post Details"])

                        with tab1:
                            st.markdown(post_part)

                        with tab2:
                            st.code(post_part, language="markdown")

                        with tab3:
                            st.markdown(metadata_part)
                            st.caption(f"Character Count: {len(post_part)} characters")

                        st.download_button(
                            label="📥 Download Post (.txt)",
                            data=post_part,
                            file_name="social_post.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("Unable to generate content right now. Please try again.")

            except Exception as e:
                st.error("An error occurred while generating content. Please try again.")
