import sounddevice as sd
import numpy as np
import queue
import threading
import time
from datetime import datetime
import scipy.io.wavfile as wav
import os

# Audio recording settings
SILENCE_THRESHOLD = 0.02  # Adjust this value based on your microphone sensitivity
SILENCE_DURATION = 2.0  # Stop after 2 seconds of silence
MAX_DURATION = 300  # Maximum recording duration in seconds
DEFAULT_MIC_NAME = (
    "MacBook Pro Microphone"  # Change this to the name of your microphone
)


class AudioRecorder:
    def __init__(self, output_directory, mic_name=None):
        """
        Initialize AudioRecorder.

        Args:
            output_directory (str): Directory to save recordings
            mic_name (str, optional): Name of the microphone to use.
                                    If None, uses the system default input device.
        """
        self.output_directory = output_directory
        self.mic_name = mic_name or DEFAULT_MIC_NAME

    def get_mic_device(self):
        """Find the specified microphone device index."""
        devices = sd.query_devices()
        print("\nAvailable audio devices:")
        default_device = sd.default.device[0]  # Get system default input device

        for idx, device in enumerate(devices):
            is_input = device.get("max_input_channels", 0) > 0
            is_default = idx == default_device
            status = "(default)" if is_default else ""
            if is_input:
                print(f"{idx}: {device['name']} {status}")

            # Check if this device matches our target microphone
            if self.mic_name and self.mic_name in device["name"]:
                return idx

        # If specified mic not found, use system default
        if self.mic_name:
            print(f"\nWarning: Specified microphone '{self.mic_name}' not found.")
            print(f"Using system default input device instead.")

        return default_device

    def _audio_callback(self, indata, frames, time, status, q):
        """Callback for audio stream to handle incoming audio data."""
        if status:
            print(status)
        q.put(indata.copy())

    def _is_silent(self, data, threshold):
        """Check if the audio chunk is silent."""
        return np.max(np.abs(data)) < threshold

    def record(self):
        """Record audio until silence is detected."""
        try:
            input_device = self.get_mic_device()
            device_info = sd.query_devices(input_device, "input")
            sample_rate = int(device_info["default_samplerate"])
            channels = min(1, device_info["max_input_channels"])

            print(f"\nUsing audio device: {device_info['name']}")
            print(f"Sample rate: {sample_rate} Hz")
            print(f"Channels: {channels}")
            print(
                "\nStarting recording... (speak now, will stop after 2 seconds of silence)"
            )

            q = queue.Queue()
            recording = []
            silence_start = None
            is_recording = True
            start_time = time.time()

            def audio_input_stream():
                with sd.InputStream(
                    device=input_device,
                    samplerate=sample_rate,
                    channels=channels,
                    callback=lambda *args: self._audio_callback(*args, q),
                ):
                    while is_recording:
                        time.sleep(0.1)

            thread = threading.Thread(
                target=audio_input_stream, daemon=True
            )  # Make thread daemon
            thread.start()

            try:
                while True:
                    if time.time() - start_time > MAX_DURATION:
                        print("\nMaximum recording duration reached")
                        is_recording = False
                        break

                    try:
                        data = q.get(timeout=0.1)
                        recording.append(data)

                        if self._is_silent(data, SILENCE_THRESHOLD):
                            if silence_start is None:
                                silence_start = time.time()
                            elif time.time() - silence_start >= SILENCE_DURATION:
                                print("\nSilence detected, stopping recording")
                                is_recording = False
                                break
                        else:
                            silence_start = None

                    except queue.Empty:
                        continue

            finally:
                is_recording = False
                if thread.is_alive():
                    thread.join(timeout=1.0)  # Wait for thread to finish with timeout

            if not recording:
                raise ValueError("No audio was recorded")

            recording = np.concatenate(recording)

            # Modified timestamp format with additional underscores
            timestamp = datetime.now().strftime("%Y_%m_%d__%H_%M_%S")
            current_date = datetime.now()

            # Create year/month/day directory structure
            year = current_date.strftime("%Y")
            month = current_date.strftime("%m")
            day = current_date.strftime("%d")

            # Construct the full directory path
            date_dir = os.path.join(self.output_directory, year, month, day)

            # Create all necessary directories
            os.makedirs(date_dir, exist_ok=True)

            # Create filename and full path
            filename = f"recording_{timestamp}.wav"
            file_path = os.path.join(date_dir, filename)

            wav.write(file_path, sample_rate, recording)
            print(f"Saved recording to: {file_path}")
            return file_path

        except Exception as e:
            print(f"\nError during recording: {str(e)}")
            print("\nTroubleshooting info:")
            print("1. Current audio devices:")
            print(sd.query_devices())
            print("\n2. Default device settings:")
            print(f"Default device: {sd.default.device}")
            print(f"Default samplerate: {sd.default.samplerate}")
            print(f"Default channels: {sd.default.channels}")
            raise
