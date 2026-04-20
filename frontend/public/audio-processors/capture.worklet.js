// Microphone capture AudioWorklet — buffers PCM16 at 16kHz for Gemini Live API
class AudioCaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._buffer = new Float32Array(4096);
    this._bufferIndex = 0;
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || !input[0]) return true;

    const channel = input[0];
    for (let i = 0; i < channel.length; i++) {
      this._buffer[this._bufferIndex++] = channel[i];
      if (this._bufferIndex === this._buffer.length) {
        this.port.postMessage(this._buffer.slice());
        this._bufferIndex = 0;
      }
    }
    return true;
  }
}

registerProcessor('audio-capture-processor', AudioCaptureProcessor);
