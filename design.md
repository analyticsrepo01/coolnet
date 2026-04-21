# CoolNest — System Design Document

## Overview

CoolNest is a voice-first AI call center for a fictional Singapore appliance brand. Customers log in and talk to specialised AI agents via the browser microphone. Agents can display products, manage a shopping cart, apply loyalty discounts, and hand off to colleagues — all in real time, driven by Gemini Live's native audio model.

**Stack:** FastAPI (Python) + React (Vite) + Gemini Live API + BigQuery

---

## Architecture

```
Browser (React)
  │  WebSocket (audio + JSON events)
  │
FastAPI  ─── ws_handler.py ─── Gemini Live API (gemini-3.1-flash-live-preview)
  │                                via AI Studio API key
  ├── /api/login, /api/me        (auth)
  ├── /api/agents                (agent registry)
  ├── /api/products              (catalog REST)
  ├── /api/orders                (order creation → BigQuery)
  └── /assets, /avatars, ...     (static files from React dist + public/)

BigQuery (dataset: coolnest)
  ├── users
  ├── sessions
  ├── messages
  └── handoffs
```

### Key design decisions

- **Single WebSocket per user session.** All audio, catalog events, transcripts, and control messages travel on one WS connection. The server side maintains a session loop that restarts Gemini sessions on timeout/transfer without closing the browser WS.
- **Always-on VAD.** Audio is sent with `send_realtime_input()` — no `end_of_turn`. Gemini's built-in voice activity detection handles speech boundaries. Sending `end_of_turn=True` permanently closes the Gemini session.
- **Never mix `send_client_content` with `send_realtime_input`.** The Gemini 3.1 Live API rejects this with WebSocket 1008 policy violation. All text inputs (greeting triggers, typed text) must use `send_realtime_input(text=...)`.
- **asyncio coordination via `done` Event.** Two tasks run per Gemini session: `browser_to_gemini` (b2g) and `gemini_to_browser` (g2b). Whichever exits first sets `done`, the other stops, then the session loop decides whether to transfer, reconnect, or exit.
- **Server-side cart as agent source of truth.** Cart state lives on the server (`session_state["cart"]`) and persists across all agent sessions. The browser is kept in sync via `set_cart_item` events (idempotent quantity setter), preventing duplicate adds.

---

## Backend Files

### `config.py`

| Setting | Value |
|---|---|
| `PROJECT_ID` | `my-project-0004-346516` |
| `LIVE_MODEL` | `gemini-3.1-flash-live-preview` |
| `GEMINI_API_KEY` | AI Studio key (Gemini 3.1 Live not available on Vertex AI) |
| `LIVE_LOCATION` | `us-central1` (BQ/Vertex only, not for Live API) |
| `PORT` | `7778` |
| `BQ_DATASET` | `coolnest` |

Demo users: `saurabh` (Platinum), `rajan` (Gold), `vamsi` (Silver), `veena` (Platinum).

Discount limits by role: specialist 0%, supervisor 10%, manager 25%.

### `agents.py` — Agent Registry

Seven agents arranged in three tiers:

```
Specialists          Supervisors          Manager
───────────          ───────────          ───────
Cora   ──────────→  Jessica  ──────────→  Alexandra
Pixel  ──────────→  Jessica               (GM, 25% discount, returns)
Frosty ──────────→  Marcus
Breeze ──────────→  Marcus
```

**Agents:**

| ID | Name | Role | Specialties | Voice |
|---|---|---|---|---|
| `cora` | Cora | specialist | Kitchen hobs, vacuums, small appliances, microwaves, dishwashers | Aoede (F) |
| `frosty` | Frosty | specialist | Refrigerators, washing machines | Charon (M) |
| `breeze` | Breeze | specialist | Air conditioners, fans, dryers | Zephyr (F) |
| `pixel` | Pixel | specialist | TVs | Fenrir (M) |
| `marcus` | Marcus | supervisor | Frosty + Breeze area | Fenrir (M) |
| `jessica` | Jessica | supervisor | Cora + Pixel area | Kore (F) |
| `alexandra` | Alexandra | manager | All — final escalation | Aoede (F) |

