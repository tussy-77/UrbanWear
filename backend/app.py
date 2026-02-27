from flask import Flask
from sqlalchemy import text
from backend.config import Config
from backend.database import db



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    @app.route("/")
    def home():
        return "UrbanWear Backend Running"

    @app.route("/test-db")
    def test_db():
        try:
            db.session.execute(text("SELECT 1"))
            return "Database connected successfully!"
        except Exception as e:
            return str(e)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)