from flask import Flask
from routes.auth_routes import auth_bp
from routes.activity_routes import activity_bp

app = Flask(__name__)
app.secret_key = "secret123"

app.register_blueprint(auth_bp)
app.register_blueprint(activity_bp)

if __name__ == "__main__":
    app.run(debug=True)