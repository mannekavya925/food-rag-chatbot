from pyngrok import ngrok
import time

# Create tunnel
public_url = ngrok.connect(8501)
print(f"\n{'='*60}")
print(f"✅ Public URL: {public_url}")
print(f"{'='*60}\n")

# Keep tunnel alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ngrok.disconnect(public_url)
    print("\nTunnel closed.")
