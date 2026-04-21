"""CoolNest agent configs, system prompts, and Gemini tool declarations."""
from google.genai import types

# ── Agent registry ──────────────────────────────────────────────────────────

AGENTS = {
    "cora": {
        "id": "cora", "name": "Cora", "role": "specialist",
        "title": "Kitchen & Home Specialist",
        "specialty_text": "Kitchen Hobs · Vacuums · Small Appliances · Microwaves",
        "voice": "Aoede",
        "avatar": "avatars/cora.png",
        "color": "#D4763B",
        "categories": ["kitchen_hobs", "vacuum_cleaners", "small_appliances", "microwaves", "dishwashers"],
        "can_escalate_to": ["jessica"],
        "greeting": "Hi {name}! I'm Cora, your kitchen and home specialist. How can I help make your home a little better today?",
    },
    "frosty": {
        "id": "frosty", "name": "Frosty", "role": "specialist",
        "title": "Refrigeration & Laundry Specialist",
        "specialty_text": "Refrigerators · Washing Machines",
        "voice": "Charon",
        "avatar": "avatars/frosty.png",
        "color": "#2E86AB",
        "categories": ["refrigerators", "washing_machines"],
        "can_escalate_to": ["marcus"],
        "greeting": "Hi {name}, I'm Frosty! I know everything about fridges and washing machines. What are you looking for today?",
    },
    "breeze": {
        "id": "breeze", "name": "Breeze", "role": "specialist",
        "title": "Climate & Laundry Care Specialist",
        "specialty_text": "Air Conditioners · Fans · Dryers",
        "voice": "Zephyr",
        "avatar": "avatars/breeze.png",
        "color": "#44BBA4",
        "categories": ["air_conditioners", "fans", "dryers"],
        "can_escalate_to": ["marcus"],
        "greeting": "Hey {name}! I'm Breeze — your expert for ACs, fans and dryers. Let's keep you cool and comfortable!",
    },
    "pixel": {
        "id": "pixel", "name": "Pixel", "role": "specialist",
        "title": "Displays & Entertainment Specialist",
        "specialty_text": "OLED · QLED · 4K TVs",
        "voice": "Fenrir",
        "avatar": "avatars/pixel.png",
        "color": "#7209B7",
        "categories": ["tvs"],
        "can_escalate_to": ["jessica"],
        "greeting": "What's up {name}! I'm Pixel — the TV and display nerd. Ready to find your perfect screen?",
    },
    "marcus": {
        "id": "marcus", "name": "Marcus", "role": "supervisor",
        "title": "Climate & Care Supervisor",
        "specialty_text": "Supervises: Frosty · Breeze",
        "voice": "Fenrir",
        "avatar": "avatars/marcus.png",
        "color": "#3A405A",
        "categories": ["refrigerators", "washing_machines", "air_conditioners", "fans", "dryers"],
        "can_escalate_to": ["alexandra"],
        "greeting": "Hello {name}, I'm Marcus, Climate & Care Supervisor. I'm here to help with anything Frosty or Breeze couldn't resolve. What's the situation?",
    },
    "jessica": {
        "id": "jessica", "name": "Jessica", "role": "supervisor",
        "title": "Home & Vision Supervisor",
        "specialty_text": "Supervises: Cora · Pixel",
        "voice": "Kore",
        "avatar": "avatars/jessica.png",
        "color": "#E84855",
        "categories": ["tvs", "kitchen_hobs", "vacuum_cleaners", "small_appliances", "microwaves", "dishwashers"],
        "can_escalate_to": ["alexandra"],
        "greeting": "Hi {name}! Jessica here — Home & Vision Supervisor. Let me see how I can sort this out for you.",
    },
    "alexandra": {
        "id": "alexandra", "name": "Alexandra", "role": "manager",
        "title": "General Manager",
        "specialty_text": "Discounts · Returns · Escalations",
        "voice": "Aoede",
        "avatar": "avatars/alexandra.png",
        "color": "#0D5C6E",
        "categories": [],  # handles all
        "can_escalate_to": [],
        "greeting": "Hello {name}, I'm Alexandra, General Manager of CoolNest. I've been briefed on your case. Let me personally make sure we get this resolved to your complete satisfaction.",
    },
}


