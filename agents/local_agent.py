import re

from tools.product_tools import search_products
from tools.orders_tools import create_order
from tools.orders_tools import get_order_status
from tools.orders_tools import cancel_order
from tools.return_tools import get_return_status


# ============================================================
# MULTILINGUAL RESPONSE TEMPLATES
# ============================================================

RESPONSE_TEMPLATES = {

    "welcome": {
        "en": (
            "I can help you with:\n\n"
            "🛍️ **Product search**\n"
            "🛒 **Place an order**\n"
            "📦 **Order tracking**\n"
            "❌ **Order cancellation**\n"
            "↩️ **Return requests**\n\n"
            "Try saying:\n\n"
            "• I want a dress\n"
            "• I want to order\n"
            "• Show me dresses\n"
            "• Where is my order ORD001?\n"
            "• Cancel order ORD002"
        ),
        "te": (
            "నేను మీకు ఈ విషయాలలో సహాయం చేయగలను:\n\n"
            "🛍️ **ఉత్పత్తి శోధన**\n"
            "🛒 **ఆర్డర్ చేయండి**\n"
            "📦 **ఆర్డర్ ట్రాకింగ్**\n"
            "❌ **ఆర్డర్ రద్దు**\n"
            "↩️ **రిటర్న్ అభ్యర్థనలు**\n\n"
            "ఇలా చెప్పండి:\n\n"
            "• నాకు డ్రెస్ కావాలి\n"
            "• ఆర్డర్ చేయాలి\n"
            "• నా ఆర్డర్ ORD001 ఎక్కడ ఉంది?\n"
            "• ఆర్డర్ ORD002 రద్దు చేయండి"
        ),
        "hi": (
            "मैं इन विषयों में आपकी मदद कर सकता हूँ:\n\n"
            "🛍️ **उत्पाद खोज**\n"
            "🛒 **ऑर्डर करें**\n"
            "📦 **ऑर्डर ट्रैकिंग**\n"
            "❌ **ऑर्डर रद्द**\n"
            "↩️ **रिटर्न अनुरोध**\n\n"
            "कुछ ऐसा कहें:\n\n"
            "• मुझे ड्रेस चाहिए\n"
            "• ऑर्डर करना है\n"
            "• मेरा ऑर्डर ORD001 कहाँ है?\n"
            "• ऑर्डर ORD002 रद्द करें"
        ),
    },

    "order_start": {
        "en": (
            "Sure! 🛒 Let's place your order.\n\n"
            "What product would you like to order?\n\n"
            "For example:\n\n"
            "- I want a dress\n"
            "- Show me dresses\n"
            "- I want a black dress under ₹2000"
        ),
        "te": (
            "తప్పకుండా! 🛒 మీ ఆర్డర్ చేద్దాం.\n\n"
            "మీకు ఏ ఉత్పత్తి కావాలి?\n\n"
            "ఉదాహరణ:\n\n"
            "- నాకు డ్రెస్ కావాలి\n"
            "- డ్రెస్‌లు చూపించండి\n"
            "- ₹2000 లోపు నల్ల డ్రెస్ కావాలి"
        ),
        "hi": (
            "ज़रूर! 🛒 आपका ऑर्डर करते हैं.\n\n"
            "आपको कौन सा उत्पाद चाहिए?\n\n"
            "उदाहरण:\n\n"
            "- मुझे ड्रेस चाहिए\n"
            "- ड्रेस दिखाइए\n"
            "- ₹2000 से कम काली ड्रेस चाहिए"
        ),
    },

    "provide_order_id": {
        "en": "Please provide your Order ID.\n\nExample: ORD001",
        "te": "దయచేసి మీ ఆర్డర్ ID అందించండి.\n\nఉదాహరణ: ORD001",
        "hi": "कृपया अपना ऑर्डर ID दें.\n\nउदाहरण: ORD001",
    },

    "provide_return_id": {
        "en": "Please provide your Return ID.\n\nExample:\nRET20260809132757",
        "te": "దయచేసి మీ రిటర్న్ ID అందించండి.\n\nఉదాహరణ:\nRET20260809132757",
        "hi": "कृपया अपना रिटर्न ID दें.\n\nउदाहरण:\nRET20260809132757",
    },

    "provide_customer_id": {
        "en": (
            "Great! 🛒 Your order is ready.\n\n"
            "Please provide your Customer ID "
            "to complete the order.\n\n"
            "Example: C001"
        ),
        "te": (
            "బాగుంది! 🛒 మీ ఆర్డర్ సిద్ధంగా ఉంది.\n\n"
            "ఆర్డర్ పూర్తి చేయడానికి దయచేసి మీ "
            "కస్టమర్ ID అందించండి.\n\n"
            "ఉదాహరణ: C001"
        ),
        "hi": (
            "बढ़िया! 🛒 आपका ऑर्डर तैयार है.\n\n"
            "ऑर्डर पूरा करने के लिए कृपया अपना "
            "कस्टमर ID दें.\n\n"
            "उदाहरण: C001"
        ),
    },

    "confirm_order": {
        "en": "Would you like to place this order?\n\nPlease answer **Yes** or **No**.",
        "te": "మీరు ఈ ఆర్డర్ చేయాలనుకుంటున్నారా?\n\nదయచేసి **అవును** లేదా **కాదు** అని చెప్పండి.",
        "hi": "क्या आप यह ऑर्डर करना चाहते हैं?\n\nकृपया **हाँ** या **नहीं** कहें.",
    },

    "order_cancelled_by_user": {
        "en": (
            "No problem. Your order was cancelled.\n\n"
            "You can start a new order whenever you want."
        ),
        "te": (
            "ఫర్వాలేదు. మీ ఆర్డర్ రద్దు చేయబడింది.\n\n"
            "మీరు ఎప్పుడైనా కొత్త ఆర్డర్ చేయవచ్చు."
        ),
        "hi": (
            "कोई बात नहीं. आपका ऑर्डर रद्द कर दिया गया.\n\n"
            "आप कभी भी नया ऑर्डर कर सकते हैं."
        ),
    },

    "no_products_found": {
        "en": "Sorry, I couldn't find any products matching your request.",
        "te": "క్షమించండి, మీ అభ్యర్థనకు సరిపోయే ఉత్పత్తులు కనుగొనలేకపోయాను.",
        "hi": "क्षमा करें, आपके अनुरोध से मेल खाने वाले उत्पाद नहीं मिले.",
    },

    "select_product_number": {
        "en": "\nPlease enter the number of the product you want to order.",
        "te": "\nదయచేసి మీకు కావలసిన ఉత్పత్తి సంఖ్యను ఎంచుకోండి.",
        "hi": "\nकृपया अपनी पसंद के उत्पाद का नंबर दर्ज करें.",
    },

    "how_many": {
        "en": "How many would you like to order?",
        "te": "మీరు ఎన్ని ఆర్డర్ చేయాలనుకుంటున్నారు?",
        "hi": "आप कितने ऑर्डर करना चाहेंगे?",
    },

    "enter_quantity": {
        "en": "Please enter the quantity as a number.\n\nExample: 1 or 2",
        "te": "దయచేసి సంఖ్యలో పరిమాణం నమోదు చేయండి.\n\nఉదాహరణ: 1 లేదా 2",
        "hi": "कृपया संख्या में मात्रा दर्ज करें.\n\nउदाहरण: 1 या 2",
    },

    "quantity_at_least_one": {
        "en": "Quantity must be at least 1.",
        "te": "పరిమాణం కనీసం 1 ఉండాలి.",
        "hi": "मात्रा कम से कम 1 होनी चाहिए.",
    },

    "confirm_yes_no": {
        "en": "Please confirm the order by answering **Yes** or **No**.",
        "te": "దయచేసి **అవును** లేదా **కాదు** అని చెప్పి ఆర్డర్ నిర్ధారించండి.",
        "hi": "कृपया **हाँ** या **नहीं** कहकर ऑर्डर की पुष्टि करें.",
    },

    "invalid_customer_id": {
        "en": "Please provide a valid Customer ID.\n\nExample: C001",
        "te": "దయచేసి చెల్లుబాటు అయ్యే కస్టమర్ ID అందించండి.\n\nఉదాహరణ: C001",
        "hi": "कृपया एक वैध कस्टमर ID दें.\n\nउदाहरण: C001",
    },

    "order_info_lost": {
        "en": "The order information was lost.\n\nPlease start the order again.",
        "te": "ఆర్డర్ సమాచారం కోల్పోయింది.\n\nదయచేసి మళ్ళీ ఆర్డర్ చేయండి.",
        "hi": "ऑर्डर की जानकारी खो गई.\n\nकृपया फिर से ऑर्डर करें.",
    },

    "product_list_lost": {
        "en": (
            "I lost the previous product list. "
            "Let's search again.\n\n"
            "What product would you like to order?\n\n"
            "Example:\n"
            "• I want a dress\n"
            "• I want black shoes"
        ),
        "te": (
            "గత ఉత్పత్తి జాబితా కోల్పోయింది. "
            "మళ్ళీ శోధిద్దాం.\n\n"
            "మీకు ఏ ఉత్పత్తి కావాలి?\n\n"
            "ఉదాహరణ:\n"
            "• నాకు డ్రెస్ కావాలి\n"
            "• నాకు నల్ల షూస్ కావాలి"
        ),
        "hi": (
            "पिछली उत्पाद सूची खो गई. "
            "फिर से खोजते हैं.\n\n"
            "आपको कौन सा उत्पाद चाहिए?\n\n"
            "उदाहरण:\n"
            "• मुझे ड्रेस चाहिए\n"
            "• मुझे काले जूते चाहिए"
        ),
    },
}


