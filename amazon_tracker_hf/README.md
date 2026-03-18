---
title: Amazon Price Tracker
emoji: 🛒
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# Amazon Price Tracker (Hugging Face Edition)

This is a Flask web application that tracks Amazon product prices over time.

## How it works

1. It uses a SQLite database to store tracked items and their price histories.
2. It uses `requests` and `BeautifulSoup` with **ScraperAPI** to fetch prices.
3. It has a `/api/cron/run-tracker` endpoint designed to be triggered by an external service (like cron-job.org) to automate the price updates.

## Setup Instructions

1. Add your `SCRAPER_API_KEY` to the repository secrets/variables in Hugging Face.
2. Add a `CRON_SECRET` to the variables (e.g. any secure password).
3. Set up a free task on [cron-job.org](https://cron-job.org/) to visit `https://<YOUR_HF_SPACE_URL>/api/cron/run-tracker?token=<YOUR_CRON_SECRET>` every hour.