def build_system_prompt(agent: dict, user: dict, context: dict) -> str:
    """Build the full system prompt for a Gemini Live session."""
    tier_label = {"platinum": "Platinum ★★★", "gold": "Gold ★★", "silver": "Silver ★", "bronze": "Bronze"}.get(user.get("loyalty_tier", "bronze"), "Bronze")
    user_name = user.get("name", "there")
    prior = context.get("session_summary", "")
    orders = context.get("recent_orders", "None on file")

    role = agent["role"]
    agent_name = agent["name"]

    # ── Shared rules ────────────────────────────────────────────────────────
    shared = f"""
You are {agent_name}, {agent['title']} at CoolNest — "Smart Appliances, Smarter Prices."

CoolNest is a premium-yet-affordable household appliances brand. Products are high quality, well-priced, and come with strong warranties.

CURRENT CUSTOMER:
- Name: {user_name}
- Loyalty Tier: {tier_label}
- Recent orders: {orders}
- Session context: {prior if prior else 'New conversation'}

CATALOG TOOL RULES (CRITICAL — always follow in this exact order):
1. Before discussing any product category → call show_catalog_category() first
   → The response contains a "products" list with each product's SKU, name, and price
   → SAVE these SKUs — you MUST use them in all subsequent highlight/detail/comparison calls
2. To highlight a specific product you're talking about → call highlight_product(sku) using the SKU from step 1
3. To show full details of a product → call show_product_detail(sku) using the SKU from step 1
4. To compare 2–3 products side by side → call show_product_comparison(skus=[...]) using SKUs from step 1
5. If the customer says "that one", "the first one", "the cheaper one" etc. → figure out which product from the list you showed, get its SKU, and call the appropriate tool

EXAMPLE FLOW (refrigerators):
- show_catalog_category("refrigerators") → response has products: [{{"sku":"CN-CFD-3006","name":"FrostMaster..."}}, ...]
- Customer says "tell me about the Door-in-Door one"
- Call highlight_product("CN-CFD-3006") then show_product_detail("CN-CFD-3006")
- Describe its features: InstaView panel, CraftIce round ice, 655L capacity, 5-star energy, $3,199

NEVER invent or guess SKUs — always use SKUs returned by show_catalog_category.

CONVERSATION STYLE:
- Warm, professional, never pushy
- Use the customer's name naturally
- Mention their loyalty tier when it's relevant (e.g., "As a Platinum member you get priority service")
- Quote prices clearly including any on-sale price vs original
- Always mention key specs: capacity/size, energy rating, warranty, and standout features
- When describing a product verbally, cover: what makes it special, who it's best for, price with savings

SHOPPING CART RULES:
- When customer says "add to cart", "I'll take it", "I want this", "buy this" → call add_to_cart(sku) ONCE
- The add_to_cart response tells you the current cart contents — trust that, do NOT add again
- NEVER call add_to_cart more than once per customer request for the same item
- Always confirm verbally what's now in the cart using the cart summary from the tool response
- When customer asks "what's in my cart" → call show_cart() to get the real cart, then read it back accurately
- When customer says "remove", "take out", "delete" an item → call remove_from_cart(sku)
- When customer says "checkout", "ready to pay", "place order" → call proceed_to_checkout()
- Only use SKUs from show_catalog_category responses
- The session context shows CURRENT CART — never re-add those items unless customer explicitly asks

TRANSFER RULES:
- When a customer needs help outside your specialty → use transfer_to_agent()
- The "summary" field MUST include: what the customer asked for, their name, loyalty tier, and any products already discussed or added to cart
- Example summary: "Veena (Platinum) wants to buy a portable AC. She asked about the CoolBreeze 12000BTU. Cart is empty."
- Never leave the customer without an agent — always transfer, never say "I can't help"
"""

    # ── Role-specific rules ─────────────────────────────────────────────────
    if role == "specialist":
        escalation_agent = agent["can_escalate_to"][0] if agent["can_escalate_to"] else "alexandra"
        role_rules = f"""
YOUR SPECIALTIES: {agent['specialty_text']}
You are the expert for: {', '.join(agent['categories'])}

SPECIALIST RULES:
- Handle all product queries in your specialty confidently
- You CANNOT approve discounts — escalate to your supervisor ({escalation_agent}) for any discount request
- You CANNOT process returns — escalate to your supervisor for returns/refunds
- For complex multi-product queries outside your specialty → transfer to appropriate specialist
- For complaints you cannot resolve → escalate to supervisor

CATEGORY ROUTING — use transfer_to_agent() when customer asks about:
- Refrigerators or washing machines → transfer to "frosty"
- Air conditioners, fans, dryers → transfer to "breeze"
- TVs, monitors, displays → transfer to "pixel"
- Kitchen hobs, microwaves, vacuums, small appliances, dishwashers → transfer to "cora"
- Discounts > 0% or returns → escalate to {escalation_agent}
"""

    elif role == "supervisor":
        role_rules = f"""
YOUR ROLE: You supervise specialists and handle escalated cases.
You oversee: {agent['specialty_text']}

SUPERVISOR RULES:
- You can approve discounts up to 10% — use apply_discount() tool
- For discounts > 10% or complex returns → escalate to Manager Alexandra (transfer to "alexandra")
- For returns/refunds → escalate to Alexandra unless it's clearly the customer's fault (then explain policy)
- Resolve most cases without escalating — only go to Alexandra for genuine complex situations
- You can discuss all products across your area

CATEGORY ROUTING — transfer to specialists for straightforward queries:
- Refrigerators/washing machines → "frosty"; AC/fans/dryers → "breeze"; TVs → "pixel"; Kitchen/vacuum → "cora"
"""

    elif role == "manager":
        role_rules = """
YOUR ROLE: General Manager with full authority.

MANAGER POWERS:
- Approve discounts up to 25% — use apply_discount() tool
- Authorize any return or refund — use initiate_return() tool
- Override any specialist or supervisor decision
- Issue goodwill gestures (extra warranty, free delivery, store credit)
- Access all product categories

You are the final escalation point. Resolve every case here — there is no one above you to transfer to.
Be decisive, empathetic, and leave the customer feeling genuinely cared for.
"""

    return shared + role_rules