Note: Breeze was originally on Puck (male) but her avatar is female — corrected to Zephyr, which also means wind/breeze thematically.

Each agent has: id, name, role, title, specialty_text, voice, avatar, color, categories, can_escalate_to, greeting.

**System prompt structure** (`build_system_prompt`):
- Shared section: brand identity, customer info (name, loyalty tier, recent orders, session context), catalog tool rules, conversation style, shopping cart rules, transfer rules
- Role-specific section: specialist rules (escalation limits, category routing), supervisor rules (discount up to 10%, returns → alexandra), manager rules (full authority)

**Shopping cart rules in system prompt:**
- Call `add_to_cart` ONCE per customer request — tool response includes current cart
- Never re-add items already in the cart (session context shows `CURRENT CART`)
- Call `show_cart()` to get the real cart state before quoting totals
- Call `remove_from_cart(sku)` when customer asks to remove an item

**Tool sets by role:**
- All agents: `CATALOG_TOOLS + PRODUCT_TOOLS + AGENT_TOOLS + CART_TOOLS`
- Supervisors + Manager additionally: `DISCOUNT_TOOLS`

### `ws_handler.py` — WebSocket Core

**Auth flow:** First WS message must be `{user_id, token}`. Verified via `verify_token()` before any Gemini session starts.

**Session loop (`handle_websocket`):**
```
shared_cart = {}   # persists across ALL agent sessions for this WS connection

while True:
    session_context = {**context, "_cart": shared_cart}
    result = await run_agent_session(ws, user, current_agent_id, session_context, ...)
    shared_cart = result["cart"]   # update from session
    if browser_gone  → break
    if transfer      → update current_agent_id, inject cart into transfer summary, continue
    if reconnect     → backoff sleep, build reconnect context (includes cart), continue
```

**Reconnect logic:**
- On Gemini GoAway or session close: backoff from 1s → 2s → 4s → 8s (max)
- Max 10 reconnects before giving up with error
- **Reset reconnect counter** if `session_responses > 20` — indicates a healthy session that hit Gemini's natural ~15-min time limit, not a crash

**Reconnect/transfer context injected into new session:**
1. Recent conversation log (last 8 turns)
2. Last shown products with SKUs (so agent can add to cart without re-fetching)
3. **Current cart contents** — `"CURRENT CART — do NOT re-add these items"` with quantities and prices

**Transfer greeting — correct pattern:**
```python
g2b = asyncio.create_task(gemini_to_browser())  # start FIRST

async def delayed_b2g():
    if is_transfer:
        await asyncio.sleep(0.5)   # let g2b's receive loop fully initialise
        await gemini.send_realtime_input(text=greeting_prompt)  # NOT send_client_content
        await asyncio.sleep(2.0)   # let greeting play before mic audio starts
    await browser_to_gemini()

b2g = asyncio.create_task(delayed_b2g())
```

**Why `send_realtime_input(text=...)` not `send_client_content`:**  
Mixing `send_client_content` into a session that uses `send_realtime_input(audio=...)` triggers WebSocket 1008 policy violation (`"Operation is not implemented, or supported, or enabled"`), killing the Gemini session silently. The session then reconnects but without the greeting — causing long silent pauses. All text input including greeting triggers must use `send_realtime_input(text=...)`.

**Gemini send methods (3.1 API):**

| Purpose | Method |
|---|---|
| Audio chunk | `gemini.send_realtime_input(audio=types.Blob(..., mime_type="audio/pcm;rate=16000"))` |
| Text / greeting trigger | `gemini.send_realtime_input(text="...")` |
| Tool ACK | `gemini.send_tool_response(function_responses=[types.FunctionResponse(...)])` |

**Server-side cart (`session_state["cart"]`):**

Structure: `{sku: {product, quantity, discounted_price, original_price}}`

Initialised from `context["_cart"]` (the shared cart passed in from `handle_websocket`). Returned in `run_agent_session` result and merged back into `shared_cart` after each session.

**Tool execution (`execute_tool`):**

