import secrets
import os

def generate_secret_key(length=32):
    """Generate a secure random secret key."""
    return secrets.token_hex(length)

def save_to_env_file(secret_key, filename="../.env"):
    """Save the secret key to a .env file."""
    with open(filename, "a") as env_file:
        env_file.write(f"\nSECRET_KEY={secret_key}\n")
    print(f"Secret key saved to {filename}")

if __name__ == "__main__":
    # Generate a secret key
    secret_key = generate_secret_key()
    print(f"Generated secret key: {secret_key}")

    # Optionally save to .env file
    save = input("Do you want to save the secret key to a .env file? (y/n): ").strip().lower()
    if save == 'y':
        save_to_env_file(secret_key)
