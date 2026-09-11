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

# Sidebar - Model selection
st.sidebar.header("⚙️ Model Settings")
selected_model = st.sidebar.selectbox(
    "Preferred Groq Model",
    ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
)

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
    api_key = st.secrets.get("GroqAPIKey", "")

    if not api_key:
        st.error("Groq API key missing in Streamlit Secrets! Please verify 'GroqAPIKey' is configured in your Streamlit Cloud app settings.")
    elif not topic:
        st.error("Please provide a topic for your content.")
    else:
        with st.spinner("Generating your post..."):
            # List of candidate models to try sequentially (Fallback Strategy)
            candidate_models = [selected_model, "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
            # Preserve order while removing duplicate entries
            candidate_models = list(dict.fromkeys(candidate_models))

            client = Groq(api_key=api_key)
            prompt = f"""
            You are an expert social media content creator and copywriter.
            Generate a high-performing post based on these exact constraints:

            - Content Type: {content_type}
            - Platform: {platform}
            - Topic: {topic}
            - Target Audience: {target_audience if target_audience else "General Audience"}
            - Tone: {tone}

            Requirements:
            1. Structure the post perfectly for the selected platform ({platform}).
            2. Include a compelling hook in the first line.
            3. Body content formatted cleanly with line breaks or bullet points where appropriate.
            4. A clear Call-To-Action (CTA).
            5. A dedicated section at the bottom with 5-10 highly relevant hashtags.

            Format output as Markdown.
            """

            generated_content = None
            used_model = ""

            # Attempt API execution across available candidate models
            for model_id in candidate_models:
                try:
                    response = client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {"role": "system", "content": "You are a professional content creation assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    generated_content = response.choices[0].message.content
                    used_model = model_id
                    break  # Success
                except Exception as model_err:
                    if "model_not_found" in str(model_err) or "404" in str(model_err):
                        continue  # Try next fallback model
                    else:
                        st.error(f"API Error: {str(model_err)}")
                        break

            if generated_content:
                st.success(f"Content Generated Successfully using {used_model}!")
                st.markdown("---")
                st.markdown(generated_content)
                st.markdown("---")

                # Post character count metric
                st.caption(f"📊 Character Count: {len(generated_content)} characters")

                # Download button
                st.download_button(
                    label="📥 Download Post (.txt)",
                    data=generated_content,
                    file_name="generated_post.txt",
                    mime="text/plain"
                )
            elif not generated_content:
                st.error("All requested Groq models are currently unreachable. Please verify your API Key or check Groq service status.")
