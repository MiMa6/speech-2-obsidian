import os
from datetime import datetime
import subprocess
import sys
import platform
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Voice Memos directory from environment variable
VOICE_MEMOS_DIR = os.getenv("VOICE_MEMOS_DIR")


def check_directory_access():
    """Check if we have access to the Voice Memos directory."""
    try:
        if not os.path.exists(VOICE_MEMOS_DIR):
            print(f"❌ Voice Memos directory not found at: {VOICE_MEMOS_DIR}")
            print(
                "Set VOICE_MEMOS_DIR environment variable to override the default path"
            )
            return False

        # Try to list directory contents to verify permissions
        os.listdir(VOICE_MEMOS_DIR)
        return True
    except PermissionError:
        print("❌ Permission denied accessing Voice Memos directory.")
        print("Please grant access to the Voice Memos directory")
        return False
    except Exception as e:
        print(f"❌ Error accessing Voice Memos directory: {e}")
        print("Set VOICE_MEMOS_DIR environment variable to override the default path")
        return False


# Function to parse date from the filename and return a datetime object
def parse_date_from_filename(filename):
    try:
        # Assuming filename format is like 'YYYYMMDD HHMMSS-<ID>.m4a'
        date_str = filename.split(" ")[0]  # Get the first part 'YYYYMMDD'
        time_str = filename.split(" ")[1].split("-")[0]  # Get time part 'HHMMSS'
        full_date_str = date_str + " " + time_str  # Combine into 'YYYYMMDD HHMMSS'

        # Convert the string into a datetime object
        return datetime.strptime(full_date_str, "%Y%m%d %H%M%S")
    except Exception as e:
        # print(f"⚠️ Error parsing date from filename '{filename}': {e}")
        return None


# Function to find the most recent recording
def find_latest_recording():
    if not check_directory_access():
        return None

    latest_file = None
    latest_time = None
    MIN_FILE_SIZE = 10 * 1024  # 10KB in bytes

    try:
        # Loop through all files in the directory
        for filename in os.listdir(VOICE_MEMOS_DIR):
            # Filter for .m4a files only
            if filename.endswith(".m4a"):
                file_path = os.path.join(VOICE_MEMOS_DIR, filename)

                # Check file size
                file_size = os.path.getsize(file_path)
                if file_size < MIN_FILE_SIZE:
                    # print(f"⚠️ Skipping {filename} - too small ({file_size/1024:.1f}KB)")
                    continue

                # Parse the date from the filename
                file_date = parse_date_from_filename(filename)

                if file_date and (latest_time is None or file_date > latest_time):
                    latest_time = file_date
                    latest_file = file_path

        return latest_file
    except Exception as e:
        print(f"❌ Error accessing files: {e}")
        return None


# Function to open the latest file in Finder
def open_latest_recording():
    latest_file = find_latest_recording()

    if latest_file:
        print(f"📝 Found latest recording: {os.path.basename(latest_file)}")
        try:
            # Open the file's location in Finder using the -R flag to reveal the file
            subprocess.run(["open", "-R", latest_file])
            print("📂 Opening recording location in Finder...")
        except Exception as e:
            print(f"❌ Error opening the file location: {e}")
    else:
        print("❌ No voice memo recordings found.")


if __name__ == "__main__":
    open_latest_recording()