| Tool | Action |
|---|---|
| `show_catalog_category` | Sends all products to browser; returns filtered list + SKUs to agent; saves `last_shown_products` |
| `highlight_product` | Sends highlight event to browser |
| `show_product_detail` | Sends detail event to browser |
| `show_product_comparison` | Sends comparison event to browser |
| `show_catalog_home` | Resets catalog to home grid |
| `lookup_product` | Direct SKU or text search, returns product |
| `search_products` | Keyword + optional category/price filter |
| `add_to_cart` | Updates server cart; sends `set_cart_item` (exact quantity) to browser; returns full cart summary to agent |
| `remove_from_cart` | Removes from server cart; sends `remove_from_cart` event to browser |
| `show_cart` | Navigates browser to cart view; returns exact cart contents + totals to agent |
| `proceed_to_checkout` | Sends `show_checkout` event to browser |
| `transfer_to_agent` | Sets `session_state["transfer"]`, signals `done` Event |
| `apply_discount` | Updates server cart price; sends promo banner + `apply_cart_discount` event; supervisors/manager only |
| `initiate_return` | Generates return reference, sends system message; manager only |

**Why `set_cart_item` instead of `add_to_cart` browser event:**  
`set_cart_item` sets the exact quantity for a SKU (idempotent). If the agent calls `add_to_cart` twice for the same product (a common LLM mistake), the browser cart stays correct because the server deduplicates and always sends the authoritative quantity. The old `add_to_cart` browser event would increment quantity on every call.

### `products.py`

11 categories, ~60+ products. Each product has: sku, name, brand, category, subcategory, price, price_original, discount_pct, rating, review_count, in_stock, description, specs (dict), highlights (list), emoji, energy_rating.

`get_category_products(category, subcategory=None)` — UI always receives all category products (subcategory tabs work client-side); agent receives subcategory-filtered list for accurate SKU awareness.

### `main.py` — FastAPI App

Static mounts: `/assets`, `/avatars`, `/audio-processors`, `/products`, `/pdfs`

Key REST endpoints:
- `POST /api/login` — returns token + user object
- `GET /api/me` — token verification
- `GET /api/agents` — list all agents (public info only)
- `GET /api/products?category=` — product list, optional category filter
- `GET /api/products/{sku}` — single product
- `POST /api/orders` — creates order ID, logs line items to BigQuery, returns `{order_id, status, total, delivery}`
- `GET /api/health`
- `WS /ws` → `handle_websocket()`
- Catch-all `GET /{path}` → serves React `index.html`

### `bq_client.py`

BigQuery tables in dataset `coolnest`:
- `users` — upserted on each login
- `sessions` — session start/end timestamps
- `messages` — all transcribed turns (user + agent)
- `handoffs` — agent transfer events

Also: `get_user_context()` — fetches user preferences/notes; `get_user_orders()` — recent purchase history injected into system prompt.

### `auth.py`

Token = SHA-256 hash of `user_id + ":" + password`. No JWT, no expiry — stateless verification.

---

## Frontend Files

### `src/App.jsx` — Root Component

State managed here:
- `user`, `agent`, `connected`, `connecting`, `reconnecting`
- `micEnabled`, `volume`, `agentSpeaking`
- `transcript` (array, max 120 entries, 5-second merge window for same speaker)
- `transitioning` (agent switch animation)
- `catalogState` (last catalog event from server)
- `cart` (array of `{product, quantity, discountedFrom?}`)
- `error`

Key refs:
- `sessionRef` → `CoolNestSession` WS wrapper
- `streamerRef` → `AudioStreamer` (mic capture)
- `playerRef` → `AudioPlayer` (PCM playback)
- `agentRef` → current agent (closure-safe ref for callbacks)

**`agentRef` pattern:** React state is stale in WS callbacks. `agentRef.current` is always updated alongside `setAgent()` so transcript callbacks always label audio with the correct agent name.

