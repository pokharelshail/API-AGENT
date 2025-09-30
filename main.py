import requests
from agent import Agent

def main():
    print("🚀 Starting Agent\n")
    
    # Initialize agent with custom context limit (default is 8000 chars)
    agent = Agent(max_context_chars=8000)
    
    print("\n" + "="*60)
    print("Agent Ready! Commands:")
    print("- Type 'quit' to exit")
    print("- Type 'clear' to clear session context")
    print("- Type 'session' to see session info")
    print("="*60 + "\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            print("👋 Goodbye!")
            break
        
        if user_input.lower() == 'clear':
            agent.clear_session()
            continue
        
        if user_input.lower() == 'session':
            session_info = agent.get_session_info()
            print(f"\n📊 Session Info:")
            print(f"  Context length: {session_info['context_length']:,} / {session_info['max_context_length']:,} chars")
            print(f"  Exchanges: {session_info['exchanges_count']}")
            print(f"  Usage: {session_info['context_usage_percent']:.1f}%")
            print("-"*60 + "\n")
            continue
        
        if not user_input:
            continue
        
        print("\n🤖 Agent:")
        response = agent.run(user_input)
        
        # Display the structured response
        print(f"\n{response.message}\n")
        
        # Show additional details if available (but keep it minimal to avoid clutter)
        if response.error:
            print(f"❌ Error: {response.error}")
        
        # Only show technical details if there were issues or if specifically requested
        if response.tools_used and (response.error or len(response.tools_used) > 1):
            print(f"🔧 Tools used: {', '.join(response.tools_used)}")
        
        if response.api_calls and response.error:
            print("🌐 API Calls made:")
            for call in response.api_calls:
                status = "✅" if call['success'] else "❌"
                print(f"  {status} {call['method']} {call['url']} (Status: {call.get('status_code', 'N/A')})")
        
        # Show session context info if it's getting full
        if response.session_context_length and response.session_context_length > 50000:
            print(f"⚠️  Session context: {response.session_context_length:,} chars (consider 'clear' command)")
        
        print("-"*60 + "\n")


if __name__ == "__main__":
    main()