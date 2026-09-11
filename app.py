import re
import streamlit as st
from groq import Groq

# Page configuration
st.set_page_config(
    page_title="AI Content Assistant",
    page_icon="✍️",
    layout="centered"
)

# Custom title and header
st.title("✍️ AI Content Assistant")
st.write("Generate optimized social media posts, captions, and hashtags in seconds.")

# Main form for user selections
with st.form("content_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        content_type = st.selectbox(
            "Content Type",
            ["Social Media Post", "Educational Thread", "Promotional / Ad Copy", "Product Launch", "Newsletter / Short Article"]
        )
        
        platform = st.selectbox(
            "Target Platform",
            ["LinkedIn", "Instagram", "Twitter / X", "Facebook", "YouTube Shorts / Reels Script"]
        )
        
        tone = st.selectbox(
            "Tone of Voice",
            ["Professional & Authoritative", "Casual & Friendly", "Engaging & Conversational", "Witty & Humorous", "Persuasive & High-Energy"]
        )

    with col2:
        topic = st.text_input(
            "Topic / Main Idea",
            placeholder="e.g. 5 tips for learning Python in 2026"
        )
        
        target_audience = st.text_input(
            "Target Audience",
            placeholder="e.g. Beginner developers, college students"
        )

    submit_button = st.form_submit_button("✨ Generate Content")

# Logic to handle content generation
if submit_button:
    # Fetch API Key from Streamlit Secrets
    api_key = st.secrets.get("GROQ_API_KEY", "")

    if not api_key:
        st.error("Groq API key missing in Streamlit Secrets! Please verify 'GroqAPIKey' is configured in app settings.")
    elif not topic:
        st.error("Please provide a topic for your content.")
    else:
        with st.spinner("Connecting to Groq API and generating content..."):
            try:
                client = Groq(api_key=api_key)

                # Fetch active models dynamically
                models_data = client.models.list()
                active_models = [m.id for m in models_data.data if hasattr(m, 'id')]

                # Exclude whisper/audio or vision-only models
                text_models = [
                    m for m in active_models 
                    if not any(x in m.lower() for x in ["whisper", "guard", "vision"])
                ]

                if not text_models:
                    st.error("No active text completion models found on Groq.")
                else:
                    # Construct strict prompt ensuring separated details and post content
                    prompt = f"""
                    You are an expert social media content creator and copywriter.
                    Generate content strictly following this exact output format without writing any internal thoughts, reasoning steps, or <think> tags.

                    ### Output Structure Requirements:
                    1. First section MUST be titled: ## 📌 Post Details & Metadata
                       List the Platform, Content Type, Topic, Target Audience, and Tone in clean bullet points.
                    
                    2. Second section MUST be titled: ## ✍️ Generated Social Media Post
                       Write the full post here. 
                       - Must have an engaging hook on the first line.
                       - Clean body structure with clear spacing and bullet points.
                       - Include a Call-To-Action (CTA).
                       - End with a dedicated hashtag line (5-10 relevant hashtags).

                    Constraints:
                    - Content Type: {content_type}
                    - Platform: {platform}
                    - Topic: {topic}
                    - Target Audience: {target_audience if target_audience else "General Audience"}
                    - Tone: {tone}
                    """

                    raw_content = None
                    used_model = ""

                    # Loop through available text models
                    for model_id in text_models:
                        try:
                            response = client.chat.completions.create(
                                model=model_id,
                                messages=[
                                    {"role": "system", "content": "You are a professional content creation assistant."},
                                    {"role": "user", "content": prompt}
                                ],
                                temperature=0.7,
                                max_tokens=1200
                            )
                            raw_content = response.choices[0].message.content
                            used_model = model_id
                            break
                        except Exception:
                            continue

                    if raw_content:
                        # Clean out any leftover <think>...</think> tags if reasoning models were used
                        clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()

                        st.success(f"Content Generated Successfully using {used_model}!")
                        st.markdown("---")
                        
                        # Render cleaned output directly as formatted Markdown
                        st.markdown(clean_content)
                        
                        st.markdown("---")
                        st.caption(f"📊 Total Output Character Count: {len(clean_content)} characters")

                        # Download button
                        st.download_button(
                            label="📥 Download Post (.txt)",
                            data=clean_content,
                            file_name="generated_post.txt",
                            mime="text/plain"
                        )
                    else:
                        st.error("Failed to generate content with available active Groq models.")

            except Exception as e:
                st.error(f"Groq API Connection Error: {str(e)}")
