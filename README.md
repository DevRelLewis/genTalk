# GetTalk - Live Speech-to-Speech POC

A live speech-to-speech Streamlit proof of concept that demonstrates bidirectional voice interaction with OpenAI.

## Key Features

- **Live speech input** - Capture audio directly from your microphone
- **Language selection** - Choose the language for transcription and AI responses
- **Voice selection** - Select from available OpenAI voices for AI speech output
- **On-screen transcript** - View the full conversation with simple user and AI icons
- **Session-only caching** - No database, all state resets on refresh

## Requirements

- Python 3.8+
- OpenAI API key

## Environment Variables

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Installation

1. Clone the repository
2. Create a virtual environment:
```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Create a `.env` file with your OpenAI API key

## Running the App
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Usage

1. Select your preferred language from the dropdown
2. Select your preferred AI voice from the dropdown
3. Either speak into your microphone or type your message
4. Receive a spoken AI response with text transcript
5. View the full conversation history in the transcript panel
6. Clear the transcript anytime with the clear button

## Note

All conversation state is stored in session only and will reset when you refresh the page.