"""
CoolNest WebSocket handler.
Proxies audio to Gemini Live API (native-audio model), intercepts function
calls to drive the catalog UI and agent transfers.

Key design:
- asyncio.Event (done) coordinates the two relay tasks so neither hangs
- Audio is ALWAYS sent as end_of_turn=False — the native model's built-in
  VAD detects speech boundaries; explicit end_of_turn breaks the session
- Transcription comes via output_/input_transcription on server_content
"""
import asyncio
import base64
import json
import uuid
import logging
import os

from fastapi import WebSocket, WebSocketDisconnect
from google import genai
from google.genai import types

import bq_client as bq
from agents import AGENTS, build_system_prompt, get_tools_for_agent, agent_public_info
from auth import verify_token
from config import PROJECT_ID, LIVE_LOCATION, LIVE_MODEL
from products import PRODUCTS, get_category_products, search_products

log = logging.getLogger("coolnest.ws")
logging.basicConfig(level=logging.INFO)

os.environ.setdefault("GOOGLE_CLOUD_PROJECT", PROJECT_ID)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", LIVE_LOCATION)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


def _get_genai_client():
    return genai.Client(vertexai=True, project=PROJECT_ID, location=LIVE_LOCATION)


# ── Tool execution ──────────────────────────────────────────────────────────

async def execute_tool(name: str, args: dict, ws: WebSocket, session_state: dict) -> dict:
    """Execute a Gemini function call; emit catalog events to browser as needed."""

    # ── Catalog display ────────────────────────────────────────────────────
    if name == "show_catalog_category":
        category   = args.get("category", "")
        subcategory = args.get("subcategory")
        page       = args.get("page", 1)
        products   = get_category_products(category, subcategory)
        await _send(ws, {
            "type": "catalog_action", "action": "show_category",
            "category": category, "subcategory": subcategory,
            "page": page, "products": products,
        })
        # Return product list so agent knows the SKUs and can call show_product_detail
        product_list = [
            {"sku": p["sku"], "name": p["name"], "price": p["price"],
             "subcategory": p.get("subcategory", ""), "rating": p.get("rating")}
            for p in products
        ]
        return {"status": "ok", "products_shown": len(products), "products": product_list}

    if name == "highlight_product":
        sku = args.get("sku", "")
        product = PRODUCTS.get(sku)
        if product:
            await _send(ws, {"type": "catalog_action", "action": "highlight",
                             "sku": sku, "reason": args.get("reason", ""), "product": product})
            return {"status": "ok", "product": product["name"]}
        return {"status": "error", "message": f"SKU {sku} not found"}

    if name == "show_product_detail":
        sku = args.get("sku", "")
        product = PRODUCTS.get(sku)
        if product:
            await _send(ws, {"type": "catalog_action", "action": "show_detail",
                             "sku": sku, "product": product})
            return {"status": "ok"}
        return {"status": "error", "message": f"SKU {sku} not found"}

    if name == "show_product_comparison":
        skus     = args.get("skus", [])
        products = [PRODUCTS[s] for s in skus if s in PRODUCTS]
        if products:
            await _send(ws, {"type": "catalog_action", "action": "show_comparison",
                             "products": products})
            return {"status": "ok", "count": len(products)}
        return {"status": "error", "message": "No valid SKUs"}

    if name == "show_catalog_home":
        await _send(ws, {"type": "catalog_action", "action": "show_home"})
        return {"status": "ok"}

    # ── Product lookup ─────────────────────────────────────────────────────
    if name == "lookup_product":
        q = args.get("query", "")
        product = PRODUCTS.get(q.upper()) or next(iter(search_products(q)), None)
        return {"product": product} if product else {"error": f"No product for '{q}'"}

    if name == "search_products":
        results = search_products(
            args.get("query", ""),
            category=args.get("category"),
            max_price=args.get("max_price"),
        )
        return {"results": results[:6], "count": len(results)}

    # ── Agent transfer ─────────────────────────────────────────────────────
    if name == "transfer_to_agent":
        session_state["transfer"] = {
            "to":      args.get("agent_id", "cora"),
            "reason":  args.get("reason", ""),
            "summary": args.get("summary", ""),
        }
        return {"status": "transferring", "to": args.get("agent_id")}

    # ── Supervisor / manager only ──────────────────────────────────────────
    if name == "apply_discount":
        sku       = args.get("sku", "")
        pct       = args.get("discount_pct", 0)
        product   = PRODUCTS.get(sku, {})
        original  = product.get("price", 0)
        discounted = round(original * (1 - pct / 100), 2)
        await _send(ws, {
            "type": "catalog_action", "action": "show_promotion",
            "title": f"{int(pct)}% Loyalty Discount Applied!",
            "description": f"{product.get('name', sku)}: ${discounted:.2f} (was ${original:.2f})",
            "discount_pct": pct, "sku": sku,
        })
        return {"status": "ok", "discounted_price": discounted, "sku": sku, "discount_pct": pct}

    if name == "initiate_return":
        order_id = args.get("order_id", "")
        ref = f"RET-{uuid.uuid4().hex[:8].upper()}"
        await _send(ws, {"type": "system_message",
                         "text": f"Return initiated for order {order_id} — ref {ref}. Team will contact you within 24h."})
        return {"status": "ok", "order_id": order_id, "return_reference": ref}

    log.warning(f"Unknown tool call: {name}")
    return {"error": f"Unknown tool '{name}'"}


