import os
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
import PyPDF2
from gtts import gTTS
from deep_translator import GoogleTranslator

# Initialize Flask Application
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'static/audio'
ALLOWED_EXTENSIONS = {'pdf'}
                        
# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

def translate_text(text, target_language):
    """Translate text to target language using deep_translator."""
    try:
        if not text or not text.strip():
            return text
            
        print(f"Translating text to {target_language}...")
        
        # Use GoogleTranslator
        translator = GoogleTranslator(source='auto', target=target_language)
        
        # Chunking (limit ~5000 chars for Google Translate)
        # using 3000 to be safe and match our truncation logic if applied later, 
        # though we translate BEFORE truncation ideally? 
        # Actually our extract function returns full text. 
        # But convert_text_to_audio currently truncates to 3000. 
        # We should probably translate the full text THEN truncate? 
        # Or truncate then translate? Truncating then translating is faster for demo.
        # But user might want full translation.
        # Let's truncate then translate to save time/API calls for this demo app.
        
        # Update: Re-reading convert_text_to_audio, it truncates to 3000.
        # So if we translate 100 pages, it takes forever, then we throw away most of it.
        # So we should probably apply similar length limit before translation for performance in this demo.
        
        if len(text) > 4500:
             print("Text too long for demo translation, truncating to 4500 chars.")
             text = text[:4500]
             
        # Simple chunking just in case 4500 is close to limit with encoding
        chunk_size = 2000 
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        translated_parts = []
        for chunk in chunks:
            res = translator.translate(chunk)
            if res:
                translated_parts.append(res)
                
        return " ".join(translated_parts)

    except Exception as e:
        print(f"Translation failed: {e}")
        return text

def convert_text_to_audio(text, language, accent, filename):
    """Convert text to audio using gTTS and save as MP3."""
    try:
        if not text.strip():
            return None
        
        # Performance Optimization: Truncate text to 3000 characters for demo speed
        if len(text) > 3000:
            print(f"Truncating text from {len(text)} to 3000 chars for performance.")
            text = text[:3000] + "... [Content Truncated for Demo Speed]"
        
        # gTTS language codes might differ slightly from our UI codes.
        # We assume standard ISO codes. 'kn' is supported by gTTS.
        # TLD allows accents (com=US, co.uk=UK, co.in=India)
        tts = gTTS(text=text, lang=language, tld=accent, slow=False)
        
        audio_filename = os.path.splitext(filename)[0] + '.mp3'
        audio_path = os.path.join(app.config['AUDIO_FOLDER'], audio_filename)
        tts.save(audio_path)
        
        return audio_filename
    except Exception as e:
        print(f"Error converting audio: {e}")
        return None

@app.route('/')
def index():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file uploads and conversion."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file part found.'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file.'}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Retrieve selected language and accent
            language = request.form.get('language', 'en')
            accent = request.form.get('accent', 'com')
            
            # 1. Extract Text
            text = extract_text_from_pdf(file_path)
            
            if not text:
                return jsonify({'success': False, 'message': 'Could not extract text from PDF. It might be empty or scanned images.'}), 400

            # Translation Logic
            should_translate = request.form.get('translate', 'false') == 'true'
            if should_translate:
                text = translate_text(text, language)

            # 2. Convert to Audio
            audio_filename = convert_text_to_audio(text, language, accent, filename)
            
            if not audio_filename:
                return jsonify({'success': False, 'message': 'Error generating audio.'}), 500
            
            audio_url = url_for('static', filename=f'audio/{audio_filename}')
            
            return jsonify({
                'success': True,
                'message': 'File converted successfully!',
                'filename': filename,
                'language': language,
                'audio_url': audio_url
            }), 200
        except Exception as e:
            return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'}), 500

    return jsonify({'success': False, 'message': 'Invalid file type. Only PDF allowed.'}), 400

if __name__ == '__main__':
    # Open the browser automatically
    import webbrowser
    from threading import Timer
    
    def open_browser():
        webbrowser.open_new("http://127.0.0.1:5000")
        
    Timer(1, open_browser).start()
    
    # Run the application
    app.run(debug=True, use_reloader=False) # use_reloader=False prevents double opening
