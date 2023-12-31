from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configuration for SQLite database
DATABASE_URL = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) # to make the URL compatible with SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Bet(db.Model):
    __tablename__ = 'bet'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify(error=str(e)), 500

@app.route('/')
def index():
    return "Welcome to the Bets Tracker!"

@app.route('/add_bet', methods=['POST'])
def add_bet():
    data = request.json
    name = data.get('name')
    amount = data.get('amount')
    winnings = data.get('winnings', 0)

    new_bet = Bet(name=name, amount=amount, winnings=winnings)
    db.session.add(new_bet)
    db.session.commit()

    return jsonify({"message": "Bet added successfully!"}), 201

@app.route('/get_bets', methods=['GET'])
def get_bets():
    bets = Bet.query.all()
    return jsonify([{
        "id": bet.id,
        "name": bet.name,
        "amount": bet.amount,
        "winnings": bet.winnings,
        "date": bet.date
    } for bet in bets]), 200

@app.route('/remove_bet/<int:bet_id>', methods=['DELETE'])
def remove_bet(bet_id):
    bet = Bet.query.get(bet_id)
    if not bet:
        return jsonify({"message": "Bet not found!"}), 404
    db.session.delete(bet)
    db.session.commit()
    return jsonify({"message": "Bet removed successfully!"}), 200

if __name__ == "__main__":
    app.run(debug=True)