async def _send(ws: WebSocket, obj: dict):
    """Best-effort JSON send — swallows closed-socket errors."""
    try:
        await ws.send_json(obj)
    except Exception:
        pass


async def _ws_alive(ws: WebSocket) -> bool:
    """Ping the browser to verify the WebSocket is still open."""
    try:
        await ws.send_json({"type": "ping"})
        return True
    except Exception:
        return False


# ── Single Gemini Live session ──────────────────────────────────────────────

async def run_agent_session(
    ws: WebSocket,
    user: dict,
    agent_id: str,
    session_id: str,
    context: dict,
    initial_summary: str = "",
) -> dict:
    """
    Run one Gemini Live session for one agent.
    Returns {"transfer": {...}} if the agent requested a handoff, else {}.
    """
    agent = AGENTS[agent_id]
    if initial_summary:
        context = {**context, "session_summary": initial_summary}

    system_prompt = build_system_prompt(agent, user, context)
    tools         = get_tools_for_agent(agent)

    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        system_instruction=types.Content(parts=[types.Part(text=system_prompt)]),
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=agent["voice"])
            )
        ),
        tools=tools,
        # Transcription — capture both sides for the transcript panel
        input_audio_transcription=types.AudioTranscriptionConfig(),
        output_audio_transcription=types.AudioTranscriptionConfig(),
    )

    session_state = {"transfer": None, "browser_disconnected": False, "conversation_log": []}
    # done is set by whichever task exits first → signals the other to stop
    done = asyncio.Event()

    client = _get_genai_client()
    try:
        async with client.aio.live.connect(model=LIVE_MODEL, config=config) as gemini:

            # ── browser → Gemini ──────────────────────────────────────────
            async def browser_to_gemini():
                try:
                    while not done.is_set():
                        try:
                            # 30-second timeout keeps the task alive during silence
                            raw = await asyncio.wait_for(ws.receive_text(), timeout=30.0)
                        except asyncio.TimeoutError:
                            continue   # nothing sent — just loop
                        except WebSocketDisconnect:
                            log.info("Browser disconnected")
                            session_state["browser_disconnected"] = True
                            break

                        try:
                            msg   = json.loads(raw)
                        except json.JSONDecodeError:
                            continue

                        mtype = msg.get("type")

                        if mtype == "audio":
                            audio_bytes = base64.b64decode(msg["data"])
                            # IMPORTANT: end_of_turn is always False for audio.
                            # The native audio model uses built-in VAD to detect
                            # when the user stops speaking — sending True here
                            # ends the Gemini session permanently.
                            await gemini.send(
                                input=types.Blob(
                                    data=audio_bytes,
                                    mime_type="audio/pcm;rate=16000",
                                ),
                                end_of_turn=False,
                            )

                        elif mtype == "text":
                            # Text input is a complete turn by nature
                            await gemini.send(
                                input=types.Content(
                                    parts=[types.Part(text=msg.get("data", ""))],
                                    role="user",
                                ),
                                end_of_turn=True,
                            )

                except Exception as e:
                    log.debug(f"b2g ended: {e}")
                finally:
                    done.set()

            # ── Gemini → browser ──────────────────────────────────────────
            async def gemini_to_browser():
                try:
                    async for response in gemini.receive():
                        if done.is_set():
                            break

                        # ── GoAway: Gemini is about to close this session ─
                        if response.go_away:
                            log.info(f"Gemini GoAway for [{agent_id}] — will auto-reconnect")
                            await _send(ws, {"type": "reconnecting",
                                             "agent": agent_public_info(agent)})
                            break

                        # ── Raw audio chunk ───────────────────────────────
                        if response.data:
                            await _send(ws, {
                                "type": "audio",
                                "data": base64.b64encode(response.data).decode(),
                            })

                        # ── Server content (transcripts, model turn) ──────
                        sc = response.server_content
                        if sc:
                            if sc.output_transcription and sc.output_transcription.text:
                                text = sc.output_transcription.text.strip()
                                if text:
                                    await _send(ws, {
                                        "type": "transcript",
                                        "speaker": "agent",
                                        "agent_id": agent_id,
                                        "text": text,
                                    })
                                    asyncio.create_task(bq.log_message(
                                        session_id, user["id"], "agent", agent_id, text
                                    ))
                                    # Track for reconnect context — merge consecutive agent chunks
                                    log = session_state["conversation_log"]
                                    if log and log[-1]["speaker"] == "agent":
                                        log[-1]["text"] += " " + text
                                    else:
                                        log.append({"speaker": "agent", "text": text})

                            if sc.input_transcription and sc.input_transcription.text:
                                text = sc.input_transcription.text.strip()
                                if text:
                                    await _send(ws, {
                                        "type": "transcript",
                                        "speaker": "user",
                                        "agent_id": agent_id,
                                        "text": text,
                                    })
                                    asyncio.create_task(bq.log_message(
                                        session_id, user["id"], "user", agent_id, text
                                    ))
                                    # Track for reconnect context — merge consecutive user chunks
                                    log = session_state["conversation_log"]
                                    if log and log[-1]["speaker"] == "user":
                                        log[-1]["text"] += " " + text
                                    else:
                                        log.append({"speaker": "user", "text": text})

                        # ── Tool / function calls ─────────────────────────
                        if response.tool_call:
                            for fc in response.tool_call.function_calls:
                                result = await execute_tool(
                                    fc.name, dict(fc.args) if fc.args else {}, ws, session_state
                                )
                                # Always ACK the tool call back to Gemini
                                try:
                                    await gemini.send(
                                        input=types.LiveClientToolResponse(
                                            function_responses=[types.FunctionResponse(
                                                id=fc.id,
                                                name=fc.name,
                                                response=result,
                                            )]
                                        )
                                    )
                                except Exception as e:
                                    log.warning(f"Tool ACK failed: {e}")

                            # If transfer was just set, end this session
                            if session_state["transfer"]:
                                done.set()
                                break

                except Exception as e:
                    log.error(f"g2b error [{agent_id}]: {type(e).__name__}: {e}", exc_info=True)
                else:
                    # receive() exhausted normally = Gemini closed session (timeout/limit)
                    log.info(f"Gemini session closed normally for [{agent_id}] — will reconnect")
                finally:
                    done.set()

            b2g = asyncio.create_task(browser_to_gemini())
            g2b = asyncio.create_task(gemini_to_browser())

            # Wait until either task signals done (disconnect / transfer / error)
            await done.wait()

            b2g.cancel()
            g2b.cancel()
            await asyncio.gather(b2g, g2b, return_exceptions=True)

    except Exception as e:
        log.error(f"Gemini session error [{agent_id}]: {e}", exc_info=True)
        await _send(ws, {"type": "error", "message": f"Voice error: {e}"})

    return {
        "transfer":             session_state["transfer"],
        "browser_disconnected": session_state["browser_disconnected"],
        "conversation_log":     session_state["conversation_log"],
    }