# ============================================================
# MULTILINGUAL KEYWORD SETS
# ============================================================

# Yes/confirmation words per language
YES_WORDS = {
    "en": ["yes", "y", "yeah", "yep", "confirm",
           "confirmed", "place order"],
    "te": ["అవును", "ఔను", "సరే", "ఒప్పుకుంటాను",
           "ఆర్డర్ చేయండి", "yes"],
    "hi": ["हाँ", "हां", "जी", "जी हाँ", "ठीक है",
           "ऑर्डर करो", "yes"],
}

# No/rejection words per language
NO_WORDS = {
    "en": ["no", "n", "cancel", "don't", "dont"],
    "te": ["కాదు", "వద్దు", "రద్దు", "no"],
    "hi": ["नहीं", "ना", "रद्द", "मत करो", "no"],
}

# Order tracking keywords per language
TRACK_KEYWORDS = {
    "en": ["where is my order", "order status",
           "track my order", "status of my order"],
    "te": ["నా ఆర్డర్ ఎక్కడ", "ఆర్డర్ స్థితి",
           "ఆర్డర్ ట్రాక్", "ఆర్డర్ ఎక్కడ ఉంది"],
    "hi": ["मेरा ऑर्डर कहाँ", "ऑर्डर स्टेटस",
           "ऑर्डर ट्रैक", "ऑर्डर कहाँ है"],
}

