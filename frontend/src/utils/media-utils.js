/**
 * Audio capture (mic → PCM16 base64) and playback (PCM16 → speaker).
 * Adapted from Google's Gemini Live API reference app.
 */

// ── AudioStreamer — captures mic at 16kHz ────────────────────────────────────

export class AudioStreamer {
  constructor(onAudioChunk) {
    this.onAudioChunk = onAudioChunk; // callback(base64string)
    this._context = null;
    this._workletNode = null;
    this._source = null;
    this._stream = null;
  }

  async start() {
    this._stream = await navigator.mediaDevices.getUserMedia({
      audio: { sampleRate: 16000, echoCancellation: true, noiseSuppression: true, channelCount: 1 },
    });

    this._context = new AudioContext({ sampleRate: 16000 });
    await this._context.audioWorklet.addModule('./audio-processors/capture.worklet.js');

    this._source = this._context.createMediaStreamSource(this._stream);
    this._workletNode = new AudioWorkletNode(this._context, 'audio-capture-processor');

    this._workletNode.port.onmessage = (e) => {
      const float32 = e.data;
      const pcm16 = floatToPCM16(float32);
      const b64 = arrayBufferToBase64(pcm16.buffer);
      this.onAudioChunk(b64);
    };

    this._source.connect(this._workletNode);
    this._workletNode.connect(this._context.destination);
  }

  stop() {
    this._source?.disconnect();
    this._workletNode?.disconnect();
    this._stream?.getTracks().forEach(t => t.stop());
    this._context?.close();
    this._context = null;
  }
}


// ── AudioPlayer — plays 24kHz PCM16 from Gemini ──────────────────────────────

export class AudioPlayer {
  constructor() {
    this._context = null;
    this._workletNode = null;
    this._gainNode = null;
    this._volume = 1.0;
  }

  async init() {
    this._context = new AudioContext({ sampleRate: 24000 });
    await this._context.audioWorklet.addModule('./audio-processors/playback.worklet.js');
    this._workletNode = new AudioWorkletNode(this._context, 'pcm-processor');
    this._gainNode = this._context.createGain();
    this._gainNode.gain.value = this._volume;
    this._workletNode.connect(this._gainNode);
    this._gainNode.connect(this._context.destination);
  }

  async playChunk(base64Audio) {
    if (!this._context) await this.init();
    if (this._context.state === 'suspended') await this._context.resume();
    const bytes = base64ToUint8(base64Audio);
    const float32 = pcm16ToFloat32(bytes);
    this._workletNode?.port.postMessage(float32);
  }

  interrupt() {
    this._workletNode?.port.postMessage('interrupt');
  }

  setVolume(v) {
    this._volume = v;
    if (this._gainNode) this._gainNode.gain.value = v;
  }

  destroy() {
    this._workletNode?.disconnect();
    this._gainNode?.disconnect();
    this._context?.close();
    this._context = null;
  }
}


// ── UI tones (Web Audio API synthesis — no files needed) ─────────────────────
//
// connect:    two ascending notes  → "you're in"
// transfer:   quick rising chime   → "handing over"
// disconnect: descending fade      → "session closed"

export function playTone(type = 'connect') {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    const master = ctx.createGain()
    master.connect(ctx.destination)
    const now = ctx.currentTime

    const note = (freq, startAt, dur, vol = 0.25, shape = 'sine') => {
      const osc = ctx.createOscillator()
      const env = ctx.createGain()
      osc.type = shape
      osc.frequency.setValueAtTime(freq, startAt)
      env.gain.setValueAtTime(0, startAt)
      env.gain.linearRampToValueAtTime(vol, startAt + 0.02)
      env.gain.exponentialRampToValueAtTime(0.001, startAt + dur)
      osc.connect(env)
      env.connect(master)
      osc.start(startAt)
      osc.stop(startAt + dur)
      return osc
    }

    if (type === 'connect') {
      // C5 → E5 ascending chime
      note(523, now,       0.5)
      note(659, now + 0.18, 0.7)
    } else if (type === 'transfer') {
      // Quick rising two-tone ding
      note(880, now,       0.4, 0.2, 'triangle')
      note(1108, now + 0.15, 0.55, 0.2, 'triangle')
    } else if (type === 'disconnect') {
      // E5 → C5 descending close
      note(659, now,       0.45)
      note(523, now + 0.2,  0.7, 0.2)
    }

    // Close the throw-away context after tones finish
    setTimeout(() => ctx.close(), 1200)
  } catch (_) { /* audio not available */ }
}


// ── Helpers ──────────────────────────────────────────────────────────────────

function floatToPCM16(float32) {
  const pcm = new Int16Array(float32.length);
  for (let i = 0; i < float32.length; i++) {
    const s = Math.max(-1, Math.min(1, float32[i]));
    pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
  }
  return pcm;
}

function pcm16ToFloat32(bytes) {
  const int16 = new Int16Array(bytes.buffer, bytes.byteOffset, bytes.byteLength / 2);
  const float32 = new Float32Array(int16.length);
  for (let i = 0; i < int16.length; i++) {
    float32[i] = int16[i] / (int16[i] < 0 ? 0x8000 : 0x7fff);
  }
  return float32;
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let b of bytes) binary += String.fromCharCode(b);
  return btoa(binary);
}

function base64ToUint8(b64) {
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}
