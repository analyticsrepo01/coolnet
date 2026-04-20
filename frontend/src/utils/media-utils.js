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