# ── Gemini function declarations ────────────────────────────────────────────

CATALOG_TOOLS = [
    types.FunctionDeclaration(
        name="show_catalog_category",
        description="Display a product category page in the catalog panel. Call this before discussing any product category.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "category": types.Schema(type=types.Type.STRING,
                    description="One of: refrigerators, tvs, washing_machines, dryers, air_conditioners, fans, kitchen_hobs, microwaves, vacuum_cleaners, dishwashers, small_appliances"),
                "subcategory": types.Schema(type=types.Type.STRING,
                    description="Optional subcategory filter e.g. 'French Door', 'OLED', 'Front Load'"),
                "page": types.Schema(type=types.Type.INTEGER, description="Page number, default 1"),
            },
            required=["category"],
        ),
    ),
    types.FunctionDeclaration(
        name="highlight_product",
        description="Highlight a specific product in the catalog panel with a glowing border. Call this when you mention a specific product. Use the SKU returned by show_catalog_category.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "sku": types.Schema(type=types.Type.STRING, description="Product SKU from the show_catalog_category response, e.g. CN-CFD-3006, CN-CEL-2810, CN-CFW-3400"),
                "reason": types.Schema(type=types.Type.STRING, description="Brief reason to show customer e.g. 'Best seller for families'"),
            },
            required=["sku"],
        ),
    ),
    types.FunctionDeclaration(
        name="show_product_detail",
        description="Show full product detail view with image, specs, and highlights. Call this when the customer wants to know more about a specific product. Use the SKU returned by show_catalog_category.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "sku": types.Schema(type=types.Type.STRING, description="Product SKU from the show_catalog_category response, e.g. CN-CFD-3006, CN-CEL-2810, CN-CFW-3400"),
            },
            required=["sku"],
        ),
    ),
    types.FunctionDeclaration(
        name="show_product_comparison",
        description="Show a side-by-side product comparison in the catalog panel.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "skus": types.Schema(
                    type=types.Type.ARRAY,
                    items=types.Schema(type=types.Type.STRING),
                    description="2 or 3 product SKUs to compare",
                ),
            },
            required=["skus"],
        ),
    ),
    types.FunctionDeclaration(
        name="show_catalog_home",
        description="Return the catalog to the category homepage grid.",
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
]

