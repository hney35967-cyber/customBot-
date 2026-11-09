import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from rag import KnowledgeBase

# Load environment variables
load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="CustomBot",
    page_icon="🤖",
    layout="centered"
)


@st.cache_resource
def load_kb():
    """Load the knowledge base once."""
    return KnowledgeBase("data")


kb = load_kb()


def get_client():
    """Create Google Gemini client."""
    api_key = os.getenv("GOOGLE_API_KEY")

    if api_key:
        return genai.Client(api_key=api_key)

    return None


# ---------------------------
# SIDEBAR
# ---------------------------

with st.sidebar:
    st.header("⚙️ CustomBot Settings")

    st.write(
        f"📚 Knowledge Base: **{kb.document_count} document(s)**"
    )

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("👩‍💼 Human Support")

    escalation_email = os.getenv(
        "SUPPORT_EMAIL",
        "support@example.com"
    )

    st.info(escalation_email)


# ---------------------------
# MAIN INTERFACE
# ---------------------------

st.title("🤖 CustomBot")
st.caption("Your AI Customer Support Assistant")

# Create conversation memory
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
prompt = st.chat_input(
    "Ask a question about our products or services..."
)


if prompt:

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)


    # Generate response
    with st.chat_message("assistant"):

        with st.spinner("CustomBot is thinking..."):

            # Search knowledge base
            context = kb.search(
                prompt,
                top_k=4
            )

            # If no relevant information is found
            if not context:

                answer = (
                    "I couldn't find a reliable answer "
                    "in our knowledge base. Please contact "
                    "our human support team for further assistance."
                )

            else:

                client = get_client()

                # Check API key
                if not client:

                    answer = (
                        "⚠️ CustomBot is not connected to Gemini yet. "
                        "Please add your GOOGLE_API_KEY."
                    )

                else:

                    # Get recent conversation history
                    history = st.session_state.messages[-8:-1]

                    history_text = "\n".join(
                        f'{message["role"].title()}: '
                        f'{message["content"]}'
                        for message in history
                    )

                    # Create AI instructions
                    system_prompt = f"""
You are CustomBot, a helpful AI Customer Support Assistant.

Answer customer questions using ONLY the information
provided in the knowledge base.

If the answer is not available in the knowledge base,
say that you do not know and recommend contacting
human support.

Never invent company policies or information.

KNOWLEDGE BASE:
{context}

RECENT CONVERSATION:
{history_text}
"""

                    # Generate Gemini response
                    response = client.models.generate_content(
                        model=os.getenv(
                            "GEMINI_MODEL",
                            "gemini-2.0-flash"
                        ),
                        contents=f"{system_prompt}\n\nUser Question: {prompt}"
                    )

                    answer = response.text


        # Display response
        st.markdown(answer)


    # Save bot response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )
