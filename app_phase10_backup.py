import streamlit as st

from agents.local_agent import local_commerce_agent


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Commerce Copilot",
    page_icon="🛍️",
    layout="wide"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🛍️ AI Commerce Copilot'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Your 24/7 AI Employee for Online Businesses'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🤖 AI Commerce Copilot")

    st.write(
        "AI assistant for products, orders, "
        "cancellations and returns."
    )

    st.divider()

    st.subheader("Features")

    st.write("🛍️ Product Search")
    st.write("🛒 Order Placement")
    st.write("📦 Order Tracking")
    st.write("❌ Order Cancellation")
    st.write("↩️ Return Requests")
    st.write("📞 AI Phone Calling")
    st.write("🌐 Telugu + English")
    st.write("🗣️ Natural Voice")

    st.divider()

    st.info(
        "Current Mode: Local Commerce Agent\n\n"
        "Gemini API is not required."
    )

    if st.button("🗑️ Clear Conversation"):

        st.session_state.messages = []
        st.session_state.order_state = {}

        st.rerun()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "order_state" not in st.session_state:

    st.session_state.order_state = {}


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "customer":

        with st.chat_message("user"):

            st.write(message["content"])

    else:

        with st.chat_message("assistant"):

            st.write(message["content"])


# ============================================================
# CUSTOMER INPUT
# ============================================================

customer_message = st.chat_input(
    "Type your message here..."
)


# ============================================================
# PROCESS MESSAGE
# ============================================================

if customer_message:

    # --------------------------------------------------------
    # Display customer message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "customer",
            "content": customer_message
        }
    )


    with st.chat_message("user"):

        st.write(customer_message)


    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "AI Commerce Copilot is thinking..."
        ):

            try:

                response = local_commerce_agent(
                    customer_message,
                    st.session_state.order_state
                )

            except Exception as e:

                response = (
                    "Sorry, I encountered an error.\n\n"
                    f"Error: {str(e)}"
                )


            st.write(response)


    # --------------------------------------------------------
    # Save response
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )