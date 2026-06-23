"""Continuous Voice listener using VAD and faster-whisper."""

import time
import threading
import numpy as np
import pyaudio
from faster_whisper import WhisperModel
from loguru import logger

from .ipc_client import get_ipc_client, start_ipc_client_sync
from .speaker import get_speaker

# Configuration
CHUNK_SIZE = 1280
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 400   # Amplitude threshold for speech detection
SILENCE_DURATION = 1.5    # Seconds of silence to end a spoken phrase
MIN_RECORD_DURATION = 1.0 # Minimum seconds to record to avoid tiny blips
CONTINUOUS_TIMEOUT = 20.0 # Seconds of silence before going back to sleep

class VoiceState:
    SLEEPING = 0
    CONTINUOUS = 1

def listen_and_transcribe():
    """Start the VAD + Whisper continuous listening loop."""
    logger.info("Initializing Voice IPC Client...")
    ipc_thread = threading.Thread(target=start_ipc_client_sync, daemon=True)
    ipc_thread.start()
    
    logger.info("Initializing Faster-Whisper Model...")
    whisper_model = WhisperModel("tiny.en", device="cpu", compute_type="int8")
    
    audio = pyaudio.PyAudio()
    mic_stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    state = VoiceState.SLEEPING
    last_interaction_time = time.time()
    
    logger.info("Listening for wake word 'Hey Sixteen'...")
    
    try:
        while True:
            # Check timeout for continuous mode
            if state == VoiceState.CONTINUOUS and (time.time() - last_interaction_time) > CONTINUOUS_TIMEOUT:
                logger.info("Continuous mode timeout. Going back to sleep...")
                state = VoiceState.SLEEPING
                get_ipc_client().send_state_update("IDLE")

            # Read audio chunk
            pcm_data = mic_stream.read(CHUNK_SIZE, exception_on_overflow=False)
            
            # If Sixteen is currently speaking, completely ignore the microphone to prevent echo loops
            if get_speaker().is_speaking:
                last_interaction_time = time.time()  # Keep continuous mode alive while she speaks
                continue
                
            audio_data = np.frombuffer(pcm_data, dtype=np.int16)
            amplitude = np.max(np.abs(audio_data))
            
            if amplitude > SILENCE_THRESHOLD:
                # Speech detected, begin recording
                if state == VoiceState.SLEEPING:
                    pass # We don't change state until we confirm wake word
                else:
                    get_ipc_client().send_state_update("LISTENING")
                
                recorded_frames = [audio_data]
                silent_chunks = 0
                max_silent_chunks = int((RATE / CHUNK_SIZE) * SILENCE_DURATION)
                min_chunks = int((RATE / CHUNK_SIZE) * MIN_RECORD_DURATION)
                
                # Record loop
                while True:
                    pcm_data = mic_stream.read(CHUNK_SIZE, exception_on_overflow=False)
                    
                    # Again, safety kill-switch if TTS starts speaking mid-recording
                    if get_speaker().is_speaking:
                        break
                        
                    audio_data = np.frombuffer(pcm_data, dtype=np.int16)
                    recorded_frames.append(audio_data)
                    
                    amp = np.max(np.abs(audio_data))
                    if amp < SILENCE_THRESHOLD:
                        silent_chunks += 1
                    else:
                        silent_chunks = 0
                        
                    if len(recorded_frames) > min_chunks and silent_chunks > max_silent_chunks:
                        break
                
                if get_speaker().is_speaking:
                    continue  # Discard recorded buffer because she started talking
                
                logger.info("Transcribing...")
                full_audio = np.concatenate(recorded_frames)
                audio_float32 = full_audio.astype(np.float32) / 32768.0
                
                segments, info = whisper_model.transcribe(audio_float32, beam_size=5)
                transcript = " ".join([segment.text for segment in segments]).strip()
                
                if not transcript:
                    if state == VoiceState.CONTINUOUS:
                        get_ipc_client().send_state_update("IDLE")
                    continue
                    
                text_lower = transcript.lower()
                logger.success(f"Heard: {transcript}")
                
                if state == VoiceState.SLEEPING:
                    # Look for wake word
                    if "sixteen" in text_lower or "16" in text_lower:
                        logger.success("Wake word detected! Entering continuous conversation mode.")
                        state = VoiceState.CONTINUOUS
                        last_interaction_time = time.time()
                        
                        # Check if they said a command immediately after the wake word
                        # E.g. "Hey Sixteen what time is it"
                        # We will send the full transcript; Sixteen's LLM is smart enough to handle it
                        get_ipc_client().send_voice_input(transcript)
                        get_ipc_client().send_state_update("THINKING")
                
                elif state == VoiceState.CONTINUOUS:
                    # In continuous mode, every spoken phrase is sent directly
                    last_interaction_time = time.time()
                    get_ipc_client().send_voice_input(transcript)
                    get_ipc_client().send_state_update("THINKING")

    except KeyboardInterrupt:
        logger.info("Shutting down voice listener.")
    finally:
        mic_stream.stop_stream()
        mic_stream.close()
        audio.terminate()

if __name__ == "__main__":
    listen_and_transcribe()
