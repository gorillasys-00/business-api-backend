import os
import subprocess
import sys
import time

def setup_and_run():
    # Define directories
    base_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(base_dir, "venv")
    
    # Python executable depending on OS
    python_cmd = sys.executable
    if os.name == 'nt':
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
        venv_uvicorn = os.path.join(venv_dir, "Scripts", "uvicorn.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        venv_pip = os.path.join(venv_dir, "bin", "pip")
        venv_uvicorn = os.path.join(venv_dir, "bin", "uvicorn")

    # Step 1: Create virtual environment if it doesn't exist
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        subprocess.run([python_cmd, "-m", "venv", "venv"], check=True, cwd=base_dir)
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

    # Step 2: Install requirements
    print("Installing requirements...")
    pip_cmd = [venv_pip, "install", "-r", "requirements.txt"]
    subprocess.run(pip_cmd, check=True, cwd=base_dir)
    print("Requirements installed successfully.")
    
    # Step 3: Run the Uvicorn server
    print("\n" + "="*50)
    print("Starting FastAPI Application with Uvicorn")
    print("Swagger UI will be available at: http://127.0.0.1:8000/docs")
    print("="*50 + "\n")
    
    # Run uvicorn
    # Using subprocess.Popen blockingly, so it runs indefinitely
    try:
        print("Press Ctrl+C to stop the server.")
        subprocess.run([venv_uvicorn, "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"], cwd=base_dir)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"\nServer stopped with error: {e}")

if __name__ == "__main__":
    setup_and_run()
