import { useState, useEffect, useRef, useCallback } from 'react'
import LoginScreen from './components/LoginScreen.jsx'
import AgentPanel from './components/AgentPanel.jsx'
import CatalogPanel from './components/CatalogPanel.jsx'
import { CoolNestSession } from './utils/coolnest-ws.js'
import { AudioStreamer, AudioPlayer } from './utils/media-utils.js'

export default function App() {
  const [user, setUser]                   = useState(null)
  const [agent, setAgent]                 = useState(null)
  const [connected, setConnected]         = useState(false)
  const [connecting, setConnecting]       = useState(false)
  const [micEnabled, setMicEnabled]       = useState(false)
  const [volume, setVolume]               = useState(0.8)
  const [transcript, setTranscript]       = useState([])
  const [agentSpeaking, setAgentSpeaking] = useState(false)
  const [transitioning, setTransitioning] = useState(false)
  const [catalogState, setCatalogState]   = useState(null)
  const [cart, setCart]                   = useState([])
  const [error, setError]                 = useState('')
  const [reconnecting, setReconnecting]   = useState(false)

  const sessionRef   = useRef(null)
  const streamerRef  = useRef(null)
  const playerRef    = useRef(new AudioPlayer())
  const speakTimer   = useRef(null)
  // Track current agent in a ref so callbacks always see the latest value
  const agentRef     = useRef(null)

  // ── Transcript helper ─────────────────────────────────────────────────────
  // Gemini streams transcription word-by-word; merge consecutive chunks from the
  // same speaker within 5 seconds into one bubble instead of creating new entries.
  const addTranscript = useCallback((speaker, agentInfo, text) => {
    if (!text?.trim()) return
    setTranscript(prev => {
      const last = prev[prev.length - 1]
      if (last && last.speaker === speaker && last.speaker !== 'system' && Date.now() - last.ts < 5000) {
        const merged = { ...last, text: last.text + ' ' + text.trim(), ts: Date.now() }
        return [...prev.slice(0, -1), merged]
      }
      return [...prev.slice(-120), {
        speaker, text: text.trim(), agent_name: agentInfo?.name, ts: Date.now(),
      }]
    })
  }, [])

  // ── Agent switch animation ────────────────────────────────────────────────
  const switchAgent = useCallback((newAgent) => {
    setTransitioning(true)
    setTimeout(() => {
      agentRef.current = newAgent
      setAgent(newAgent)
      setTransitioning(false)
      addTranscript('system', null, `— Transferred to ${newAgent.name} (${newAgent.title}) —`)
    }, 400)
  }, [addTranscript])

  // ── Start mic (internal — always-on continuous stream) ────────────────────
  const startMic = useCallback(async () => {
    if (streamerRef.current) return   // already running
    try {
      const streamer = new AudioStreamer((chunk) => {
        sessionRef.current?.sendAudio(chunk)
      })
      await streamer.start()
      streamerRef.current = streamer
      setMicEnabled(true)
    } catch (e) {
      setError('Mic access denied — please allow microphone permission and refresh.')
    }
  }, [])

  const stopMic = useCallback(() => {
    streamerRef.current?.stop()
    streamerRef.current = null
    setMicEnabled(false)
    // NOTE: do NOT send end_of_turn — the Gemini native audio model uses
    // built-in VAD to detect speech boundaries. Sending end_of_turn=true
    // permanently closes the Gemini session.
  }, [])

  // ── Mic toggle (user-facing mute/unmute) ─────────────────────────────────
  const toggleMic = useCallback(async () => {
    if (micEnabled) {
      stopMic()
    } else {
      await startMic()
      // Interrupt agent if speaking when user wants to talk
      playerRef.current.interrupt()
    }
  }, [micEnabled, startMic, stopMic])

  // ── Audio received from agent ─────────────────────────────────────────────
  const onAudioReceived = useCallback(async (b64) => {
    setAgentSpeaking(true)
    clearTimeout(speakTimer.current)
    speakTimer.current = setTimeout(() => setAgentSpeaking(false), 1000)
    await playerRef.current.playChunk(b64)
  }, [])

  // ── Connect + auto-start mic after ready ─────────────────────────────────
  const connect = useCallback((loggedInUser) => {
    setConnecting(true)
    setError('')

    const sess = new CoolNestSession({
      userId: loggedInUser.id,
      token:  loggedInUser.token,

      onReady: async (msg) => {
        agentRef.current = msg.agent
        setAgent(msg.agent)
        setConnected(true)
        setConnecting(false)
        setReconnecting(false)
        addTranscript('system', null, `Hi ${loggedInUser.name}! Connected to ${msg.agent.name} — listening...`)
        // Auto-start mic — startMic() is idempotent (no-op if already running)
        await startMic()
      },

      onAgentChanged: (msg) => {
        switchAgent(msg.agent)
      },

      onCatalogAction: (msg) => {
        setCatalogState({ ...msg, _ts: Date.now() })
      },

      onTranscript: (msg) => {
        addTranscript(
          msg.speaker,
          msg.speaker === 'agent' ? agentRef.current : null,
          msg.text,
        )
      },

      onAudio: onAudioReceived,

      onSystemMessage: (text) => {
        addTranscript('system', null, text)
      },

      onError: (msg) => {
        setError(msg)
        setConnecting(false)
      },

      onReconnecting: (newAgent) => {
        // Gemini session expired server-side — keep mic running, show status
        setReconnecting(true)
        if (newAgent) {
          agentRef.current = newAgent
          setAgent(newAgent)
        }
      },

      onDisconnect: () => {
        // Only fires when the browser WebSocket actually closes
        setConnected(false)
        setReconnecting(false)
        stopMic()
        addTranscript('system', null, 'Session ended.')
      },
    })

    sessionRef.current = sess
    sess.connect()
  }, [addTranscript, onAudioReceived, startMic, stopMic, switchAgent])

  // ── Login ─────────────────────────────────────────────────────────────────
  const handleLogin = useCallback((loggedInUser) => {
    setUser(loggedInUser)
    connect(loggedInUser)
  }, [connect])

  // ── Send text ─────────────────────────────────────────────────────────────
  const handleSendText = useCallback((text) => {
    sessionRef.current?.sendText(text)
    addTranscript('user', null, text)
  }, [addTranscript])

  // ── Cart management ───────────────────────────────────────────────────────
  const handleAddToCart = useCallback((product, quantity = 1) => {
    setCart(prev => {
      const existing = prev.find(i => i.product.sku === product.sku)
      if (existing) {
        return prev.map(i => i.product.sku === product.sku
          ? { ...i, quantity: i.quantity + quantity } : i)
      }
      return [...prev, { product, quantity }]
    })
  }, [])

  const handleUpdateCartQty = useCallback((sku, delta) => {
    setCart(prev =>
      prev.map(i => i.product.sku === sku ? { ...i, quantity: Math.max(0, i.quantity + delta) } : i)
          .filter(i => i.quantity > 0)
    )
  }, [])

  const handleRemoveFromCart = useCallback((sku) => {
    setCart(prev => prev.filter(i => i.product.sku !== sku))
  }, [])

  const handleClearCart = useCallback(() => setCart([]), [])

  // ── Product selected by user in catalog ──────────────────────────────────
  const handleProductSelect = useCallback((product) => {
    sessionRef.current?.sendText(
      `[The customer just opened the detail page for: ${product.name} (SKU: ${product.sku}, Price: $${product.price}). Please acknowledge this product and offer to describe its features or answer questions about it.]`
    )
  }, [])

  // ── Volume ────────────────────────────────────────────────────────────────
  const handleVolume = useCallback((v) => {
    setVolume(v)
    playerRef.current.setVolume(v)
  }, [])

  // ── Disconnect ────────────────────────────────────────────────────────────
  const handleDisconnect = useCallback(() => {
    stopMic()
    sessionRef.current?.disconnect()
    sessionRef.current = null
    playerRef.current.destroy()
    playerRef.current = new AudioPlayer()
    setConnected(false)
    setAgent(null)
    agentRef.current = null
    setUser(null)
    setTranscript([])
    setCatalogState(null)
    setError('')
  }, [stopMic])

  // Cleanup on unmount
  useEffect(() => () => {
    stopMic()
    sessionRef.current?.disconnect()
    playerRef.current.destroy()
  }, [stopMic])

  // ── Render ────────────────────────────────────────────────────────────────
  if (!user) {
    return <LoginScreen onLogin={handleLogin} />
  }

  return (
    <div className="flex flex-col h-screen overflow-hidden" style={{ background: '#f0f4f5' }}>

      {/* Header */}
      <header className="flex items-center justify-between px-6 py-3 text-white shadow-sm flex-shrink-0"
              style={{ background: '#0D5C6E' }}>
        <div className="flex items-center gap-3">
          <span className="text-2xl">🏠</span>
          <div>
            <span className="font-bold text-lg tracking-tight">CoolNest</span>
            <span className="ml-2 text-xs opacity-70">Smart Appliances, Smarter Prices</span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {connecting && <span className="text-xs opacity-80 animate-pulse">Connecting...</span>}
          {reconnecting && (
            <span className="flex items-center gap-1.5 text-xs opacity-80 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-yellow-400" />
              Refreshing session...
            </span>
          )}
          {connected && !reconnecting && (
            <span className="flex items-center gap-1.5 text-xs">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              {micEnabled ? 'Listening' : 'Muted'}
            </span>
          )}
          {error && (
            <span className="text-xs bg-red-500/20 text-red-200 px-2 py-1 rounded-lg max-w-xs truncate" title={error}>
              ⚠ {error}
            </span>
          )}
        </div>
      </header>

      {/* Main */}
      <div className="flex flex-1 overflow-hidden">
        <div className="w-80 flex-shrink-0 overflow-hidden">
          <AgentPanel
            agent={agent}
            user={user}
            transcript={transcript}
            micEnabled={micEnabled}
            volume={volume}
            isSpeaking={agentSpeaking}
            transitioning={transitioning}
            onToggleMic={toggleMic}
            onVolumeChange={handleVolume}
            onDisconnect={handleDisconnect}
            onSendText={handleSendText}
          />
        </div>
        <div className="flex-1 overflow-hidden">
          <CatalogPanel
            catalogState={catalogState}
            agentColor={agent?.color}
            onProductSelect={handleProductSelect}
            cart={cart}
            user={user}
            onAddToCart={handleAddToCart}
            onUpdateCartQty={handleUpdateCartQty}
            onRemoveFromCart={handleRemoveFromCart}
            onClearCart={handleClearCart}
          />
        </div>
      </div>
    </div>
  )
}
