from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# Load environment variables
load_dotenv()


# Set page configuration
st.set_page_config(
    page_title="YT Insights",       # Title of the page (appears in browser tab)
    page_icon=":guardsman:",             # Icon for the page (can be emoji or file path)
    layout="wide",                       # Layout: "centered" (default) or "wide"
    initial_sidebar_state="expanded"     # Sidebar state: "auto", "expanded", or "collapsed"
)


# CSS to hide the footer and GitHub logo
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)



GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def standardize_youtube_url(url):
    """
    Converts a YouTube URL into the standard desktop format.
    
    Args:
        url (str): The original YouTube URL.
    
    Returns:
        str: The standardized YouTube URL.
    """
    if "youtu.be" in url:  # Mobile YouTube URL
        # Extract the video ID
        video_id = url.split('/')[-1].split('?')[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    elif "youtube.com" in url:  # Already a desktop YouTube URL
        return url
    else:
        raise ValueError("Invalid YouTube URL format")

   
def extract_transcript_details(youtube_video_url):
    """
    Extracts the transcript from a YouTube video.

    Args:
        youtube_video_url (str): The full URL of the YouTube video.

    Returns:
        str or None: The combined transcript text if successful, otherwise None.
    """
    try:
        # Extract the video ID from the YouTube URL
        if "watch?v=" in youtube_video_url:
            video_id = youtube_video_url.split("watch?v=")[1].split("&")[0]
        else:
            raise ValueError("Invalid YouTube URL format. Expected 'watch?v=' in the URL.")
        
        # Fetch the transcript in specified languages
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])
        transcript = " ".join(entry["text"] for entry in transcript_text)
        return transcript

    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        st.error("No transcript available for this video in the specified languages.")
    except VideoUnavailable:
        st.error("The video is unavailable.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

    return None


# Streamlit app to handle input, summarization, and email sending
def main():
    st.title("YT Insights")
    # Input field for transcript
    youtube_url = st.text_input("Enter YouTube Video URL:")
    # Only call the model when the button is pressed
    if st.button("Generate") and youtube_url:
        
        corrected_url=standardize_youtube_url(youtube_url)
        if corrected_url:
            with st.spinner("Almost there! We're gathering the insights..."):
                transcript_input=extract_transcript_details(corrected_url)
                if transcript_input:
                    # Summarize the transcript using ChatGoogleGenerativeAI
                    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.5, GOOGLE_API_KEY=GOOGLE_API_KEY)
                    prompt = """
                    Provide a detailed and comprehensive summary in English of the following content about the stock market, covering all key points without omitting any important information. The summary should be long and include the following elements:

                    Key Points: Highlight the main topics or discussions related to the stock market.
                    Insights: Provide deeper analysis or important takeaways emphasized in the content.
                    Suggestions/Recommendations: Note any advice, strategies, or recommendations regarding stock market investments.
                    Positives: Discuss the positive aspects, trends, or opportunities in the stock market or specific stocks.
                    Negatives: Discuss any negative points, risks, or concerns raised about the stock market or specific stocks.
                    The summary should be thorough, ensuring all major aspects are covered in a clear, informative, and well-rounded manner, without missing any important details. Do not mention that this information is derived from a video or any other source.
                    """
                    
                    # Generate the summary using LLM
                    messages = [("system", prompt), ("human", transcript_input)]
                    
                    ai_msg = llm.invoke(messages)
                    summary = ai_msg.content

                    # Display the summary
                    st.subheader("Insights")
                    st.markdown(summary)

                else:
                    # st.error("Please enter a transcript.")
                    pass
    else:
        st.error("please enter valid url")
if __name__ == "__main__":
    main()