# ── Top-level WebSocket handler ─────────────────────────────────────────────

async def handle_websocket(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())

    try:
        # Auth handshake
        raw  = await asyncio.wait_for(ws.receive_text(), timeout=15)
        init = json.loads(raw)

        user_id = init.get("user_id", "").strip().lower()
        token   = init.get("token", "")
        user    = verify_token(user_id, token)

        if not user:
            await _send(ws, {"type": "error", "message": "Authentication failed"})
            await ws.close()
            return

        initial_agent_id = init.get("agent_id", "cora")

        # Load BQ context (fire-and-forget)
        context = await bq.get_user_context(user_id)
        orders  = await bq.get_user_orders(user_id)
        if orders:
            lines = [f"{o.get('product_name', o['sku'])} — ${o['price_paid']} ({o['status']})"
                     for o in orders]
            context["recent_orders"] = "\n".join(lines)

        asyncio.create_task(bq.upsert_user(user_id, user["name"], user["email"], user["loyalty_tier"]))
        asyncio.create_task(bq.log_session_start(session_id, user_id, initial_agent_id))

        # Tell browser we're ready
        await ws.send_json({
            "type":       "ready",
            "user":       {"id": user_id, "name": user["name"], "loyalty_tier": user["loyalty_tier"]},
            "agent":      agent_public_info(AGENTS[initial_agent_id]),
            "session_id": session_id,
        })

        # Agent session loop — restarts on transfer OR Gemini timeout/go_away.
        # Only exits when the browser WebSocket actually closes.
        current_agent_id = initial_agent_id
        transfer_summary = ""
        reconnect_delay  = 1.0   # seconds, doubles on repeated reconnects (max 8s)
        reconnect_count  = 0     # guard against infinite loops on persistent API errors
        full_log = []            # accumulates conversation across all Gemini sessions

        while True:
            result   = await run_agent_session(
                ws, user, current_agent_id, session_id, context, transfer_summary
            )
            transfer         = result.get("transfer")
            browser_gone     = result.get("browser_disconnected", False)
            full_log.extend(result.get("conversation_log", []))

            # ── Browser closed the tab / connection ──────────────────────────
            if browser_gone:
                log.info("Browser disconnected — ending session loop")
                break

            # ── Agent requested a transfer ────────────────────────────────────
            if transfer:
                next_id = transfer["to"]
                if next_id not in AGENTS:
                    log.warning(f"Unknown transfer target: {next_id}")
                    break

                asyncio.create_task(bq.log_handoff(
                    session_id, current_agent_id, next_id, transfer["reason"]
                ))
                await ws.send_json({
                    "type":       "agent_changed",
                    "from_agent": current_agent_id,
                    "agent":      agent_public_info(AGENTS[next_id]),
                    "reason":     transfer["reason"],
                })

                current_agent_id = next_id
                transfer_summary = transfer.get("summary", "")
                reconnect_delay  = 1.0   # reset backoff after a successful transfer
                reconnect_count  = 0
                continue

            # ── Gemini session expired/closed — browser is still alive ────────
            reconnect_count += 1
            if reconnect_count > 10:
                log.error(f"Too many reconnects for [{current_agent_id}] — giving up")
                await _send(ws, {"type": "error",
                                 "message": "Voice session could not be restored. Please refresh the page."})
                break

            alive = await _ws_alive(ws)
            if not alive:
                log.info("Browser WS gone after Gemini close — ending")
                break

            log.info(f"Auto-reconnecting Gemini session for [{current_agent_id}] "
                     f"(attempt={reconnect_count}, delay={reconnect_delay:.1f}s)")
            await _send(ws, {
                "type":  "reconnecting",
                "agent": agent_public_info(AGENTS[current_agent_id]),
            })
            await asyncio.sleep(reconnect_delay)
            reconnect_delay = min(reconnect_delay * 2, 8.0)

            # Build reconnect context — keep it short to avoid oversized prompts
            if full_log:
                # Last 8 turns max, truncate each to 120 chars
                recent = full_log[-8:]
                lines = [
                    f"{'Customer' if e['speaker'] == 'user' else 'Agent'}: {e['text'][:120]}"
                    for e in recent
                ]
                transfer_summary = (
                    "RECONNECT — voice session refreshed. "
                    "DO NOT greet again. Continue the conversation naturally.\n"
                    "Recent context:\n" + "\n".join(lines)
                )
            else:
                transfer_summary = "RECONNECT — session refreshed. Continue naturally without re-introducing yourself."

    except WebSocketDisconnect:
        pass
    except asyncio.TimeoutError:
        await _send(ws, {"type": "error", "message": "Auth handshake timed out"})
    except Exception as e:
        log.exception(f"WS handler error: {e}")
    finally:
        asyncio.create_task(bq.log_session_end(session_id))
