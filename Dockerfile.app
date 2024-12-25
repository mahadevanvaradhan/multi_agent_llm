FROM python:3.12-slim

RUN mkdir /usr/local/chatbot/
# Set the working directory
WORKDIR /usr/local/chatbot/

# Upgrade pip and install setuptools
RUN pip install --upgrade pip setuptools

# Install cffi and lxml first
RUN pip install --no-cache-dir cffi lxml

RUN pip install llama-index-core && \
    pip install llama-index

# Copy everything from the current directory to /app in the container

COPY . /usr/local/chatbot

RUN pip install -r requirements.txt

RUN pip install --upgrade pip setuptools wheel

# Install PostgreSQL dependencies
RUN pip install \
    psycopg2-binary \
    "psycopg[binary,pool]" \
    sqlalchemy \
    pgvector \
    psycopg \
    psycopg-binary \
    psycopg-pool \
    fastapi \
    uvicorn[standard] 

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DISPLAY=:0
ENV PYTHONPATH /usr/local/chatbot

EXPOSE 8888 7282 8000 7860
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]