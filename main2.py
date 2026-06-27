import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
import edge_tts
import pygame
import tempfile
import os
import string

class SimpleTTSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Edge TTS - Instant Player")
        self.root.geometry("1920x1200")
        self.root.attributes('-fullscreen', True)
        self.root.configure(padx=20, pady=20)

        # Apply a clean, modern theme
        style = ttk.Style(self.root)
        if 'clam' in style.theme_names():
            style.theme_use('clam')

        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=5)
        style.configure('TLabel', font=('Segoe UI', 10))

        # UI Header
        ttk.Label(root, text="🎙️ Edge TTS Player", font=('Segoe UI', 16, 'bold')).pack(anchor="w", pady=(0, 15))

        # Voice Dropdown
        voice_frame = ttk.Frame(root)
        voice_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(voice_frame, text="Select Voice:").pack(side="left", padx=(0, 10))

        self.voice_var = tk.StringVar()
        self.voice_cb = ttk.Combobox(voice_frame, textvariable=self.voice_var, state="readonly")
        self.voice_cb.pack(side="left", fill="x", expand=True)
        self.voice_cb.set("Fetching voices...")

        # Text Box
        ttk.Label(root, text="Enter Text:").pack(anchor="w", pady=(0, 5))
        self.text_area = tk.Text(root, height=8, font=('Segoe UI', 11), wrap="word", relief="flat", borderwidth=1)
        self.text_area.pack(fill="both", expand=True, pady=(0, 15))

        self.text_area.bind("<KeyRelease>", self.counting)

        # Controls
        bottom_frame = ttk.Frame(root)
        bottom_frame.pack(fill="x")

        self.play_btn = ttk.Button(bottom_frame, text="▶ Play Right Now", command=self.on_play)
        self.play_btn.pack(side="left")

        self.status = ttk.Label(bottom_frame, text="Ready", foreground="gray")
        self.status.pack(side="left", padx=15)


        self.char_label = ttk.Label(root, text="Characters: 0")
        self.char_label.pack(pady=(0, 15))


        self.words_label = ttk.Label(root, text="Words: 0")
        self.words_label.pack(pady=(0, 15))


        self.numbers_label = ttk.Label(root, text="Numbers: 0")
        self.numbers_label.pack(pady=(0,15))


        self.typographical_label = ttk.Label(root, text="Punctuation marks: 0")
        self.typographical_label.pack(pady=(0, 15))


        # Initialize Audio Mixer
        pygame.mixer.init()
        self.voices_dict = {}

        # Load voices in background so the UI doesn't freeze
        threading.Thread(target=self.load_voices_thread, daemon=True).start()

    def counting(self, event=None):
        content = self.text_area.get("1.0", "end-1c")
        self.char_label.config(text=f"Characters: {len(content)}")
        self.words_label.config(text=f"Words: {len(content.split())}")
        count = 0
        for c in content:
            if c >= '0' and c <= '9':
                count += 1
        self.numbers_label.config(text=f"Numbers: {count}")
        count_punctuation = 0
        for ch in content:
            if ch in string.punctuation:
                count_punctuation += 1
        self.typographical_label.config(text=f"Punctuation marks: {count_punctuation}")
    def load_voices_thread(self):
        asyncio.run(self.fetch_voices())

    async def fetch_voices(self):
        try:
            voices = await edge_tts.list_voices()
            # Format: "ShortName - Locale (Gender)"
            self.voices_dict = {f"{v['ShortName']} - {v['Locale']} ({v['Gender']})": v['ShortName'] for v in voices}
            self.root.after(0, self.update_ui_voices)
        except Exception as e:
            self.root.after(0, lambda: self.status.config(text=f"Error: {e}"))

    def update_ui_voices(self):
        voice_names = sorted(self.voices_dict.keys())
        self.voice_cb['values'] = voice_names
        if voice_names:
            # Default to a natural-sounding English voice if available
            default = next((v for v in voice_names if "en-US-Aria" in v), voice_names[0])
            self.voice_cb.set(default)

    def on_play(self):
        text = self.text_area.get("1.0", tk.END).strip()
        voice_display = self.voice_var.get()

        if not text:
            messagebox.showwarning("No Text", "Please enter some text to read out loud.")
            return
        if voice_display not in self.voices_dict:
            messagebox.showwarning("Voice Error", "Please wait for voices to load or select a valid voice.")
            return

        short_name = self.voices_dict[voice_display]
        self.play_btn.config(state="disabled")
        self.status.config(text="Generating audio...")

        # Spin up a thread to handle audio generation and playback
        threading.Thread(target=self.play_audio_thread, args=(text, short_name), daemon=True).start()

    def play_audio_thread(self, text, voice):
        asyncio.run(self.generate_and_play(text, voice))

    async def generate_and_play(self, text, voice):
        try:
            # Stop any currently playing audio
            pygame.mixer.music.stop()

            # Generate a unique temporary file path
            fd, path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(path)

            self.root.after(0, lambda: self.status.config(text="Playing audio..."))

            # Load and play the temp file via Pygame
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()

            self.root.after(0, lambda: self.status.config(text="Done!"))

        except Exception as e:
            self.root.after(0, lambda: self.status.config(text=f"Error: {e}"))
        finally:
            # Re-enable the button once playback initiates
            self.root.after(0, lambda: self.play_btn.config(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTTSApp(root)
    root.mainloop()