# CoolNest — System Design Document

## Overview

CoolNest is a voice-first AI call center for a fictional Singapore appliance brand. Customers log in and talk to specialised AI agents via the browser microphone. Agents can display products, take items into a shopping cart, and hand off to colleagues — all in real time, driven by Gemini Live's native audio model.

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
- **asyncio coordination via `done` Event.** Two tasks run per Gemini session: `browser_to_gemini` (b2g) and `gemini_to_browser` (g2b). Whichever exits first sets `done`, the other stops, then the session loop decides whether to transfer, reconnect, or exit.

---

## Backend Files

### `config.py`

| Setting | Value |
|---|---|
| `PROJECT_ID` | `my-project-0004-346516` |
| `LIVE_MODEL` | `gemini-3.1-flash-live-preview` |
| `GEMINI_API_KEY` | AI Studio key (Gemini 3.1 Live not on Vertex AI yet) |
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
| `cora` | Cora | specialist | Kitchen hobs, vacuums, small appliances, microwaves, dishwashers | Aoede |
| `frosty` | Frosty | specialist | Refrigerators, washing machines | Charon |
| `breeze` | Breeze | specialist | Air conditioners, fans, dryers | Puck |
| `pixel` | Pixel | specialist | TVs | Fenrir |
| `marcus` | Marcus | supervisor | Frosty + Breeze area | Fenrir |
| `jessica` | Jessica | supervisor | Cora + Pixel area | Kore |
| `alexandra` | Alexandra | manager | All — final escalation | Aoede |

Each agent has: id, name, role, title, specialty_text, voice, avatar, color, categories, can_escalate_to, greeting.

**System prompt structure** (`build_system_prompt`):
- Shared section: brand identity, customer info (name, loyalty tier, recent orders), catalog tool rules, conversation style, shopping cart rules, transfer rules
- Role-specific section: specialist rules (escalation limits, category routing), supervisor rules (discount up to 10%, returns → alexandra), manager rules (full authority)

**Tool sets by role:**
- All agents: `CATALOG_TOOLS + PRODUCT_TOOLS + AGENT_TOOLS + CART_TOOLS`
- Supervisors + Manager additionally: `DISCOUNT_TOOLS`

### `ws_handler.py` — WebSocket Core

**Auth flow:** First WS message must be `{user_id, token}`. Verified via `verify_token()` before any Gemini session starts.

**Session loop (`handle_websocket`):**
```
while True:
    result = await run_agent_session(ws, user, current_agent_id, ...)
    if browser_gone  → break
    if transfer      → update current_agent_id, continue
    if reconnect     → backoff sleep, build reconnect context, continue
```

**Reconnect logic:**
- On Gemini GoAway or session close: backoff from 1s → 2s → 4s → 8s (max)
- Max 10 reconnects before giving up with error
- **Reset reconnect counter** if `session_responses > 20` — indicates a healthy session that hit Gemini's natural ~15-min time limit, not a crash

**SKU persistence across reconnects:**  
`last_shown_products` and `last_shown_category` are persisted in `handle_websocket` across session boundaries. On reconnect, injected into the context prompt so the agent can call `add_to_cart` without needing to `show_catalog_category` again.

**Transfer greeting fix:**  
On agent transfer, `g2b` (gemini→browser) task starts first, gets one async tick (`await asyncio.sleep(0)`) to initialise its iterator, then the greeting trigger is sent via `send_client_content`. `b2g` (browser→gemini) is delayed 2 seconds on transfers to prevent the interleaving double-response bug.

```python
g2b = asyncio.create_task(gemini_to_browser())
await asyncio.sleep(0)          # let g2b start its async iterator

if is_transfer:
    await gemini.send_client_content(turns=..., turn_complete=True)  # greeting trigger

async def delayed_b2g():
    if is_transfer:
        await asyncio.sleep(2.0)    # don't send mic audio until greeting is done
    await browser_to_gemini()

b2g = asyncio.create_task(delayed_b2g())
```