**Cart handlers:**
- `handleAddToCart(product, quantity)` — merges quantity if SKU exists (used by UI buttons)
- `handleSetCartItem(product, quantity, discountedPrice, originalPrice)` — sets exact quantity (used by agent via `set_cart_item` event); prevents duplicate adds
- `handleUpdateCartQty(sku, delta)` — UI +/− buttons
- `handleRemoveFromCart(sku)` — UI remove button or agent `remove_from_cart`
- `handleApplyDiscount(sku, discountedPrice, originalPrice)` — updates price + sets `discountedFrom`
- `handleClearCart()` — clears after order placed

**UI tones:** `playTone('connect')` on session ready, `playTone('transfer')` on agent change, `playTone('disconnect')` on session end.

**Home button:** 🏠 CoolNest logo in header is a button that fires `setCatalogState({action:'show_home'})` — resets catalog to home from anywhere.

### `src/utils/coolnest-ws.js` — CoolNestSession

WebSocket wrapper. Handles:
- Auth handshake (`{user_id, token}`)
- Message routing to callbacks: `onReady`, `onAgentChanged`, `onCatalogAction`, `onTranscript`, `onAudio`, `onSystemMessage`, `onError`, `onReconnecting`, `onDisconnect`
- `sendAudio(chunk)` — base64 encodes PCM and sends as `{type:"audio", data:...}`
- `sendText(text)` — sends as `{type:"text", data:...}`
- `disconnect()` — closes WS

### `src/utils/media-utils.js`

**AudioStreamer:**
- Gets mic via `getUserMedia({audio:{sampleRate:16000, channelCount:1}})`
- `AudioWorkletProcessor` resamples to 16 kHz mono PCM16
- Streams 512-sample chunks to callback

**AudioPlayer:**
- Receives base64 PCM16 from server
- Queues and plays chunks through `AudioContext`
- `interrupt()` — stops current playback (user pressed mic)
- `setVolume(v)` — controls gain node
- `destroy()` — closes audio context

**`playTone(type)`** — Web Audio API synthesis, no audio files needed:
| Type | Sound | Trigger |
|---|---|---|
| `connect` | C5 → E5 ascending chime | Session ready |
| `transfer` | Quick rising two-note ding (triangle wave) | Agent transfer |
| `disconnect` | E5 → C5 descending fade | Session ended |

### `src/components/AgentPanel.jsx`

Left panel (320px fixed width). Contains:
- Agent avatar + name + title + specialty
- Connection status indicator (green pulse = listening, yellow = reconnecting)
- Transcript bubbles (scrollable, color-coded by speaker)
- Mic toggle button + volume slider
- Text input (fallback for typed queries)
- Disconnect button

### `src/components/CatalogPanel.jsx`

Right panel (flex-1). Views: `home`, `category`, `detail`, `comparison`, `cart`, `checkout`.

Applies catalog events from `catalogState` prop:

| Action | Effect |
|---|---|
| `show_home` | Reset to category grid |
| `show_category` | Category grid with subcategory tabs + pagination |
| `highlight` | Glowing border on product card |
| `show_detail` | Full product detail view |
| `show_comparison` | Side-by-side specs table |
| `show_promotion` | Floating banner (8-second auto-dismiss) |
| `set_cart_item` | Sets exact quantity for a SKU (calls `onSetCartItem`) |
| `remove_from_cart` | Removes SKU from cart (calls `onRemoveFromCart`) |
| `apply_cart_discount` | Updates item price + sets `discountedFrom` (calls `onApplyDiscount`) |
| `show_cart` | Switches to cart view |
| `show_checkout` | Switches to checkout view |

Floating cart badge (top-right) shows item count; hidden when in cart/checkout views.

Subcategory filtering: tabs shown when `subcats.length > 2`. Filter applied client-side on the full product list (server always sends all products for the category).

Pagination: `PAGE_SIZE = 4` products per page.

### `src/components/ProductCard.jsx`

Grid card showing: emoji, name, price (with strike-through original + % off), rating stars + review count, "Add to Cart" button with 1.8-second "✓ Added" flash feedback (`e.stopPropagation()` prevents card click).

### `src/components/ProductDetail.jsx`

Full-page product view: image, badge (sale %), description, highlights list, specs table, quantity selector (+/−), "Add to Cart" button with flash feedback, PDF download link (if product has `pdf_url`).