# Cancel keywords per language
CANCEL_KEYWORDS = {
    "en": ["cancel order", "cancel my order"],
    "te": ["ఆర్డర్ రద్దు", "రద్దు చేయండి",
           "ఆర్డర్ కేన్సల్"],
    "hi": ["ऑर्डर रद्द", "ऑर्डर कैंसिल",
           "रद्द करो", "कैंसल करो"],
}

# Return status keywords per language
RETURN_KEYWORDS = {
    "en": ["return"],
    "te": ["రిటర్న్", "వాపస్"],
    "hi": ["रिटर्न", "वापसी"],
}

RETURN_STATUS_KEYWORDS = {
    "en": ["status", "where"],
    "te": ["స్థితి", "ఎక్కడ"],
    "hi": ["स्टेटस", "कहाँ", "स्थिति"],
}

# Order start keywords per language
ORDER_START_KEYWORDS = {
    "en": ["i want to order", "place an order",
           "buy something"],
    "te": ["ఆర్డర్ చేయాలి", "కొనాలి",
           "ఆర్డర్ పెట్టాలి"],
    "hi": ["ऑर्डर करना है", "ऑर्डर करना चाहता",
           "खरीदना है", "ऑर्डर दो"],
}

# Product keywords (same across languages since
# product names are in English in the database)
PRODUCT_KEYWORDS = [
    "dress", "shirt", "shoes", "jeans",
    "tshirt", "t-shirt", "phone", "laptop",
    "డ్రెస్", "షర్ట్", "షూస్", "జీన్స్",
    "ड्रेस", "शर्ट", "जूते", "जींस",
    "saree", "సారీ", "साड़ी",
    "kurti", "కుర్తీ", "कुर्ती",
    "necklace", "నెక్లెస్", "नेकलेस",
    "handbag", "హ్యాండ్‌బ్యాగ్", "हैंडबैग",
    "jewelry", "జ్యువెలరీ", "ज्वेलरी",
]

