# 1. Start with a clean Python 3.10 Linux machine
FROM python:3.10-slim

# 2. Force the installation of the OpenGL and X11 graphics drivers
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libglu1-mesa \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# 3. Set up the working folder
WORKDIR /app

# 4. Copy your files into the container
COPY . .

# 5. Install your Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 6. Run the Braun UI Streamlit app
CMD ["sh", "-c", "streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0"]
