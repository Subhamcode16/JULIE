"""Text-to-speech integration for Julie using Kokoro ONNX."""

import os
import queue
import threading
import requests
import sounddevice as sd
from loguru import logger
from kokoro_onnx import Kokoro

# Configuration
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
MODEL_PATH = "kokoro-v1.0.onnx"
VOICES_PATH = "voices-v1.0.bin"
VOICE_NAME = "af_bella"  # A highly expressive, warm, and natural voice

class JulieSpeaker:
    def __init__(self):
        self._ensure_models()
        self.kokoro = Kokoro(MODEL_PATH, VOICES_PATH)
        self.tts_queue = queue.Queue()
        self.is_speaking = False
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def _ensure_models(self):
        if not os.path.exists(MODEL_PATH):
            logger.info("Downloading Kokoro ONNX model (this may take a minute)...")
            self._download_file(MODEL_URL, MODEL_PATH)
        if not os.path.exists(VOICES_PATH):
            logger.info("Downloading voices.json...")
            self._download_file(VOICES_URL, VOICES_PATH)

    def _download_file(self, url, dest):
        r = requests.get(url, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    def _worker_loop(self):
        logger.info("Speaker queue worker started.")
        while True:
            text = self.tts_queue.get()
            if text is None:
                break
            
            try:
                samples, sample_rate = self.kokoro.create(
                    text, voice=VOICE_NAME, speed=1.1, lang="en-us"
                )
                logger.info("Speaking...")
                self.is_speaking = True
                sd.play(samples, sample_rate)
                sd.wait()
                self.is_speaking = False
            except Exception as e:
                logger.error(f"TTS Error: {e}")
            finally:
                self.tts_queue.task_done()

    def speak(self, text: str):
        """Queue text to be spoken."""
        self.tts_queue.put(text)

# Singleton instance
_speaker_instance = None

def get_speaker() -> JulieSpeaker:
    global _speaker_instance
    if _speaker_instance is None:
        _speaker_instance = JulieSpeaker()
    return _speaker_instance

def speak(text: str):
    """Queue text to be spoken."""
    get_speaker().speak(text)

if __name__ == "__main__":
    speak("Hello, I am Julie. How can I help you today?")
    # Wait for the queue to finish processing the test
    get_speaker().tts_queue.join()
