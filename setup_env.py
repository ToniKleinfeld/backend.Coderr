import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

env_path = Path(".env")

# When .env allready exist, abort task.
if env_path.exists():
    print(".env allready exist. End script.")
else:
    secret_key = get_random_secret_key()

    env_content = f"""# Generiert mit setup_env.py
SECRET_KEY={secret_key}
DEBUG=True #set on False when go to production
CORS_ALLOWED_ORIGINS=http://localhost:5500   #change if needed
"""

    # Datei schreiben
    with open(env_path, "w") as f:
        f.write(env_content)

    print(".env succesfull created.")
