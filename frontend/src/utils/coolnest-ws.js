/**
 * CoolNest WebSocket client.
 * Manages the connection to the backend /ws endpoint,
 * handles auth handshake, and dispatches typed messages.
 */

export class CoolNestSession {
  constructor({ userId, token, onReady, onAgentChanged, onCatalogAction,
                onTranscript, onAudio, onSystemMessage, onError, onDisconnect,
                onReconnecting }) {
    this.userId = userId;
    this.token = token;
    this.handlers = { onReady, onAgentChanged, onCatalogAction, onTranscript,
                      onAudio, onSystemMessage, onError, onDisconnect, onReconnecting };
    this._ws = null;
  }

  connect() {
    // Build WS URL relative to the current page
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const base = window.location.pathname.replace(/\/?$/, '');
    const url = `${proto}//${window.location.host}${base}/ws`;

    this._ws = new WebSocket(url);

    this._ws.onopen = () => {
      // Send auth init
      this._send({ type: 'init', user_id: this.userId, token: this.token, agent_id: 'cora' });
    };

    this._ws.onmessage = (event) => {
      let msg;
      try { msg = JSON.parse(event.data); } catch { return; }
      this._dispatch(msg);
    };

    this._ws.onerror = (e) => {
      this.handlers.onError?.('WebSocket error');
    };

    this._ws.onclose = () => {
      this.handlers.onDisconnect?.();
    };
  }

  _dispatch(msg) {
    switch (msg.type) {
      case 'ready':           this.handlers.onReady?.(msg); break;
      case 'agent_changed':   this.handlers.onAgentChanged?.(msg); break;
      case 'catalog_action':  this.handlers.onCatalogAction?.(msg); break;
      case 'transcript':      this.handlers.onTranscript?.(msg); break;
      case 'audio':           this.handlers.onAudio?.(msg.data); break;
      case 'system_message':  this.handlers.onSystemMessage?.(msg.text); break;
      case 'error':           this.handlers.onError?.(msg.message); break;
      case 'reconnecting':    this.handlers.onReconnecting?.(msg.agent); break;
      case 'ping':            break; // heartbeat — no action needed
    }
  }

  _send(obj) {
    if (this._ws?.readyState === WebSocket.OPEN) {
      this._ws.send(JSON.stringify(obj));
    }
  }

  sendAudio(base64Chunk) {
    this._send({ type: 'audio', data: base64Chunk });
  }

  sendText(text) {
    this._send({ type: 'text', data: text });
  }

  sendEndOfTurn() {
    this._send({ type: 'end_of_turn' });
  }

  disconnect() {
    this._ws?.close();
    this._ws = null;
  }
}
