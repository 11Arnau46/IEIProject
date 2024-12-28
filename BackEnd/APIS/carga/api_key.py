import secrets
import secrets

def generate_api_key():
    api_key = secrets.token_urlsafe(32)
    return api_key

if __name__ == "__main__":
    api_key = generate_api_key()
    print(f"Your generated API key is: {api_key}")