### `src/components/CartView.jsx`

Shopping cart view:
- Line items: product name, discounted price (with strikethrough original if loyalty discount applied), quantity × price, green "Loyalty discount" badge
- +/− quantity controls (0 removes item)
- Remove button per item
- Subtotal, GST (9% Singapore), **Total**
- "Proceed to Checkout" button
- Empty cart state with "Browse products" link

Cart items have shape: `{product, quantity, discountedFrom?}`. When `discountedFrom` is set, the original price is shown struck through and the discounted price in brand colour.

### `src/components/CheckoutView.jsx`

Two-screen flow:

**Screen 1 — Order form:**
- Singapore delivery address (street, unit, 6-digit postal code)
- Credit card: number (auto-formatted as `XXXX XXXX XXXX XXXX`), name, expiry (auto-formatted as `MM/YY`), CVV
- Order summary: each line item with strikethrough original price if discounted, subtotal, GST (9%), total
- "Place Order" button → processing spinner animation

**Screen 2 — Confirmation:**
- Order ID (e.g. `CN-A3B4C5D6`)
- Line items with discounts shown
- Estimated delivery: 3–5 business days
- "Continue Shopping" → back to home

POSTs to `POST /api/orders` with cart items, user auth, total. Falls back to client-generated order ID on API error.

---

## Event Flow: Voice to Catalog

```
User speaks → AudioStreamer captures PCM → CoolNestSession.sendAudio()
  → WS {type:"audio", data:"<base64 PCM16>"}
  → ws_handler browser_to_gemini() → gemini.send_realtime_input(audio=...)
  → Gemini VAD detects end of speech → model generates response
  → Gemini calls tool: show_catalog_category("refrigerators")
  → ws_handler execute_tool() → fetches products, sends {type:"catalog_action", action:"show_category", products:[...]}
  → Browser CatalogPanel useEffect → setView({type:"category", products:[...]})
  → UI updates to show refrigerator grid
  → Gemini gets tool response (SKU list) → continues speaking
  → Audio chunks → {type:"audio"} → AudioPlayer.playChunk()
  → Transcript chunks → {type:"transcript"} → AgentPanel transcript bubbles
```

## Cart Flow

```
User says "add it to my cart"
  → Gemini calls add_to_cart(sku="CN-CBE-2900", quantity=1)
  → ws_handler: check server cart → SKU not present → add to session_state["cart"]
  → send {type:"catalog_action", action:"set_cart_item", product:{...}, quantity:1}
  → Browser handleSetCartItem → setCart(prev → [...prev, {product, quantity:1}])
  → Tool response to Gemini: {status:"ok", cart:["1x Bespoke 648L @ $4199.00"]}
  → Gemini: "I've added the Bespoke fridge to your cart!"

User says "add another one"
  → Gemini calls add_to_cart(sku="CN-CBE-2900", quantity=1)
  → ws_handler: SKU already in cart → quantity 1+1=2 → send set_cart_item quantity=2
  → Browser: updates existing item to quantity 2 (no duplicate)
  → Tool response: {cart:["2x Bespoke 648L @ $4199.00"]}
```

---

## Agent Transfer Flow

```
1. Agent calls transfer_to_agent(agent_id="frosty", reason="...", summary="...")
2. ws_handler sets session_state["transfer"], signals done Event
3. run_agent_session returns {transfer:{to:"frosty",...}, cart:{...}}
4. handle_websocket: shared_cart updated from result
5. Browser receives {type:"agent_changed"} → playTone('transfer') → 400ms CSS transition
6. handle_websocket builds transfer summary including CURRENT CART
7. Starts new run_agent_session for "frosty" with shared_cart injected via context["_cart"]
8. In run_agent_session:
   a. g2b task starts (begins iterating gemini.receive())
   b. delayed_b2g waits 0.5s (g2b receive loop fully initialised)
   c. send_realtime_input(text=greeting_prompt) — Gemini generates greeting
   d. b2g waits another 2.0s before starting mic audio relay
9. Gemini greeting audio → g2b forwards to browser → user hears new agent immediately
```

---

## Known Issues Fixed