**Gemini send methods (3.1 API):**

| Purpose | Method |
|---|---|
| Audio chunk | `gemini.send_realtime_input(audio=types.Blob(...))` |
| Text / trigger | `gemini.send_client_content(turns=types.Content(...), turn_complete=True)` |
| Tool ACK | `gemini.send_tool_response(function_responses=[types.FunctionResponse(...)])` |

**Tool execution (`execute_tool`):**

| Tool | Action |
|---|---|
| `show_catalog_category` | Sends all products to browser UI; returns filtered list to agent; saves `last_shown_products` |
| `highlight_product` | Sends highlight event to browser |
| `show_product_detail` | Sends detail event to browser |
| `show_product_comparison` | Sends comparison event to browser |
| `show_catalog_home` | Resets catalog to home grid |
| `lookup_product` | Direct SKU or text search, returns product |
| `search_products` | Keyword + optional category/price filter |
| `add_to_cart` | Sends `add_to_cart` catalog event to browser |
| `show_cart` | Sends `show_cart` event to browser |
| `proceed_to_checkout` | Sends `show_checkout` event to browser |
| `transfer_to_agent` | Sets `session_state["transfer"]`, ends session |
| `apply_discount` | Sends promotion banner event; supervisors/manager only |
| `initiate_return` | Generates return reference, sends system message |

### `products.py`

11 categories, ~60+ products. Each product has: sku, name, brand, category, subcategory, price, price_original, discount_pct, rating, review_count, in_stock, description, specs (dict), highlights (list), emoji, energy_rating.

**Important fix:** `CN-CBE-2900` (Bespoke refrigerator) subcategory corrected to `"Bespoke"` — was `"4-Door"`, causing "No products in this category" when agent called `show_catalog_category("refrigerators", subcategory="Bespoke")`.

`get_category_products(category, subcategory=None)` — when subcategory is provided, UI always receives all products (so tabs work), but agent receives filtered list for SKU awareness.

### `main.py` — FastAPI App

Static mounts: `/assets`, `/avatars`, `/audio-processors`, `/products`, `/pdfs`

Key REST endpoints:
- `POST /api/login` — returns token + user object
- `GET /api/me` — token verification
- `GET /api/agents` — list all agents (public info only)
- `GET /api/products?category=` — product list, optional category filter
- `GET /api/products/{sku}` — single product
- `POST /api/orders` — creates order, logs line items to BigQuery, returns order ID
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
- `cart` (array of `{product, quantity}`)
- `error`

Key refs:
- `sessionRef` → `CoolNestSession` WS wrapper
- `streamerRef` → `AudioStreamer` (mic capture)
- `playerRef` → `AudioPlayer` (PCM playback)
- `agentRef` → current agent (closure-safe ref for callbacks)

**`agentRef` pattern:** React state is stale in WS callbacks. `agentRef.current` is always updated alongside `setAgent()` so transcript callbacks always label audio with the correct agent name.

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

Applies catalog events from `catalogState` prop (set by `onCatalogAction` callback):
- `show_home` → reset to home grid
- `show_category` → category grid with subcategory tabs, pagination
- `highlight` → glowing border on product card
- `show_detail` → full product detail
- `show_comparison` → side-by-side specs table
- `show_promotion` → floating banner (8-second auto-dismiss)
- `add_to_cart` → calls `onAddToCart` prop
- `show_cart` → switches to cart view
- `show_checkout` → switches to checkout view

Floating cart badge (top-right) shows item count; hidden when in cart/checkout views.

Subcategory filtering: tabs shown when `subcats.length > 2`. Filter applied client-side on the full product list (server always sends all products for the category).

Pagination: `PAGE_SIZE = 4` products per page.

### `src/components/ProductCard.jsx`

Grid card showing: emoji, name, price (with strike-through original + % off), rating stars + review count, "Add to Cart" button with 1.8-second "✓ Added" flash feedback.

