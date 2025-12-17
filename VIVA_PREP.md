# 🎓 Viva Exam Preparation Guide

## Q1: Why did you choose Flask over Django for this project?
**Answer:** "I chose **Flask** because it is a **micro-framework**. It provides exactly what I need—routing, request handling, and templating—without the heavy overhead of Django's built-in ORM and admin panel, which are unnecessary for this specific tool. This makes the application **lighter**, **faster**, and easier to extend with specific libraries like `PyPDF2` or `gTTS` effectively."

## Q2: How do you handle file security during upload?
**Answer:** "Security is critical. I used the `secure_filename` function from the `werkzeug.utils` library. This function prevents **Path Traversal Attacks** by removing dangerous characters (like `../`) that could allow a malicious user to overwrite system files. Additionally, I implemented **server-side validation** to ensure only files with the `.pdf` extension are processed, ignoring any client-side spoofing."

## Q3: How is the frontend communicating with the backend?
**Answer:** "The frontend uses **AJAX (Asynchronous JavaScript and XML)** via the modern `fetch` API. When a user uploads a file, we send a `POST` request with a `FormData` object containing the file and the selected language. The backend processes this and returns a **JSON response**. This allows us to update the UI (like showing the success message) **dynamically without reloading the page**, providing a smoother user experience."

## Q4: How would you implement the actual Audio Conversion?
**Answer:** "The architecture is already in place. In the `upload_file` route, after saving the PDF, I would:
1.  Use a library like `PyPDF2` or `pdfminer` to extract the text content from the PDF.
2.  Pass that text to a Text-to-Speech engine. For a basic version, I'd use `gTTS` (Google Text-to-Speech) or `pyttsx3` for offline support.
3.  For a professional version, I would call a cloud API like **AWS Polly** or **Google Cloud TTS** to generate high-quality neural audio, save it as an MP3, and return the download URL in the JSON response."
    
## Q5: How does the new Translation Feature work?
**Answer:** "The translation feature acts as a **'Language Bridge'**. When a user selects a foreign language (like Hindi) for an English PDF, the backend first extracts the text using `PyPDF2`. Then, it passes this text to the `deep-translator` library (which wraps Google Translate). The translated text is then sent to the TTS engine. This sequence—**Extract -> Translate -> Synthesize**—allows users to consume content in their native language despite the original document being in English."

## Q6: What is 'Glassmorphism' which you mentioned in the design?
**Answer:** "Glassmorphism is a modern UI trend based on translucency. It uses the CSS property `backdrop-filter: blur()`, creates a semi-transparent background (like frosted glass), and uses a subtle white border to simulate a physical glass edge. This creates a sense of **depth and hierarchy** in the interface, making the primary content stand out against the background."

## Q7: Is this application scalable?
**Answer:** "Yes. Currently, it saves files locally, but for a scalable production environment, I would modify the storage logic to save files to an **S3 Bucket (AWS)** or **Google Cloud Storage**. The heavy processing (audio conversion) would be offloaded to a **Task Queue** (like Celery with Redis) so the web server doesn't get blocked during long conversions. This 'Asynchronous Worker' pattern is standard for scalable web apps."
