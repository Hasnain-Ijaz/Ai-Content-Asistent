import re
import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(
    page_title="AI Content Assistant",
    page_icon="✍️",
    layout="centered"
)

# Custom Title Header
st.title("✍️ AI Content Assistant")
st.write("Generate highly punchy, ultra-clean social media posts formatted for maximum readability.")

# Form inputs for post constraints
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

# Content Generation Pipeline
if submit_button:
    api_key = st.secrets.get("GroqAPIKey", "")

    if not api_key:
        st.error("Groq API key missing in Streamlit Secrets! Check 'GroqAPIKey' configuration.")
    elif not topic:
        st.error("Please provide a topic for your content.")
    else:
        with st.spinner("Crafting high-impact content..."):
            try:
                client = Groq(api_key=api_key)

                # Fetch active text models from Groq API
                models_data = client.models.list()
                active_models = [m.id for m in models_data.data if hasattr(m, 'id')]
                text_models = [
                    m for m in active_models 
                    if not any(x in m.lower() for x in ["whisper", "guard", "vision"])
                ]

                if not text_models:
                    st.error("No active text models currently available on Groq.")
                else:
                    # Ultra-strict prompt instructing exact structure and readability rules
                    prompt = f"""
                    You are an elite, top-tier social media strategist and copywriting expert.
                    Generate content strictly following the guidelines below.

                    ### OUTPUT FORMAT RULES:
                    Do NOT write internal thoughts, reasoning steps, or <think> tags.
                    Return ONLY two distinct, cleanly separated sections:

                    SECTION 1: METADATA
                    Write exactly:
                    ## 📌 Post Overview
                    - **Platform:** {platform}
                    - **Target Audience:** {target_audience if target_audience else "General Audience"}
                    - **Tone:** {tone}
                    - **Content Style:** {content_type}

                    SECTION 2: POST CONTENT
                    Write exactly:
                    ## ✍️ Post Content

                    [Insert the exact post here using these strict writing rules]:
                    1. HOOK: First line must be a high-converting, single-line hook.
                    2. WHITE SPACE: Keep paragraphs short (maximum 1-2 sentences per line).
                    3. BULLET POINTS: Use short, bold bullet points for key technical details or tips.
                    4. PINPOINT VALUE: Zero fluff, zero generic intro filler phrases. Jump directly into exact facts.
                    5. CTA: Single clear Call-To-Action at the bottom.
                    6. HASHTAGS: Exactly 5-8 hyper-relevant hashtags placed at the very end.

                    ### CONSTRAINTS:
                    - Topic: {topic}
                    - Platform: {platform}
                    """

                    raw_output = None
                    used_model = ""

                    # Query dynamic live models
                    for model_id in text_models:
                        try:
                            response = client.chat.completions.create(
                                model=model_id,
                                messages=[
                                    {"role": "system", "content": "You write clear, ultra-clean, high-converting social media posts."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.6,
                                max_tokens=1200
                            )
                            raw_output = response.choices[0].message.content
                            used_model = model_id
                            break
                        except Exception:
                            continue

                    if raw_output:
                        # Clean out reasoning tags (<think>...</think>)
                        clean_content = re.sub(r'<think>.*?</think>', '', raw_output, flags=re.DOTALL).strip()

                        # Split metadata section and post content section for tabbed UI
                        sections = clean_content.split("## ✍️ Post Content")
                        
                        metadata_part = sections[0].strip() if len(sections) > 1 else "## 📌 Post Overview"
                        post_part = sections[1].strip() if len(sections) > 1 else clean_content

                        st.success(f"Generated via {used_model}")

                        # Streamlit UI Tabs to keep content clean and unmerged
                        tab1, tab2, tab3 = st.tabs(["👁️ Formatted View", "📋 Copy Raw Text", "📊 Details"])

                        with tab1:
                            st.markdown(post_part)

                        with tab2:
                            st.code(post_part, language="markdown")

                        with tab3:
                            st.markdown(metadata_part)
                            st.caption(f"Character Count: {len(post_part)} characters")

                        # Download File Option
                        st.download_button(
                            label="📥 Download Post (.txt)",
                            data=post_part,
                            file_name="social_post.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("Failed to generate response across active models.")

            except Exception as e:
                st.error(f"Error connecting to Groq API: {str(e)}")