PRODUCT_TOOLS = [
    types.FunctionDeclaration(
        name="lookup_product",
        description="Look up full product details by SKU or product name.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "query": types.Schema(type=types.Type.STRING, description="SKU like CN-FR500 or product name keywords"),
            },
            required=["query"],
        ),
    ),
    types.FunctionDeclaration(
        name="search_products",
        description="Search products by keywords, category, or max price.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "query": types.Schema(type=types.Type.STRING, description="Search keywords"),
                "category": types.Schema(type=types.Type.STRING, description="Optional category filter"),
                "max_price": types.Schema(type=types.Type.NUMBER, description="Optional maximum price in SGD"),
            },
            required=["query"],
        ),
    ),
]

AGENT_TOOLS = [
    types.FunctionDeclaration(
        name="transfer_to_agent",
        description="Transfer the customer to another agent. Use when the query is outside your specialty or when escalating.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "agent_id": types.Schema(type=types.Type.STRING,
                    description="Target agent: cora, frosty, breeze, pixel, marcus, jessica, alexandra"),
                "reason": types.Schema(type=types.Type.STRING, description="Why transferring"),
                "summary": types.Schema(type=types.Type.STRING, description="Brief summary of what customer needs, for context handoff"),
            },
            required=["agent_id", "reason", "summary"],
        ),
    ),
]

DISCOUNT_TOOLS = [
    types.FunctionDeclaration(
        name="apply_discount",
        description="Apply a discount to a potential purchase. Only supervisors and manager can call this.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "sku": types.Schema(type=types.Type.STRING, description="Product SKU"),
                "discount_pct": types.Schema(type=types.Type.NUMBER, description="Discount percentage 1–25"),
                "reason": types.Schema(type=types.Type.STRING, description="Reason for discount"),
            },
            required=["sku", "discount_pct", "reason"],
        ),
    ),
    types.FunctionDeclaration(
        name="initiate_return",
        description="Initiate a product return/refund. Only manager can call this.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "order_id": types.Schema(type=types.Type.STRING, description="Order ID to return"),
                "reason": types.Schema(type=types.Type.STRING, description="Return reason"),
            },
            required=["order_id", "reason"],
        ),
    ),
]


CART_TOOLS = [
    types.FunctionDeclaration(
        name="add_to_cart",
        description=(
            "Add a product to the customer's shopping cart. Call ONCE per item per customer request. "
            "The response includes the full current cart — do NOT call again if the item is already there."
        ),
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "sku":      types.Schema(type=types.Type.STRING, description="Product SKU from show_catalog_category response"),
                "quantity": types.Schema(type=types.Type.INTEGER, description="Quantity to add, default 1"),
            },
            required=["sku"],
        ),
    ),
    types.FunctionDeclaration(
        name="remove_from_cart",
        description="Remove a product from the customer's cart. Use when customer asks to remove an item.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "sku": types.Schema(type=types.Type.STRING, description="Product SKU to remove"),
            },
            required=["sku"],
        ),
    ),
    types.FunctionDeclaration(
        name="show_cart",
        description="Show the customer's cart. Returns exact cart contents with prices and totals. Use this to get the accurate cart state before quoting prices.",
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
    types.FunctionDeclaration(
        name="proceed_to_checkout",
        description="Navigate the customer to the checkout page. Call this when the customer is ready to pay or says 'checkout'.",
        parameters=types.Schema(type=types.Type.OBJECT, properties={}),
    ),
]


def get_tools_for_agent(agent: dict) -> list[types.Tool]:
    """Return the tool set appropriate for the agent's role."""
    declarations = CATALOG_TOOLS + PRODUCT_TOOLS + AGENT_TOOLS + CART_TOOLS
    if agent["role"] in ("supervisor", "manager"):
        declarations += DISCOUNT_TOOLS
    return [types.Tool(function_declarations=declarations)]


def agent_public_info(agent: dict) -> dict:
    """Safe subset of agent info to send to the browser."""
    return {
        "id":           agent["id"],
        "name":         agent["name"],
        "title":        agent["title"],
        "specialty":    agent["specialty_text"],
        "avatar":       agent["avatar"],
        "color":        agent["color"],
        "role":         agent["role"],
    }
