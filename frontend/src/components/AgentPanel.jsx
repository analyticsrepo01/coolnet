import { useEffect, useRef, useState, useCallback } from 'react'

const TIER_COLORS = {
  platinum: 'bg-purple-100 text-purple-700',
  gold:     'bg-yellow-100 text-yellow-700',
  silver:   'bg-gray-100 text-gray-600',
  bronze:   'bg-orange-100 text-orange-700',
}

const TIER_ICONS = { platinum: '★★★', gold: '★★', silver: '★', bronze: '' }

export default function AgentPanel({
  agent, user, transcript, micEnabled, volume,
  onToggleMic, onVolumeChange, onDisconnect, onSendText, isSpeaking, transitioning,
}) {
  const transcriptRef = useRef(null)
  const [textInput, setTextInput] = useState('')

  const handleSendText = useCallback((e) => {
    e.preventDefault()
    const msg = textInput.trim()
    if (!msg) return
    onSendText?.(msg)
    setTextInput('')
  }, [textInput, onSendText])

  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight
    }
  }, [transcript])

  const tierColor = TIER_COLORS[user?.loyalty_tier] || TIER_COLORS.bronze
  const tierIcon  = TIER_ICONS[user?.loyalty_tier] || ''

  return (
    <div className="flex flex-col h-full bg-white border-r border-gray-100">

      {/* Agent avatar */}
      <div className="flex flex-col items-center pt-8 pb-4 px-4">
        <div className="relative mb-3">
          {/* Speaking ring */}
          {isSpeaking && (
            <div
              className="absolute inset-0 rounded-full animate-ping opacity-30"
              style={{ backgroundColor: agent?.color || '#0D5C6E', transform: 'scale(1.15)' }}
            />
          )}
          {/* Avatar image */}
          <div
            className="relative w-36 h-36 rounded-full overflow-hidden border-4 transition-all duration-500"
            style={{
              borderColor: agent?.color || '#0D5C6E',
              opacity: transitioning ? 0 : 1,
              transform: transitioning ? 'scale(0.9)' : 'scale(1)',
            }}
          >
            {agent?.avatar ? (
              <img
                src={agent.avatar}
                alt={agent.name}
                className="w-full h-full object-cover"
                onError={e => { e.target.style.display = 'none' }}
              />
            ) : (
              <div
                className="w-full h-full flex items-center justify-center text-4xl text-white font-bold"
                style={{ backgroundColor: agent?.color || '#0D5C6E' }}
              >
                {agent?.name?.[0] || '?'}
              </div>
            )}
          </div>

          {/* Speaking indicator dot */}
          <div
            className="absolute bottom-2 right-2 w-4 h-4 rounded-full border-2 border-white transition-colors duration-300"
            style={{ backgroundColor: isSpeaking ? '#22c55e' : '#d1d5db' }}
          />
        </div>

        {/* Agent name + role */}
        <div
          className="transition-all duration-500"
          style={{ opacity: transitioning ? 0 : 1 }}
        >
          <h2 className="text-xl font-bold text-gray-800 text-center">{agent?.name || '...'}</h2>
          <p className="text-sm text-gray-500 text-center">{agent?.title || ''}</p>
          {agent?.specialty && (
            <p className="text-xs text-center mt-1" style={{ color: agent.color }}>
              {agent.specialty}
            </p>
          )}
          {agent?.role === 'manager' && (
            <div className="flex justify-center mt-1">
              <span className="text-xs bg-yellow-50 text-yellow-700 border border-yellow-200 rounded-full px-2 py-0.5">
                👑 General Manager
              </span>
            </div>
          )}
          {agent?.role === 'supervisor' && (
            <div className="flex justify-center mt-1">
              <span className="text-xs bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-2 py-0.5">
                🔷 Supervisor
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Divider */}
      <div className="mx-4 border-t border-gray-100" />

      {/* Transcript */}
      <div ref={transcriptRef} className="flex-1 overflow-y-auto px-4 py-3 space-y-2 min-h-0">
        {transcript.length === 0 ? (
          <p className="text-gray-400 text-sm text-center mt-4 italic">
            Start speaking to begin...
          </p>
        ) : (
          transcript.map((msg, i) => {
            const time = new Date(msg.ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
            return (
              <div
                key={i}
                className={`flex flex-col gap-0.5 ${msg.speaker === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm leading-snug ${
                    msg.speaker === 'user'
                      ? 'bg-brand text-white rounded-br-sm'
                      : msg.speaker === 'system'
                      ? 'bg-yellow-50 text-yellow-800 text-xs italic w-full text-center rounded-xl'
                      : 'bg-gray-100 text-gray-800 rounded-bl-sm'
                  }`}
                >
                  {msg.speaker === 'agent' && (
                    <span className="text-xs font-semibold block mb-0.5" style={{ color: agent?.color }}>
                      {msg.agent_name || agent?.name}
                    </span>
                  )}
                  {msg.text}
                </div>
                {msg.speaker !== 'system' && (
                  <span className="text-xs text-gray-400 px-1">{time}</span>
                )}
              </div>
            )
          })
        )}
      </div>

      {/* Controls */}
      <div className="px-4 py-4 border-t border-gray-100">
        {/* User info */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-brand flex items-center justify-center text-white text-xs font-bold">
              {user?.name?.[0] || '?'}
            </div>
            <div>
              <p className="text-xs font-medium text-gray-700">{user?.name}</p>
              <span className={`text-xs rounded-full px-2 py-0.5 ${tierColor}`}>
                {tierIcon} {user?.loyalty_tier}
              </span>
            </div>
          </div>
          <button
            onClick={onDisconnect}
            className="text-xs text-gray-400 hover:text-red-500 transition"
          >
            Disconnect
          </button>
        </div>

        {/* Mic toggle */}
        <button
          onClick={onToggleMic}
          className={`w-full flex items-center justify-center gap-2 rounded-xl py-2.5 font-medium text-sm transition-all duration-200 ${
            micEnabled
              ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100'
              : 'bg-brand text-white hover:bg-brand-light'
          }`}
        >
          <span className="text-lg">{micEnabled ? '🎙️' : '🔇'}</span>
          {micEnabled ? 'Mic On — Click to Mute' : 'Click to Speak'}
        </button>

        {/* Volume */}
        <div className="flex items-center gap-2 mt-2">
          <span className="text-sm">🔊</span>
          <input
            type="range" min="0" max="1" step="0.05" value={volume}
            onChange={e => onVolumeChange(parseFloat(e.target.value))}
            className="flex-1 accent-brand"
          />
        </div>

        {/* Text input fallback */}
        <form onSubmit={handleSendText} className="flex gap-2 mt-3">
          <input
            type="text"
            value={textInput}
            onChange={e => setTextInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 text-xs border border-gray-200 rounded-xl px-3 py-2 focus:outline-none focus:ring-1 focus:ring-brand text-gray-800"
          />
          <button
            type="submit"
            disabled={!textInput.trim()}
            className="text-xs px-3 py-2 bg-brand text-white rounded-xl disabled:opacity-40 hover:bg-brand-light transition"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  )
}
