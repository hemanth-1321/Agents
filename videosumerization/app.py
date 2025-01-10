import streamlit as st
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
import google.generativeai as genai

from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API keys
API_KEY = os.getenv("GOOGLE_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

# Page configuration
st.set_page_config(
    page_title="YouTube Video AI Analyzer",
    page_icon="🎥",
    layout="wide"
)

st.title("Phidata YouTube Video AI Summarizer 🎥")
st.header("Powered by Gemini 2.0 Flash Exp")

@st.cache_resource
def initialize_agent():
    return Agent(
        name="YouTube Video AI Analyzer",
        model=Gemini(id="gemini-2.0-flash-exp"),
        tools=[DuckDuckGo()],
        markdown=True,
    )

# Initialize the agent
multimodal_Agent = initialize_agent()

# Input for YouTube URL
youtube_url = st.text_input(
    "Enter YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=example",
    help="Provide a YouTube URL for the video you want to analyze."
)

if youtube_url:
    try:
        # Extract the video ID from the YouTube URL
        video_id = youtube_url.split("v=")[-1].split("&")[0]

        # Use the YouTube Data API to fetch video details
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.videos().list(part="snippet,contentDetails", id=video_id)
        response = request.execute()

        if "items" in response and len(response["items"]) > 0:
            video_data = response["items"][0]["snippet"]
            title = video_data.get("title", "No Title Available")
            description = video_data.get("description", "No Description Available")

            # Display video details
            st.subheader("Video Details")
            st.write(f"**Title:** {title}")
            st.write(f"**Description:** {description}")

            # Input for user query
            user_query = st.text_area(
                "What insights are you seeking from the video?",
                placeholder="Ask anything about the video content. The AI agent will analyze and gather additional context if needed.",
                help="Provide specific questions or insights you want from the video."
            )

            if st.button("🔍 Analyze Video", key="analyze_video_button"):
                if not user_query:
                    st.warning("Please enter a question or insight to analyze the video.")
                else:
                    try:
                        with st.spinner("Analyzing video metadata and gathering insights..."):
                            # Create analysis prompt
                            analysis_prompt = (
                                f"""
                                Analyze the following YouTube video details:
                                - Title: {title}
                                - Description: {description}

                                Respond to the following query using the provided video insights and supplementary web research:
                                {user_query}

                                Provide a detailed, user-friendly, and actionable response.
                                """
                            )

                            # AI agent processing
                            response = multimodal_Agent.run(analysis_prompt)

                        # Display the result
                        st.subheader("Analysis Result")
                        st.markdown(response.content)

                    except Exception as error:
                        st.error(f"An error occurred during analysis: {error}")

        else:
            st.error("Unable to fetch video details. Please check the URL or try another video.")

    except Exception as error:
        st.error(f"An error occurred: {error}")
else:
    st.info("Enter a YouTube video URL to begin analysis.")
