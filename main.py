import asyncio
import edge_tts
import os

TEXT = "Hello! I'm a bot written from Python. I don't like GitHub"
VOICE = "en-SG-LunaNeural"
OUTPUT_FILE = "speech.mp3"


async def generate_speech() -> None:
    # Initialize the TTS stream
    communicate = edge_tts.Communicate(TEXT, VOICE)

    # Save the generated audio to a local file
    await communicate.save(OUTPUT_FILE)
    print(f"Audio successfully saved to {OUTPUT_FILE}")
    os.startfile(OUTPUT_FILE)


if __name__ == "__main__":
    # Execute the asynchronous function
    asyncio.run(generate_speech())