# Map non-English product words to English categories
PRODUCT_WORD_MAP = {
    "డ్రెస్": "dress", "ड्रेस": "dress",
    "షర్ట్": "shirt", "शर्ट": "shirt",
    "షూస్": "shoes", "जूते": "shoes",
    "జీన్స్": "jeans", "जींस": "jeans",
    "సారీ": "saree", "साड़ी": "saree",
    "కుర్తీ": "kurti", "कुर्ती": "kurti",
    "నెక్లెస్": "necklace", "नेकलेस": "necklace",
    "హ్యాండ్‌బ్యాగ్": "handbag", "हैंडबैग": "handbag",
    "జ్యువెలరీ": "jewelry", "ज्वेलरी": "jewelry",
}


# ============================================================
# TRANSLATE HELPER
# ============================================================

def get_template(key, language="en"):
    """
    Get a response template in the given language.
    Falls back to English if the language is not found.
    """

    templates = RESPONSE_TEMPLATES.get(key, {})

    return templates.get(
        language,
        templates.get("en", "")
    )


def normalize_product_message(message):
    """
    Replace non-English product keywords with their
    English equivalents so existing product search
    logic works unchanged.
    """

    normalized = message.lower()

    for native_word, english_word in PRODUCT_WORD_MAP.items():

        if native_word in message:
            normalized = normalized.replace(
                native_word.lower(),
                english_word,
            )

    return normalized


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def extract_order_id(message):
    match = re.search(r"\bORD\d+\b", message.upper())

    if match:
        return match.group(0)

    return None


def extract_return_id(message):
    match = re.search(r"\bRET\d+\b", message.upper())

    if match:
        return match.group(0)

    return None


def extract_customer_id(message):
    match = re.search(r"\bC\d+\b", message.upper())

    if match:
        return match.group(0)

    return None


def is_yes(message, language="en"):
    words = YES_WORDS.get(language, YES_WORDS["en"])
    # Also check English words as fallback
    all_words = list(set(words + YES_WORDS["en"]))
    return message.strip().lower() in all_words


def is_no(message, language="en"):
    words = NO_WORDS.get(language, NO_WORDS["en"])
    # Also check English words as fallback
    all_words = list(set(words + NO_WORDS["en"]))
    return message.strip().lower() in all_words


def matches_keywords(text, keyword_dict, language="en"):
    """
    Check if text matches any keyword in the given
    language. Also checks English keywords as fallback.
    """

    lower_text = text.lower()

    # Check selected language
    for keyword in keyword_dict.get(language, []):
        if keyword in lower_text:
            return True

    # Always also check English
    if language != "en":
        for keyword in keyword_dict.get("en", []):
            if keyword in lower_text:
                return True

    return False


# ============================================================
# PRODUCT SEARCH
# ============================================================

