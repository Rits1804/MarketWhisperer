from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
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
 
# Streamlit app to handle input, summarization, and email sending
def main():
    st.title("YT Insights")

    # Input field for transcript
    transcript_input = st.text_area("Enter the transcript here:")

    # Only call the model when the button is pressed
    if st.button("Generate"):
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
            st.error("Please enter a transcript.")

if __name__ == "__main__":
    main()
