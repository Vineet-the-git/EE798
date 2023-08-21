import tkinter as tk
from tkinter import ttk, filedialog
import pygame
import threading
import time

class MetronomeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metronome")
        
        self.bpm = tk.IntVar(value=120)
        self.min_bpm = 30
        self.max_bpm = 240
        
        self.slider = ttk.Scale(root, from_=self.min_bpm, to=self.max_bpm, variable=self.bpm, orient="horizontal", length=300, command=self.update_bpm_label)
        self.slider.pack(pady=20)
        
        self.bpm_label = tk.Label(root, text="BPM: {}".format(self.bpm.get()))
        self.bpm_label.pack()
        
        self.audio_file_path = tk.StringVar()
        self.audio_file_path_label = tk.Label(root, textvariable=self.audio_file_path)
        self.audio_file_path_label.pack()

        self.upload_button = ttk.Button(root, text="Upload Audio", command=self.upload_audio)
        self.upload_button.pack(pady=5)

        self.play_button = ttk.Button(root, text="Start", command=self.toggle_metronome)
        self.play_button.pack(pady=10)
        
        self.is_playing = False
        self.metronome_thread = None
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if self.is_playing:
            self.stop_metronome()
        self.root.destroy()

    def upload_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            self.audio_file_path.set(file_path)

    def update_bpm_label(self, _=None):
        self.bpm_label.config(text="BPM: {}".format(self.bpm.get()))

    def toggle_metronome(self):
        if self.is_playing:
            self.stop_metronome()
            self.play_button.config(text="Start")
        else:
            self.start_metronome()
            self.play_button.config(text="Stop")

    def start_metronome(self):
        if not self.is_playing and self.audio_file_path.get():
            self.is_playing = True
            self.metronome_thread = threading.Thread(target=self.metronome_loop)
            self.metronome_thread.start()

    def stop_metronome(self):
        self.is_playing = False
        if self.metronome_thread:
            self.metronome_thread.join()  # Wait for the thread to finish
        pygame.mixer.quit()  # Release resources
        
    def metronome_loop(self):
        pygame.mixer.init()
        sound = pygame.mixer.Sound(self.audio_file_path.get())
        
        while self.is_playing:
            sound.play()
            time.sleep(60 / self.bpm.get())
        
        pygame.mixer.quit()

        self.audio_file_path.set("")

if __name__ == "__main__":
    pygame.init()
    root = tk.Tk()
    app = MetronomeApp(root)
    
    root.mainloop()