def handle_product_search(message):

    text = message.lower()

    category = None
    color = None
    max_price = None

    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

    categories = [
        "dress",
        "shirt",
        "shoes",
        "jeans",
        "tshirt",
        "t-shirt",
        "phone",
        "laptop"
    ]

    for item in categories:

        if item in text:

            if item in ["tshirt", "t-shirt"]:
                category = "T-Shirt"

            elif item == "phone":
                category = "Phone"

            elif item == "laptop":
                category = "Laptop"

            else:
                category = item.capitalize()

            break

    # --------------------------------------------------------
    # COLOR
    # --------------------------------------------------------

    colors = [
        "black",
        "blue",
        "red",
        "green",
        "white",
        "yellow"
    ]

    for item in colors:

        if item in text:
            color = item.capitalize()
            break

    # --------------------------------------------------------
    # PRICE
    # --------------------------------------------------------

    price_match = re.search(
        r"(?:under|below|less than|maximum|max)\s*[₹rs.]?\s*(\d+)",
        text
    )

    if price_match:

        max_price = float(
            price_match.group(1)
        )

    # --------------------------------------------------------
    # DATABASE SEARCH
    # --------------------------------------------------------

    results = search_products(
        category=category,
        color=color,
        max_price=max_price
    )

    if not results:

        return (
            "Sorry, I couldn't find any products "
            "matching your request."
        )

    response = (
        f"I found {len(results)} "
        f"products matching your request:\n\n"
    )

    for index, product in enumerate(
        results,
        start=1
    ):

        response += (
            f"{index}. **{product['name']}**\n"
            f"   Price: ₹{product['price']}\n"
            f"   Color: {product['color']}\n"
            f"   Size: {product['size']}\n"
            f"   Stock: {product['stock']}\n"
            f"   Rating: {product['rating']}/5\n\n"
        )

    return response, results


# ============================================================
# LOCAL COMMERCE AGENT
# ============================================================

