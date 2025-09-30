# 🤖 API Agent

An intelligent API agent powered by Google's Gemini 2.0 Flash that can interact with web APIs while maintaining conversation context and providing structured responses.

## ✨ Features

- **🌐 API Integration**: Make GET and POST requests to any web API
- **🧠 Context Awareness**: Remembers conversation history and references previous API calls
- **📋 Structured Responses**: Uses Pydantic models for type-safe, validated responses
- **🎯 Custom Headers**: Support for authentication and custom HTTP headers
- **📊 Session Management**: Intelligent conversation tracking without artificial limits
- **⚡ Gemini 2.0 Flash**: Leverages Google's latest AI model with 1M token context window
- **🛠️ Error Handling**: Graceful error management with detailed debugging info

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Google AI API key
- `uv` package manager (recommended) or `pip`

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/pokharelshail/API-AGENT.git
   cd API-AGENT
   ```

2. **Install dependencies**
   
   **Option A: Using UV (recommended)**
   ```bash
   uv sync
   ```
   
   **Option B: Using pip**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
   ```

4. **Run the agent**
   
   **With UV:**
   ```bash
   uv run python main.py
   # or activate the environment first
   uv shell
   python main.py
   ```
   
   **With regular Python:**
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
```
You: Get data from https://jsonplaceholder.typicode.com/posts/1

Agent:
📡 API Request: GET https://jsonplaceholder.typicode.com/posts/1
✅ Status: 200
📄 Response Data:
{
  "userId": 1,
  "id": 1,
  "title": "sunt aut facere repellat provident occaecati excepturi optio reprehenderit",
  "body": "quia et suscipit..."
}
```

#### Making POST Requests with Headers
```
You: Post this data {"name": "John", "age": 30} to https://httpbin.org/post with header "Authorization: Bearer token123"

Agent:
📡 API Request: POST https://httpbin.org/post
📋 Headers: Authorization: Bearer token123
✅ Status: 200
📄 Response Data:
{
  "json": {
    "name": "John",
    "age": 30
  },
  "headers": {
    "Authorization": "Bearer token123"
  }
}
```

#### Context-Aware Follow-ups
```
You: Get user data from https://api.example.com/users/1
Agent: [Shows user data]

You: Now get their posts
Agent: [Automatically references the previous API call and fetches posts for that user]
```

## 🏗️ Architecture

### Core Components

#### 1. **Agent Class** (`agent.py`)
- Main orchestrator using LangChain and Gemini 2.0 Flash
- Manages session context and tool execution
- Provides structured responses via Pydantic models

#### 2. **SessionManager Class**
- Tracks conversation history without character limits
- Maintains up to 50 exchanges (configurable)
- Provides context-aware responses

#### 3. **API Tools** (`tools/api_tool.py`)
- **`get_api_request`**: Makes GET requests with optional headers
- **`post_api_request`**: Makes POST requests with data and headers
- Returns structured `APIResponse` objects

#### 4. **Response Models**
- **`AgentResponse`**: Structured agent responses with metadata
- **`APIResponse`**: Structured API call responses
- **`SessionContext`**: Individual conversation exchanges

### Data Flow

```
User Input → SessionManager → Agent → LangChain → Gemini 2.0 → Tools → API → Response
     ↑                                                                              ↓
     ← Structured Response ← Session Update ← Context Processing ← Tool Results ←
```

## 📖 API Reference

### Agent Class

```python
class Agent:
    def __init__(self, max_exchanges: int = 50)
    def run(self, input_text: str) -> AgentResponse
    def clear_session(self) -> None
    def get_session_info(self) -> Dict[str, Any]
```

### API Tools

```python
def get_api_request(url: str, headers: dict = None) -> APIResponse
def post_api_request(url: str, data: dict, headers: dict = None) -> APIResponse
```

### Response Models

```python
class AgentResponse(BaseModel):
    success: bool
    message: str
    timestamp: datetime
    tools_used: Optional[List[str]]
    api_calls: Optional[List[Dict[str, Any]]]
    error: Optional[str]
    metadata: Optional[Dict[str, Any]]

class APIResponse(BaseModel):
    success: bool
    status_code: Optional[int]
    data: Optional[Any]
    error: Optional[str]
    url: str
    method: str
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Your Google AI API key | ✅ Yes |

### Agent Configuration

```python
# Customize max exchanges in session
agent = Agent(max_exchanges=100)

# Default is 50 exchanges
agent = Agent()
```

## 🛠️ Development

### Project Structure

```
my-agent/
├── agent.py              # Main agent class and session management
├── main.py               # CLI application entry point
├── tools/
│   └── api_tool.py       # API interaction tools
├── pyproject.toml        # Project configuration
├── requirements.txt      # Pip dependencies
├── .env                  # Environment variables (create this)
└── README.md            # This file
```

### Adding New Tools

1. Create a new tool function in `tools/` directory
2. Decorate with `@tool` from LangChain
3. Add to the `self.tools` list in `Agent.__init__()`

Example:
```python
from langchain.tools import tool

@tool
def my_custom_tool(input_param: str) -> str:
    """Description of what this tool does."""
    # Your tool logic here
    return result
```

### Testing

**Interactive testing:**
```bash
# With UV
uv run python main.py

# With regular Python
python main.py
```

**Quick API test:**
```bash
# With UV
uv run python -c "
from agent import Agent
agent = Agent()
response = agent.run('Get data from https://httpbin.org/get')
print(response.message)
"

# With regular Python
python -c "
from agent import Agent
agent = Agent()
response = agent.run('Get data from https://httpbin.org/get')
print(response.message)
"
```

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure `GOOGLE_API_KEY` is set in your `.env` file
   - Verify the API key is valid and has appropriate permissions

2. **Network Errors**
   - Check internet connection
   - Verify target API endpoints are accessible
   - Check for firewall/proxy issues

3. **Memory Issues**
   - Use the `clear` command to reset session context
   - Reduce `max_exchanges` if needed

### Debug Mode

Enable verbose logging by setting `verbose=True` in the AgentExecutor:

```python
# In agent.py, line ~180
self.agent_executor = AgentExecutor(
    agent=agent,
    tools=self.tools,
    verbose=True,  # Enable debug output
    max_iterations=10
)
```

## 📝 License

This project is open source. Feel free to use, modify, and distribute as needed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues, questions, or feature requests, please open an issue in the repository.

---

**Built with ❤️ using Google Gemini 2.0 Flash, LangChain, and Pydantic**