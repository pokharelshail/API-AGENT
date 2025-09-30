import argparse
import sys
from agent import Agent

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Intelligent API Agent powered by Google Gemini 2.0 Flash")
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Enable verbose mode for detailed debugging output"
    )
    parser.add_argument(
        "--max-exchanges", 
        type=int, 
        default=50, 
        help="Maximum number of conversation exchanges to keep in session (default: 50)"
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting Agent\n")
    
    # Initialize agent with command line options
    agent = Agent(max_exchanges=args.max_exchanges, verbose=args.verbose)
    
    print("\n" + "="*60)
    print("Agent Ready! Commands:")
    print("- Type 'quit' to exit")
    print("- Type 'clear' to clear session context")
    print("- Type 'session' to see session info")
    if args.verbose:
        print("- Verbose mode: ON (detailed debugging enabled)")
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
            print(f"  Exchanges: {session_info['exchanges_count']} / {session_info['max_exchanges']}")
            print(f"  Total characters: {session_info['total_characters']:,}")
            print(f"  Average exchange length: {session_info['average_exchange_length']:.0f} chars")
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
        
        # Show verbose information if enabled
        if args.verbose:
            if response.tools_used:
                print(f"🔧 Tools used: {', '.join(response.tools_used)}")
            
            if response.api_calls:
                print("🌐 API Calls made:")
                for call in response.api_calls:
                    status = "✅" if call['success'] else "❌"
                    print(f"  {status} {call['method']} {call['url']} (Status: {call.get('status_code', 'N/A')})")
            
            if response.metadata:
                print(f"📋 Metadata: {response.metadata}")
        else:
            # Only show technical details if there were issues or if specifically requested
            if response.tools_used and (response.error or len(response.tools_used) > 1):
                print(f"🔧 Tools used: {', '.join(response.tools_used)}")
            
            if response.api_calls and response.error:
                print("🌐 API Calls made:")
                for call in response.api_calls:
                    status = "✅" if call['success'] else "❌"
                    print(f"  {status} {call['method']} {call['url']} (Status: {call.get('status_code', 'N/A')})")
        
        print("-"*60 + "\n")


if __name__ == "__main__":
    main()