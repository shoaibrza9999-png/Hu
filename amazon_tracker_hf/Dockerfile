FROM python:3.11-slim

# Create user with a home directory
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set working directory
WORKDIR $HOME/app

# Copy files
COPY --chown=user . $HOME/app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start the application on port 7860
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:create_app()"]
