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
    # Fetch API Key from Streamlit Secrets using 'GroqAPIKey'
    api_key = st.secrets.get("GroqAPIKey", "")

    if not api_key:
        st.error("Groq API key missing in Streamlit Secrets! Please verify 'GroqAPIKey' is configured in app settings.")
    elif not topic:
        st.error("Please provide a topic for your content.")
    else:
        with st.spinner("Generating your post..."):
            try:
                # Initialize Groq client with key from secrets
                client = Groq(api_key=api_key)

                # Construct prompt for Groq model
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

                # Request completion from Groq API
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": "You are a professional content creation assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )

                generated_content = response.choices[0].message.content

                # Output generated content
                st.success("Content Generated Successfully!")
                st.markdown("---")
                st.markdown(generated_content)
                st.markdown("---")

                # Copy/Download convenience
                st.download_button(
                    label="📥 Download Post (.txt)",
                    data=generated_content,
                    file_name="generated_post.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
