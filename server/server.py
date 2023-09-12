from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuration for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    winnings = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

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
    with app.app_context():  # Pushes an application context manually
        db.create_all()
    app.run(debug=True)