### `src/components/ProductDetail.jsx`

Full-page product view: image, badge (sale %), description, highlights list, specs table, quantity selector (+/−), "Add to Cart" button with flash feedback, PDF download link (if product has `pdf_url`).

### `src/components/CartView.jsx`

Shopping cart view:
- Line items: product name, unit price × quantity, line total
- +/− quantity controls (0 removes item)
- Remove button per item
- Subtotal, GST (9% Singapore), **Total**
- "Proceed to Checkout" button
- Empty cart state with "Browse products" link

### `src/components/CheckoutView.jsx`

Two-screen flow:

**Screen 1 — Order form:**
- Singapore delivery address (street, unit, 6-digit postal code)
- Credit card: number (auto-formatted as `XXXX XXXX XXXX XXXX`), name, expiry (auto-formatted as `MM/YY`), CVV
- Order summary: subtotal, GST (9%), total
- "Place Order" button → processing spinner animation

**Screen 2 — Confirmation:**
- Order ID (e.g. `CN-A3B4C5D6`)
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
  → Gemini may call a tool: show_catalog_category("refrigerators")
  → ws_handler execute_tool() → fetches products, sends {type:"catalog_action", action:"show_category", products:[...]}
  → Browser CatalogPanel useEffect → setView({type:"category", products:[...]})
  → UI updates to show refrigerator grid
  → Gemini gets tool response (SKU list) → continues speaking
  → Audio chunks → {type:"audio"} → AudioPlayer.playChunk()
  → Transcript chunks → {type:"transcript"} → AgentPanel transcript bubbles
```

---

## Agent Transfer Flow

```
1. Agent calls transfer_to_agent(agent_id="frosty", reason="...", summary="...")
2. ws_handler sets session_state["transfer"], signals done Event
3. run_agent_session returns {transfer: {to:"frosty", summary:"..."}}
4. handle_websocket sends {type:"agent_changed", agent:{...}} to browser
5. Browser App.jsx onAgentChanged → switchAgent() → 400ms CSS transition → setAgent(newAgent)
6. handle_websocket starts new run_agent_session for "frosty" with transfer summary
7. In run_agent_session:
   a. g2b task starts (listening for Gemini output)
   b. await asyncio.sleep(0)  ← gives g2b one tick to initialise iterator
   c. send_client_content(greeting trigger)  ← Gemini generates greeting
   d. b2g task starts with 2-second delay  ← no mic audio until greeting done
8. Gemini greeting audio arrives → g2b forwards to browser → user hears new agent
```

---

## Known Issues Fixed

| Issue | Root Cause | Fix |
|---|---|---|
| "No products" for Bespoke fridge | `CN-CBE-2900` had subcategory `"4-Door"` but agent passed `"Bespoke"` | Changed product subcategory to `"Bespoke"` |
| Frosty hanging/reconnecting | Vertex AI rate-limiting Gemini Live with speech_config + transcription → immediate GoAway | Switched to AI Studio API key |
| Gemini `media_chunks` deprecated | `realtime_input.media_chunks` removed in 3.1 SDK | Updated to `send_realtime_input`, `send_client_content`, `send_tool_response` |
| "Session ended" after long use | reconnect counter never reset on healthy sessions | Reset when `session_responses > 20` |
| Agent loses SKUs after reconnect | `last_shown_products` not in reconnect context | Persist and inject into reconnect summary |
| Silent transfer (agent doesn't speak) | `g2b` task not started before greeting trigger sent → audio response dropped | Start `g2b` first, `await asyncio.sleep(0)`, then send trigger |
| Double response on transfer | `send_client_content` + `send_realtime_input` concurrent → two model responses | Delay `b2g` by 2 seconds on transfers |
| Silent crash on tool calls | `log = session_state["conversation_log"]` shadowed the module-level Python logger | Renamed to `conv_log` |

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
