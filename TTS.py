import pyttsx3
import customtkinter as ctk
from PIL import Image
from tkinter import messagebox
import os
from googletrans import Translator

# Optional: database logging
try:
    from tts_database import log_to_db
except ImportError:
    log_to_db = None

# Initialize pyttsx3 engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Translator
translator = Translator()

# Setup CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")  # warm, soft theme

class TTSApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎤 Multilingual TTS Converter")
        self.geometry("1300x750")
        self.configure(fg_color="#fdf6e3")  # warm/light background
        self.images = {}
        self.show_intro()

    def load_image(self, path, size):
        if os.path.exists(path):
            img = ctk.CTkImage(light_image=Image.open(path), size=size)
            self.images[path] = img
            return img
        return None

    def show_intro(self):
        self.intro_frame = ctk.CTkFrame(self, fg_color="#fdf6e3")
        self.intro_frame.pack(expand=True, fill="both")

        logo_img = self.load_image("icons/microphone.png", (160, 160))
        if logo_img:
            ctk.CTkLabel(self.intro_frame, image=logo_img, text="").pack(pady=40)

        ctk.CTkLabel(
            self.intro_frame,
            text="🎤 Multilingual TTS Converter",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="#5c4033"
        ).pack(pady=15)

        ctk.CTkLabel(
            self.intro_frame,
            text="✨ Convert your text into voice in many languages ✨",
            font=ctk.CTkFont(size=24),
            text_color="#5c4033"
        ).pack(pady=10)

        start_btn = ctk.CTkButton(
            self.intro_frame,
            text="🚀 Start",
            font=ctk.CTkFont(size=24),
            command=self.show_main,
            fg_color="#5cb85c",
            hover_color="#4cae4c"
        )
        start_btn.pack(pady=30)

    def show_main(self):
        self.intro_frame.destroy()
        self.main_frame = ctk.CTkFrame(self, fg_color="#fdf6e3")
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=20)

        # Header
        icon_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        icon_frame.pack(pady=20)

        logo_icon = self.load_image("icons/logo.png", (70, 70))
        writing_icon = self.load_image("icons/writing.png", (70, 70))

        if logo_icon:
            ctk.CTkLabel(icon_frame, image=logo_icon, text="").grid(row=0, column=0, padx=20)
        ctk.CTkLabel(icon_frame, text="📝 Enter Text",
                     font=ctk.CTkFont(size=36, weight="bold")).grid(row=0, column=1, padx=20)
        if writing_icon:
            ctk.CTkLabel(icon_frame, image=writing_icon, text="").grid(row=0, column=2, padx=20)

        # Textbox
        self.text_entry = ctk.CTkTextbox(self.main_frame, height=200, font=("Arial", 20),
                                         border_color="gray", border_width=2)
        self.text_entry.pack(pady=20, padx=80, fill="x")

        # Language selection
        self.lang_menu = ctk.CTkOptionMenu(
            self.main_frame,
            values=["English", "Hindi", "Spanish", "French", "German", "Japanese", "Chinese"],
            width=250,
            font=ctk.CTkFont(size=18)
        )
        self.lang_menu.set("English")
        self.lang_menu.pack(pady=15)

        # Voice selection
        self.voice_menu = ctk.CTkOptionMenu(
            self.main_frame,
            values=["Male", "Female"],
            width=200,
            font=ctk.CTkFont(size=18)
        )
        self.voice_menu.set("Male")
        self.voice_menu.pack(pady=15)

        # Speech rate
        ctk.CTkLabel(self.main_frame, text="📈 Speech Rate", font=ctk.CTkFont(size=20)).pack()
        self.rate_slider = ctk.CTkSlider(self.main_frame, from_=100, to=300, number_of_steps=10, width=400)
        self.rate_slider.set(150)
        self.rate_slider.pack(pady=10)

        # Volume
        ctk.CTkLabel(self.main_frame, text="🔊 Volume (Always Max)", font=ctk.CTkFont(size=20)).pack()
        self.volume_slider = ctk.CTkSlider(self.main_frame, from_=0, to=1, width=400)
        self.volume_slider.set(1.0)
        self.volume_slider.configure(state="disabled")
        self.volume_slider.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=40)

        ctk.CTkButton(button_frame, text="🗣️ Speak", command=self.speak_text,
                      width=180, height=50, font=ctk.CTkFont(size=18),
                      fg_color="#0275d8", hover_color="#025aa5").grid(row=0, column=0, padx=20)

        ctk.CTkButton(button_frame, text="❌ Clear", command=self.clear_text,
                      width=180, height=50, font=ctk.CTkFont(size=18),
                      fg_color="#d9534f", hover_color="#c9302c").grid(row=0, column=1, padx=20)

    def speak_text(self):
        text = self.text_entry.get("0.0", "end").strip()
        if not text:
            messagebox.showwarning("Input Required", "Please enter some text first.")
            return

        # Translate text if language selected is not English
        target_lang = self.lang_menu.get().lower()
        translated_text = text
        if target_lang != "english":
            try:
                translated_text = translator.translate(text, dest=target_lang).text
            except Exception as e:
                messagebox.showerror("Translation Error", str(e))
                return

        rate = int(self.rate_slider.get())
        gender = self.voice_menu.get()
        selected_voice = None

        for voice in voices:
            vid = voice.id.lower()
            if gender.lower() == "male" and any(x in vid for x in ["david", "barry", "mark"]):
                selected_voice = voice.id
                break
            elif gender.lower() == "female" and any(x in vid for x in ["zira", "eva", "hazel", "susan", "helen"]):
                selected_voice = voice.id
                break

        if not selected_voice:
            selected_voice = voices[0].id

        try:
            engine.setProperty("voice", selected_voice)
            engine.setProperty("rate", rate)
            engine.setProperty("volume", 1.0)
            engine.say(translated_text)
            engine.runAndWait()
            if log_to_db:
                log_to_db(translated_text, gender, rate, 1.0)
        except Exception as e:
            messagebox.showerror("TTS Error", str(e))

    def clear_text(self):
        self.text_entry.delete("0.0", "end")


if __name__ == "__main__":
    app = TTSApp()
    app.mainloop()
