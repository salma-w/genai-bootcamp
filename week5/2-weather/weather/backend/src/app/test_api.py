import requests
import json

# Test the streaming endpoint
API_BASE = "http://localhost:8080"

def test_streaming():
    print("=" * 60)
    print("TESTING WEATHER ASSISTANT API")
    print("=" * 60)
    
    # Test 1: Check if server is running
    print("\n1. Testing server connection...")
    try:
        response = requests.get(f"{API_BASE}/")
        print(f"   ✓ Server is running: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Error connecting to server: {e}")
        print(f"   Make sure the server is running on {API_BASE}")
        return
    
    # Test 2: Send a test message
    print("\n2. Testing chat endpoint with streaming...")
    test_message = "What's the weather in Paris?"
    print(f"   Sending: '{test_message}'")
    
    try:
        response = requests.post(
            f"{API_BASE}/chat",
            json={"prompt": test_message},
            stream=True,
            timeout=30
        )
        
        print(f"   Response status: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        print("\n3. Stream content:")
        print("-" * 60)
        
        chunk_count = 0
        for line in response.iter_lines():
            if line:
                chunk_count += 1
                decoded = line.decode('utf-8')
                print(f"\n   Chunk {chunk_count}:")
                print(f"   Raw: {decoded[:200]}")
                
                # Try to parse if it's SSE format
                if decoded.startswith('data: '):
                    try:
                        json_str = decoded[6:]  # Remove 'data: '
                        data = json.loads(json_str)
                        print(f"   Parsed JSON keys: {list(data.keys())}")
                        print(f"   Full data: {json.dumps(data, indent=2)}")
                    except json.JSONDecodeError as e:
                        print(f"   ✗ JSON parse error: {e}")
        
        print("\n" + "-" * 60)
        print(f"\n   Total chunks received: {chunk_count}")
        
        if chunk_count == 0:
            print("\n   ⚠️  WARNING: No chunks received!")
            print("   This might indicate an issue with the streaming response.")
        
    except Exception as e:
        print(f"\n   ✗ Error during streaming: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Check chat history
    print("\n4. Testing chat history endpoint...")
    try:
        response = requests.get(f"{API_BASE}/chat")
        print(f"   ✓ Status: {response.status_code}")
        data = response.json()
        print(f"   Messages in history: {len(data.get('messages', []))}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_streaming()
