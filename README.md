# 🤖 API Agent

An intelligent API agent powered by Google's Gemini 2.0 Flash that can interact with web APIs while maintaining conversation context and providing structured responses.

## ✨ Features

- **🌐 API Integration**: Make GET and POST requests to any web API
- **🧠 Context Awareness**: Remembers conversation history and references previous API calls
- **📋 Structured Responses**: Uses Pydantic models for type-safe, validated responses
- **🎯 Custom Headers**: Support for authentication and custom HTTP headers
- **📊 Session Management**: Intelligent conversation tracking without artificial limits
- **⚡ Gemini 2.0 Flash**: Leverages Google's Gemini Flash AI model with 1M token context window
- **🛠️ Error Handling**: Graceful error management with detailed debugging info

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Google AI API key
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd my-agent
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
   ```

4. **Run the agent**
   ```bash
   python main.py
   ```

## 💡 Usage

### Basic Commands

- **`quit`** - Exit the application
- **`clear`** - Clear conversation history
- **`session`** - Show session information

### API Examples

#### Making GET Requests