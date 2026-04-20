// PCM16 audio playback AudioWorklet — plays 24kHz audio from Gemini Live API
class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this._queue = [];
    this._offset = 0;
    this.port.onmessage = (e) => {
      if (e.data === 'interrupt') {
        this._queue = [];
        this._offset = 0;
      } else {
        this._queue.push(e.data);
      }
    };
  }

  process(_, outputs) {
    const output = outputs[0][0];
    if (!output) return true;

    let written = 0;
    while (written < output.length && this._queue.length > 0) {
      const buf = this._queue[0];
      const remaining = buf.length - this._offset;
      const toCopy = Math.min(remaining, output.length - written);
      output.set(buf.subarray(this._offset, this._offset + toCopy), written);
      written += toCopy;
      this._offset += toCopy;
      if (this._offset >= buf.length) {
        this._queue.shift();
        this._offset = 0;
      }
    }
    // Fill remaining with silence
    for (let i = written; i < output.length; i++) output[i] = 0;
    return true;
  }
}

registerProcessor('pcm-processor', PCMProcessor);
