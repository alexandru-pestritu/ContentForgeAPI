import sys
from app.services.settings_service import SettingsService

def main():
    """
    Initialize default settings in the database.
    """
    try:
        print("Starting settings initialization...")
        SettingsService.initialize_default_settings()
        print("Settings have been successfully initialized.")
    except Exception as e:
        print(f"An error occurred while initializing settings: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