| Issue | Root Cause | Fix |
|---|---|---|
| "No products" for Bespoke fridge | `CN-CBE-2900` subcategory was `"4-Door"`, agent passed `"Bespoke"` | Changed product subcategory to `"Bespoke"` |
| Frosty hanging/reconnecting | Vertex AI rate-limiting Gemini Live → immediate GoAway | Switched to AI Studio API key |
| Gemini `media_chunks` deprecated | `realtime_input.media_chunks` removed in SDK 3.1 | Updated to `send_realtime_input`, `send_tool_response` |
| "Session ended" after long use | Reconnect counter never reset on healthy sessions | Reset when `session_responses > 20` |
| Agent loses SKUs after reconnect | `last_shown_products` not in reconnect context | Persist and inject into reconnect summary |
| New agent silent after transfer | `g2b` not started before greeting trigger → audio response dropped | Start `g2b` first, then send trigger inside `delayed_b2g` after 0.5s |
| WebSocket 1008 policy violation on transfer | `send_client_content` mixed with `send_realtime_input` — prohibited in 3.1 | Use `send_realtime_input(text=...)` for greeting trigger |
| Double response on transfer | Concurrent greeting trigger + mic audio → two simultaneous model responses | Delay `b2g` by 2.5s total on transfers |
| Transfer greeting delayed 4+ minutes | 1008 error killed session silently; reconnect had no greeting → waited for user audio | Fixed by using correct `send_realtime_input(text=...)` |
| Agent adds same item to cart multiple times | LLM calls `add_to_cart` multiple times; browser incremented on each call | Server-side cart deduplication + `set_cart_item` (exact quantity) |
| Agent makes up cart contents | No real cart state returned to agent | `show_cart` / `add_to_cart` tool responses include full cart summary |
| Discount not applied in cart | `apply_discount` only showed a banner | Also sends `apply_cart_discount` action; updates server cart price |
| Discount not shown at checkout | CheckoutView only read `product.price` | Added `discountedFrom` display with strikethrough in both order summary and confirmation |
| Cart lost on agent transfer | Cart lived only in individual session state | `shared_cart` in `handle_websocket` persists across all sessions; new agent receives it via `context["_cart"]` |
| Logger silent crash on tool calls | `log = session_state["conversation_log"]` shadowed module-level Python logger | Renamed to `conv_log` |
| Breeze had male voice | Used `Puck` (male), avatar is female | Changed to `Zephyr` (female, thematically fits "breeze") |

---

## Gemini Live Configuration

```python
types.LiveConnectConfig(
    response_modalities=["AUDIO"],
    system_instruction=types.Content(parts=[types.Part(text=system_prompt)]),
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=agent["voice"])
        )
    ),
    tools=tools,
    input_audio_transcription=types.AudioTranscriptionConfig(),
    output_audio_transcription=types.AudioTranscriptionConfig(),
)
```

Audio format: PCM16, 16 kHz, mono, 512-sample chunks (browser → server), 24 kHz PCM16 (server → browser, Gemini native output).

---

## Secrets & `.gitignore`

**Never commit `backend/config.py`** — it contains the AI Studio API key (`GEMINI_API_KEY`) and demo user passwords. It is listed in `.gitignore` and must stay that way.

`.gitignore` covers:
```
backend/config.py       ← API key + user credentials
.env / *.env            ← any env file
frontend/node_modules/  ← npm packages
frontend/dist/          ← React build output (regenerate with npm run build)
__pycache__/            ← Python bytecode
*.log / nohup.out       ← runtime logs
```

When deploying to a new machine, copy `config.py` manually or provision it via a secret manager — do not add it to git.

---

## Running the App

```bash
# Build frontend
cd /home/jupyter/coolnest/frontend && npm run build

# Start backend (serves React + WS + REST)
cd /home/jupyter/coolnest/backend && python main.py
# Runs on port 7778

# Access via JupyterLab proxy
# https://<notebook-url>/proxy/7778/
```

Demo credentials: `saurabh / Cool@123`, `veena / Cool@123`, `rajan / Nest@456`, `vamsi / Home@789`
