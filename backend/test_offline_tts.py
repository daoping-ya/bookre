import pyttsx3
import os

def test_offline_tts():
    print("Testing pyttsx3...")
    try:
        engine = pyttsx3.init()
        output_file = "test_offline.mp3"
        # pyttsx3 on Windows usually saves as wav if not specified, but let's try
        # Actually save_to_file might determine format by extension or just save wav
        engine.save_to_file("Hello, this is an offline test.", output_file)
        engine.runAndWait()
        
        if os.path.exists(output_file):
            print(f"Success! Audio saved to {output_file}")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print("Error: File was not created.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_offline_tts()
