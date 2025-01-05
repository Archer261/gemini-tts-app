from dotenv import load_dotenv
import os
from typing import List, Dict
import google.generativeai as genai
import json
import time
from gtts import gTTS

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

load_dotenv()
gemini_api_key_env = os.getenv('GOOGLE_API_KEY')

genai.configure(api_key=gemini_api_key_env)
model = genai.GenerativeModel('gemini-1.5-flash',
                            safety_settings=safety_settings,
                            generation_config={
                                'temperature': 0.7,
                                'top_p': 0.8,
                                'top_k': 40,
                                'max_output_tokens': 2048,
                            })

def generate_script(topic: str) -> Dict:
    """Generate video script and structure using Gemini API"""
    try:
        prompt = f"""Create a 60 second YouTube short script about {topic}. 
    
        Use these timing guidelines but DO NOT include them in your response:
        - Introduction should be 10 seconds
        - Main content should be 30 seconds
        - Conclusion should be 10 seconds
        - Call to action should be 10 seconds

        Format your response EXACTLY as follows, without including any timing references or sections references such as "Introduction" or "Main Content":

        Title: [Video Title]

        Introduction:
        [Write the introduction text here]
        Visual 1: [scene description]
        Visual 2: [scene description]

        Main Content:
        [Write the main content here]
        Visual 1: [scene description]
        Visual 2: [scene description]
        Visual 3: [scene description]

        Conclusion:
        [Write the conclusion here]
        Visual 1: [scene description]
        Visual 2: [scene description]

        Call to Action:
        [Write the call to action here]
        Visual 1: [scene description]"""

        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise ValueError("No response generated from Gemini API")
            
        # Debug: Print raw response
        print("\nRaw Gemini Response:")
        print(response.text)
        
        def parse_script(raw_text: str) -> List[Dict]:
            """Helper method to parse Gemini's output into structured format"""
            sections = []
            current_section = None
            
            # Split text into lines and clean them
            lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
            
            # Debug: Print all lines
            print("\nProcessing script lines:")
            for i, line in enumerate(lines):
                print(f"Line {i}: {line}")
            
            for line in lines:
                # Check for section headers
                if any(line.lower().startswith(header.lower()) for header in [
                    "Title:", "Introduction:", "Section", "Main Content:",
                    "Conclusion:", "Call to Action:"
                ]):
                    # Save previous section if it exists
                    if current_section and current_section["text"]:
                        print(f"\nCompleted section: {json.dumps(current_section, indent=2)}")
                        sections.append(current_section)
                    
                    # Start new section
                    header = line.split(":")[0] if ":" in line else line
                    current_section = {
                        "text": line.split(":", 1)[1].strip() if ":" in line else line,
                        "scenes": []
                    }
                    print(f"\nStarting new section: {header}")
                
                # Check for visual descriptions
                elif current_section and (
                    line.lower().startswith(("visual", "scene")) or
                    "visual:" in line.lower() or
                    "scene:" in line.lower()
                ):
                    # Handle both "Visual 1:" and "Visual: " formats
                    scene_parts = line.split(":", 1)
                    if len(scene_parts) > 1:
                        scene_desc = scene_parts[1].strip()
                        current_section["scenes"].append(scene_desc)
                        print(f"Added scene: {scene_desc}")
                
                # Add to current section's text
                elif current_section:
                    current_section["text"] += "\n" + line
            
            # Add final section
            if current_section and current_section["text"]:
                sections.append(current_section)
            
            # Ensure we have at least one section
            if not sections:
                sections.append({
                    "text": raw_text,
                    "scenes": []
                })
            
            return sections
        
        # Parse the response into structured format
        script = {
            "title": response.text.split("\n")[0].replace("Title:", "").strip(),
            "sections": parse_script(response.text)
        }
        
        # Debug: Print parsed script
        print("\nParsed Script Structure:")
        print(json.dumps(script, indent=2))
        
        if not script["sections"]:
            raise ValueError("Failed to parse script sections")
        
        # Verify scene descriptions
        scene_count = sum(len(section.get("scenes", [])) for section in script["sections"])
        print(f"\nTotal scenes found: {scene_count}")
        
        return script
        
    except Exception as e:
        print(f"Error generating script: {str(e)}")
        raise

def generate_audio(script: Dict, output_dir: str = "audio"):
    """Generate audio from script using gTTS"""
    try:
        # Create audio directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a filename based on the script title
        safe_title = "".join(c for c in script["title"] if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        output_filename = f"{safe_title}_{int(time.time())}.mp3"
        output_path = os.path.join(output_dir, output_filename)
        
        # Combine all text from sections
        full_text = ""
        for section in script["sections"]:
            full_text += section.get("text", "") + " "
            
        # Generate audio using gTTS
        tts = gTTS(text=full_text.strip(), lang='en', tld='co.uk', slow=False)
        tts.save(output_path)
        
        print(f"Audio file saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        raise
        
def main():    
    try:
        # Get topic from user
        print("\n=== YouTube Short Script Generator ===")
        topic = input("\nEnter the topic for your video: ")
        while not topic.strip():
            topic = input("Topic cannot be empty. Please enter a topic: ")

        print(f"\nGenerating script for topic: {topic}\n")

        # Generate script
        script = generate_script(topic)
        
        # Generate audio in the audio directory
        audio_path = generate_audio(script)
        print(f"\nSuccessfully generated audio at: {audio_path}")
        
    except Exception as e:
        print(f"\nError in main: {str(e)}")
        raise

    print("\nDone!")

if __name__ == "__main__":
    main()