import os
from pdf2image import convert_from_path
import base64
from io import BytesIO
import requests
from dotenv import load_dotenv
from util import update_file_processing_status

load_dotenv()

UPLOAD_FOLDER = "data"
OUTPUT_FOLDER = "extracted"


def list_files(folder_path):
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
    return files

def convert_pdf_to_img(file):
    images = convert_from_path(file)
    return images

def convert_img_to_base64(images):
    base64_images = []
    
    for image in images:
        buffered = BytesIO()
        image.save(buffered, format="PNG")  # Save the image as PNG in buffer
        img_bytes = buffered.getvalue()
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')  # Encode to base64 string
        formatted_base64 = f"data:image/png;base64,{img_base64}"
        base64_images.append(formatted_base64)
    return base64_images

def call_qwen_vision_api(images):
    prompt = """
        <prompt>
            <identity>
                You are an AI assistant that extracts meaningful and structured text from documents and images.
                Focus on clarity, logical flow, and excluding decorative or irrelevant elements.
            </identity>

            <capabilities>
                <capability>Extract main text, explanations, introductions, and conclusions.</capability>
                <capability>Convert tabular data into clean Markdown tables.</capability>
                <capability>Preserve structure, indentation, and logical sequence.</capability>
                <capability>Deliver well-formatted Markdown for downstream processing.</capability>
            </capabilities>

            <rules>
                <rule>Keep only meaningful, explanatory content.</rule>
                <rule>Exclude visuals, decorative elements, and repetitions.</rule>
                <rule>Maintain flow and readability in Markdown.</rule>
                <rule>Reproduce tables faithfully, preserving spans and accuracy.</rule>
                <rule>Provide detailed responses if a solution is requested.</rule>
            </rules>

            <environment>
                You may use OCR or parsing to extract text. 
                Goal: clean, structured Markdown for integration into RAG workflows.
            </environment>
        </prompt>
        """
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
        "Content-Type": "application/json"
    }
    content = [{"type": "text", "text": prompt}]

    for image_base64 in images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image_base64
            }
        })
    
    data = {
        "model": "google/gemini-2.5-flash-image-preview:free",
        "messages": [{
                "role": "user",
                "content": content
            }]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            extracted_text = result['choices'][0]['message']['content']
            
            return extracted_text
        else:
            print(f"Unexpected API response format: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                print(f"Error details: {error_details}")
            except:
                print(f"Response content: {e.response.text}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None
    

def main():
    files = list_files(UPLOAD_FOLDER)
    for file in files:
        images = convert_pdf_to_img(file)
        base64_images = convert_img_to_base64(images)
        response = call_qwen_vision_api(base64_images)

        if response:
            output_filename = os.path.basename(file).replace(".pdf", ".md")
            if not os.path.exists("extracted"):
                os.mkdir("extracted")
            output_path = os.path.join("extracted", output_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(response)
            filename = os.path.basename(file)
            update_file_processing_status(filename, output_path)

if __name__ == "__main__":
    main()