"""Entry point for Julie's isolated voice process."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from julie.voice.listener import listen_and_transcribe

if __name__ == "__main__":
    try:
        listen_and_transcribe()
    except KeyboardInterrupt:
        print("\nExiting voice process.")
