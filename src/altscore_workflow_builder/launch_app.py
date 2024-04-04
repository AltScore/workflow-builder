import subprocess
import os
from dotenv import load_dotenv
from decouple import config


def launch_streamlit_app():
    print(os.getcwd())
    load_dotenv(dotenv_path='.env', override=True)
    print(os.environ.get("PROJECT_ROOT", "N/A"))
    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Path to your Streamlit app script
    app_path = os.path.join(dir_path, 'Home.py')
    # Launch the Streamlit app
    subprocess.run(['streamlit', 'run', app_path], check=True)


if __name__ == "__main__":
    launch_streamlit_app()