def local_commerce_agent(
    user_message,
    state,
    language="en",
):

    message = user_message.strip()
    lower_message = message.lower()

    # Normalize non-English product words
    normalized_message = normalize_product_message(
        message
    )
    lower_normalized = normalized_message.lower()

    print("\n====================================")
    try:
        print("DEBUG MESSAGE:", message)
    except UnicodeEncodeError:
        print("DEBUG MESSAGE:", message.encode('utf-8', 'replace'))
        
    print("DEBUG STATE BEFORE:", state)
    print("====================================")


    # ========================================================
    # 1. WAITING FOR PRODUCT SELECTION
    # ========================================================

    if state.get("step") == "WAITING_FOR_PRODUCT":

        products = state.get(
            "products",
            []
        )

        # ----------------------------------------------------
        # CUSTOMER ENTERED A NUMBER
        # ----------------------------------------------------

        if message.isdigit():

            selected_number = int(message)

            # ------------------------------------------------
            # IMPORTANT FIX
            # ------------------------------------------------

            if len(products) == 0:

                print(
                    "DEBUG: Product list is empty."
                )

                state.clear()

                return get_template(
                    "product_list_lost", language
                )

            # ------------------------------------------------
            # INVALID NUMBER
            # ------------------------------------------------

            if (
                selected_number < 1
                or selected_number > len(products)
            ):

                return (
                    f"Please enter a number between "
                    f"1 and {len(products)}."
                )

            # ------------------------------------------------
            # SELECT PRODUCT
            # ------------------------------------------------

            selected_product = products[
                selected_number - 1
            ]

            state["selected_product"] = (
                selected_product
            )

            state["step"] = (
                "WAITING_FOR_QUANTITY"
            )

            print(
                "DEBUG SELECTED PRODUCT:",
                selected_product
            )

            print(
                "DEBUG STATE AFTER:",
                state
            )

            return (
                f"You selected "
                f"**{selected_product['name']}**.\n\n"
                f"Price: ₹{selected_product['price']}\n"
                f"Color: {selected_product['color']}\n"
                f"Size: {selected_product['size']}\n"
                f"Stock: {selected_product['stock']}\n"
                f"Rating: {selected_product['rating']}/5\n\n"
                + get_template("how_many", language)
            )

        # ----------------------------------------------------
        # CUSTOMER ENTERED PRODUCT REQUEST
        # ----------------------------------------------------

        result = handle_product_search(
            normalized_message
        )

        if isinstance(result, str):

            return result

        response, products = result

        # ----------------------------------------------------
        # SAVE PRODUCT LIST
        # ----------------------------------------------------

        state["products"] = products

        state["step"] = (
            "WAITING_FOR_PRODUCT"
        )

        print(
            "DEBUG PRODUCTS SAVED:",
            products
        )

        print(
            "DEBUG STATE AFTER SEARCH:",
            state
        )

        return (
            response
            + get_template(
                "select_product_number", language
            )
        )


    # ========================================================
    # 2. WAITING FOR QUANTITY
    # ========================================================

    if state.get("step") == "WAITING_FOR_QUANTITY":

        selected_product = state.get(
            "selected_product"
        )

        if not selected_product:

            state.clear()

            return (
                "Something went wrong with the "
                "product selection.\n\n"
                "Please start the order again."
            )

        # ----------------------------------------------------
        # QUANTITY MUST BE NUMBER
        # ----------------------------------------------------

        if not message.isdigit():

            return get_template(
                "enter_quantity", language
            )

        quantity = int(message)

        # ----------------------------------------------------
        # QUANTITY VALIDATION
        # ----------------------------------------------------

        if quantity <= 0:

            return get_template(
                "quantity_at_least_one", language
            )

        stock = int(
            selected_product["stock"]
        )

        if quantity > stock:

            return (
                f"Sorry, only {stock} units "
                f"are available."
            )

        # ----------------------------------------------------
        # CALCULATE TOTAL
        # ----------------------------------------------------

        price = float(
            selected_product["price"]
        )

        total = price * quantity

        # ----------------------------------------------------
        # SAVE STATE
        # ----------------------------------------------------

        state["quantity"] = quantity

        state["total"] = total

        state["step"] = (
            "WAITING_FOR_CONFIRMATION"
        )

        print(
            "DEBUG QUANTITY:",
            quantity
        )

        print(
            "DEBUG TOTAL:",
            total
        )

        print(
            "DEBUG STATE AFTER:",
            state
        )

        return (
            "Please confirm your order:\n\n"
            f"**Product:** "
            f"{selected_product['name']}\n"
            f"**Quantity:** {quantity}\n"
            f"**Price per item:** ₹{price}\n"
            f"**Total:** ₹{total}\n\n"
            + get_template("confirm_order", language)
        )


    # ========================================================
    # 3. WAITING FOR CONFIRMATION
    # ========================================================

    if state.get("step") == "WAITING_FOR_CONFIRMATION":

        # ----------------------------------------------------
        # NO
        # ----------------------------------------------------

        if is_no(message, language):

            state.clear()

            return get_template(
                "order_cancelled_by_user", language
            )

        # ----------------------------------------------------
        # YES
        # ----------------------------------------------------

        if is_yes(message, language):

            state["step"] = (
                "WAITING_FOR_CUSTOMER_ID"
            )

            print(
                "DEBUG STATE AFTER:",
                state
            )

            return get_template(
                "provide_customer_id", language
            )

        return get_template(
            "confirm_yes_no", language
        )


    # ========================================================
    # 4. WAITING FOR CUSTOMER ID
    # ========================================================

    if state.get("step") == "WAITING_FOR_CUSTOMER_ID":

        customer_id = extract_customer_id(
            message
        )

        if not customer_id:

            return get_template(
                "invalid_customer_id", language
            )

        selected_product = state.get(
            "selected_product"
        )

        quantity = state.get(
            "quantity"
        )

        if not selected_product or not quantity:

            state.clear()

            return get_template(
                "order_info_lost", language
            )

        # ----------------------------------------------------
        # CREATE ORDER
        # ----------------------------------------------------

        try:

            result = create_order(
                customer_id,
                selected_product["product_id"],
                quantity
            )

        except Exception as e:

            print(
                "DEBUG CREATE ORDER ERROR:",
                e
            )

            return (
                "Sorry, I couldn't create the order.\n\n"
                f"Error: {str(e)}"
            )

        print(
            "DEBUG ORDER RESULT:",
            result
        )

        # ----------------------------------------------------
        # ORDER FAILED
        # ----------------------------------------------------

        if not result.get("success"):

            return (
                "Sorry, I couldn't place the order.\n\n"
                f"{result.get('message', 'Unknown error')}"
            )

        # ----------------------------------------------------
        # ORDER SUCCESS
        # ----------------------------------------------------

        order_id = result.get(
            "order_id"
        )

        total = result.get(
            "amount",
            state.get("total")
        )

        product_name = selected_product[
            "name"
        ]

        # Clear order state
        state.clear()

        return (
            "🎉 **Order placed successfully!**\n\n"
            f"**Order ID:** {order_id}\n"
            f"**Customer ID:** {customer_id}\n"
            f"**Product:** {product_name}\n"
            f"**Quantity:** {quantity}\n"
            f"**Total:** ₹{total}\n\n"
            "Thank you for shopping with us! 🛒"
        )


    # ========================================================
    # 5. START ORDER
    # ========================================================

    if (
        matches_keywords(
            message, ORDER_START_KEYWORDS, language
        )
        or lower_message == "order"
        or lower_message == "ఆర్డర్"
        or lower_message == "ऑर्डर"
    ):

        state.clear()

        state["step"] = (
            "WAITING_FOR_PRODUCT"
        )

        print(
            "DEBUG ORDER START STATE:",
            state
        )

        return get_template(
            "order_start", language
        )


    # ========================================================
    # 6. PRODUCT SEARCH
    # ========================================================

    contains_product_request = any(
        keyword in lower_normalized
        for keyword in PRODUCT_KEYWORDS
    )

    if contains_product_request:

        result = handle_product_search(
            normalized_message
        )

        if isinstance(result, str):

            return result

        response, products = result

        # ----------------------------------------------------
        # SAVE PRODUCTS
        # ----------------------------------------------------

        state["products"] = products

        # IMPORTANT:
        # If customer is simply searching products,
        # we still allow product selection.
        state["step"] = (
            "WAITING_FOR_PRODUCT"
        )

        print(
            "DEBUG PRODUCT SEARCH RESULT:",
            products
        )

        print(
            "DEBUG STATE AFTER PRODUCT SEARCH:",
            state
        )

        return (
            response
            + get_template(
                "select_product_number", language
            )
        )


    # ========================================================
    # 7. ORDER TRACKING
    # ========================================================

    if matches_keywords(
        message, TRACK_KEYWORDS, language
    ):

        order_id = extract_order_id(
            message
        )

        if not order_id:

            return get_template(
                "provide_order_id", language
            )

        result = get_order_status(
            order_id
        )

        print(
            "DEBUG ORDER STATUS:",
            result
        )

        if not result.get("success"):

            return result.get(
                "message",
                "Order not found."
            )

        return (
            f"Your order **{result['order_id']}** "
            f"for **{result['product']}** is currently "
            f"**{result['status']}**.\n\n"
            f"- Quantity: {result['quantity']}\n"
            f"- Amount: ₹{result['amount']}\n"
            f"- Order Date: {result['created_at']}"
        )


    # ========================================================
    # 8. CANCEL ORDER
    # ========================================================

    if matches_keywords(
        message, CANCEL_KEYWORDS, language
    ):

        order_id = extract_order_id(
            message
        )

        if not order_id:

            return get_template(
                "provide_order_id", language
            )

        try:

            result = cancel_order(
                order_id
            )

        except Exception as e:

            return (
                f"Unable to cancel the order: {str(e)}"
            )

        print(
            "DEBUG CANCEL RESULT:",
            result
        )

        if not result.get("success"):

            return result.get(
                "message",
                "Order cannot be cancelled."
            )

        return (
            f"Order **{order_id}** has been "
            f"cancelled successfully."
        )


    # ========================================================
    # 9. RETURN STATUS
    # ========================================================

    if (
        matches_keywords(
            message,
            RETURN_KEYWORDS,
            language,
        )
        and matches_keywords(
            message,
            RETURN_STATUS_KEYWORDS,
            language,
        )
    ):

        return_id = extract_return_id(
            message
        )

        if return_id:

            result = get_return_status(
                return_id
            )

        else:

            return get_template(
                "provide_return_id", language
            )

        print(
            "DEBUG RETURN RESULT:",
            result
        )

        if not result.get("success"):

            return result.get(
                "message",
                "Return request not found."
            )

        return (
            f"Your return request for order "
            f"**{result['order_id']}** is currently "
            f"**{result['status']}**.\n\n"
            f"- Return ID: {result['return_id']}\n"
            f"- Reason: {result['reason']}"
        )


    # ========================================================
    # 10. GENERAL HELP
    # ========================================================

    return get_template("welcome", language)