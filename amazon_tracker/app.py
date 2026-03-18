import os
from flask import Flask, request, jsonify, render_template
from models import db, Item, PriceHistory

def create_app():
    app = Flask(__name__)

    # Default to local SQLite for development, but use DATABASE_URL from Render if available
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/items', methods=['GET'])
    def get_items():
        items = Item.query.all()
        return jsonify([item.to_dict() for item in items])

    @app.route('/api/add', methods=['POST'])
    def add_item():
        data = request.json
        url = data.get('url')
        target_price = data.get('target_price')

        if not url or not target_price:
            return jsonify({'error': 'URL and target_price are required'}), 400

        try:
            target_price = float(target_price)
        except ValueError:
            return jsonify({'error': 'target_price must be a number'}), 400

        existing_item = Item.query.filter_by(url=url).first()
        if existing_item:
            return jsonify({'error': 'Item already exists'}), 400

        # We will fetch the initial price in the tracker or right here.
        # For simplicity, we can let the background tracker handle the first scrape,
        # or we can do it synchronously. Given the requirement to return success quickly,
        # we'll do an initial synchronous scrape here using the scraper module.
        try:
            from scraper import fetch_price
            title, initial_price = fetch_price(url)

            new_item = Item(url=url, target_price=target_price, title=title)
            db.session.add(new_item)
            db.session.commit()

            if initial_price is not None:
                history = PriceHistory(item_id=new_item.id, price=initial_price)
                db.session.add(history)
                db.session.commit()

            return jsonify(new_item.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.cli.command("run-tracker")
    def run_tracker():
        """Scrape latest prices for all tracked items."""
        from scraper import fetch_price
        print("Starting tracker...")

        items = Item.query.all()
        for item in items:
            print(f"Tracking: {item.title or item.url}")
            try:
                title, current_price = fetch_price(item.url)

                if not item.title and title != "Unknown Title":
                    item.title = title
                    db.session.commit()

                if current_price is not None:
                    print(f"  Current Price: {current_price} | Target: {item.target_price}")

                    history = PriceHistory(item_id=item.id, price=current_price)
                    db.session.add(history)
                    db.session.commit()

                    if current_price <= item.target_price:
                        # For MVP, log it instead of actual email
                        print(f"  ALERT: Price dropped! Send email to user. {item.title} is now {current_price}")
                else:
                    print(f"  Failed to get price for {item.url}")

            except Exception as e:
                print(f"  Error processing {item.url}: {e}")
                db.session.rollback()

        print("Tracker finished.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
