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

In a separate terminal, you can run the tracker manually via CLI:
```bash
flask --app app run-tracker
```
Or you can trigger the webhook in your browser: `http://127.0.0.1:5000/api/cron/run-tracker?token=default-local-secret`

## Deploying to Render.com

This repository includes a `render.yaml` file to deploy the stack (PostgreSQL database and Web Service) seamlessly.

1. Create an account on [Render.com](https://render.com/) and link your GitHub account.
2. In the Render Dashboard, click "New" -> "Blueprint".
3. Connect the repository containing this code.
4. Render will automatically detect the `render.yaml` file.
5. Provide your `SCRAPER_API_KEY` when prompted. (Render will automatically generate a secure `CRON_SECRET` for you).
6. Click "Apply".

## Automating the Tracker (Free Tier Workaround)

Render does not allow native Cron Jobs on the Free Tier. To automate the price tracking for free, we use a web-accessible webhook (`/api/cron/run-tracker`) secured by a secret token, and an external free cron service to ping it.

1. Find your secret token: In the Render dashboard, click on your deployed Web Service (`amazon-tracker-web`), go to "Environment", and copy the value of `CRON_SECRET`.
2. Find your app URL: Also in the Render dashboard, copy the public URL of your web service (e.g., `https://amazon-tracker-web.onrender.com`).
3. Create a free account on [cron-job.org](https://cron-job.org/).
4. Click "Create Cronjob".
5. Set the URL to your webhook, passing the secret token as a query parameter. It should look exactly like this:
   `https://YOUR_APP_NAME.onrender.com/api/cron/run-tracker?token=YOUR_CRON_SECRET_VALUE`
6. Set the Execution schedule to "Every 1 hours" (or however often you want to track).
7. Save the cronjob.

Cron-job.org will now visit that hidden link automatically every hour. Your app will verify the secret token, query all saved items, and fetch their latest prices in the background.
