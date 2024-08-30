import os
import simpleaudio as sa
from pydub import AudioSegment
import customtkinter as ctk
from tkinter import filedialog, messagebox
import multiprocessing

def play_audio_segment(audio_segment, position) -> object:
    return sa.play_buffer(audio_segment[position:].raw_data, audio_segment.channels, audio_segment.sample_width, audio_segment.frame_rate)

class AudioConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Converter")
        self.root.geometry("700x450")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")
        self.audio_obj = None
        self.audio = None
        self.create_widgets()

    def create_widgets(self):
        # Title
        title = ctk.CTkLabel(self.root, text="Audio Converter", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack(pady=20)

        # Input File
        input_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        input_frame.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(input_frame, text="Input File:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, sticky="w")
        self.file_path = ctk.StringVar()
        ctk.CTkEntry(input_frame, textvariable=self.file_path, width=360).grid(row=0, column=1, padx=10)
        ctk.CTkButton(input_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=10)

        # Input and Output Format
        format_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        format_frame.pack(pady=10, fill="x", padx=20)
        ctk.CTkLabel(format_frame, text="Input Format:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, sticky="w")
        self.input_format = ctk.StringVar(value="wav")
        input_formats = ["wav", "mp3", "ogg"]
        ctk.CTkOptionMenu(format_frame, variable=self.input_format, values=input_formats, width=120).grid(row=0, column=1, padx=10)

        ctk.CTkLabel(format_frame, text="Output Format:", font=ctk.CTkFont(size=14)).grid(row=0, column=2, padx=10, sticky="w")
        self.output_format = ctk.StringVar(value="mp3")
        output_formats = ["mp3", "wav", "ogg"]
        ctk.CTkOptionMenu(format_frame, variable=self.output_format, values=output_formats, width=120).grid(row=0, column=3, padx=10)

        # BPM and Volume Adjustments (Side by Side)
        adjustments_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        adjustments_frame.pack(pady=10, fill="x", padx=20)

        # BPM Adjustment
        bpm_frame = ctk.CTkFrame(adjustments_frame, fg_color="transparent")
        bpm_frame.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(bpm_frame, text="BPM Adjustment:", font=ctk.CTkFont(size=14)).pack(side=ctk.TOP, anchor="w")
        self.bpm_value = ctk.DoubleVar(value=100)
        ctk.CTkSlider(bpm_frame, variable=self.bpm_value, from_=50, to=200, number_of_steps=150).pack(side=ctk.TOP, pady=10)
        ctk.CTkLabel(bpm_frame, text="BPM", font=ctk.CTkFont(size=12)).pack(side=ctk.TOP, anchor="w")

        # Volume Adjustment
        volume_frame = ctk.CTkFrame(adjustments_frame, fg_color="transparent")
        volume_frame.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(volume_frame, text="Volume Adjustment:", font=ctk.CTkFont(size=14)).pack(side=ctk.TOP, anchor="w")
        self.volume_value = ctk.DoubleVar(value=1.0)
        ctk.CTkSlider(volume_frame, variable=self.volume_value, from_=0.1, to=2.0, number_of_steps=19).pack(side=ctk.TOP, pady=10)
        ctk.CTkLabel(volume_frame, text="Volume", font=ctk.CTkFont(size=12)).pack(side=ctk.TOP, anchor="w")

        # Convert and Preview Buttons
        button_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        button_frame.pack(pady=20, fill="x", padx=20)
        ctk.CTkButton(button_frame, text="Convert", command=self.convert_audio, width=120).pack(side=ctk.LEFT, padx=10)
        ctk.CTkButton(button_frame, text="Preview", command=self.preview_audio, width=120).pack(side=ctk.RIGHT, padx=10)

        # Status Bar
        self.status = ctk.CTkLabel(self.root, text="", font=ctk.CTkFont(size=14))
        self.status.pack(pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.ogg")])
        if filename:
            ext = filename.split(".")[-1]
            self.file_path.set(filename)
            self.input_format.set(ext)


    def convert_audio(self):
        input_file = self.file_path.get()
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return

        input_format = self.input_format.get()
        output_format = self.output_format.get()
        if input_format not in ["wav", "mp3", "ogg"] or output_format not in ["mp3", "wav", "ogg"]:
            messagebox.showerror("Error", "Unsupported format")
            return

        try:
            # Read the audio file
            audio = AudioSegment.from_file(input_file, format=input_format)
            # Adjust volume
            volume = self.volume_value.get()
            audio = audio + (volume * 10 - 10)  # Adjust volume based on the scale (1.0 is the default)
            # Save the converted file
            output_file = f"output.{output_format}"
            audio.export(output_file, format=output_format)
            self.status.configure(text=f"Conversion successful! Saved as {output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def preview_audio(self):
        input_file = self.file_path.get()
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return

        try:
            self.preview_window = ctk.CTkToplevel(self.root)
            self.preview_window.title("Preview Audio")
            self.preview_window.geometry("400x200")

            # Load the audio file
            self.audio = AudioSegment.from_file(input_file)
            # Adjust volume
            volume = self.volume_value.get()
            self.audio = self.audio + (volume * 10 - 10)

            # Play/Pause Button
            self.play_button = ctk.CTkButton(self.preview_window, text="Play", command=self.play_audio)
            self.play_button.pack(pady=10)

            self.pause_button = ctk.CTkButton(self.preview_window, text="Pause", command=self.pause_audio, state=ctk.DISABLED)
            self.pause_button.pack(pady=10)

            # Slider for audio position
            self.position_value = ctk.IntVar(value=0)
            self.position_slider = ctk.CTkSlider(self.preview_window, variable=self.position_value, from_=0, to=len(self.audio), command=self.update_audio_position)
            self.position_slider.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def play_audio(self):
        if self.audio_obj is not None:
            self.audio_obj.stop()

        self.audio_obj = play_audio_segment(self.audio, int(self.position_value.get()))
        self.play_button.configure(state=ctk.DISABLED)
        self.pause_button.configure(state=ctk.NORMAL)
        self.update_slider()

    def pause_audio(self):
        if self.audio_obj is not None:
            self.audio_obj.stop()
            self.audio_obj = None
        self.play_button.configure(state=ctk.NORMAL)
        self.pause_button.configure(state=ctk.DISABLED)

    def update_slider(self):
        if self.audio_obj is not None:
            position = self.position_value.get()
            position += 1000  # Assuming the slider moves forward every second
            self.position_value.set(position)
            self.root.after(1000, self.update_slider)  # Update every second

    def update_audio_position(self, position):
        if self.audio_obj is not None:
            self.pause_audio()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    root = ctk.CTk()
    app = AudioConverterApp(root)
    root.mainloop()
