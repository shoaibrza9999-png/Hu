# Amazon Price Tracker MVP

A simple web application to track Amazon prices over time, utilizing Flask, SQLAlchemy, ScraperAPI, and Chart.js.

## Local Development

1. Create a virtual environment:
   ```bash
   py -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask application (defaults to local SQLite database):
   ```bash
   flask --app app run
   ```
4. Access the web interface at `http://127.0.0.1:5000`.

### Running the background tracker locally

In a separate terminal, run:
```bash
flask --app app run-tracker
```
This will fetch the latest prices for all items in the database.

## Deploying to Render.com

This repository includes a `render.yaml` file to deploy the entire stack (PostgreSQL database, Web Service, and Cron Job) seamlessly.

1. Create an account on [Render.com](https://render.com/) and link your GitHub account.
2. In the Render Dashboard, click "New" -> "Blueprint".
3. Connect the repository containing this code.
4. Render will automatically detect the `render.yaml` file.
5. In the final step before creating the services, Render will ask you to supply the value for `SCRAPER_API_KEY`.
   - Enter your ScraperAPI key (e.g., `1f57cfc93728601451afdc95e862d30e`).
6. Click "Apply". Render will spin up:
   - A free PostgreSQL database.
   - A web service running the Flask application (using Gunicorn).
   - A cron job that runs the tracker script (`flask --app app run-tracker`) every hour.

Once deployed, you can access your live web application via the `.onrender.com` URL provided in the dashboard.
