from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import os

port = int(os.environ.get("PORT", 8080))
#st.set_option('server.address', '0.0.0.0')
st.set_option('server.port', port)
BASE_URL = "https://sports-betting-tracker-107bb77d84cc.herokuapp.com/"  # Flask server URL

def get_all_bets():
    response = requests.get(f"{BASE_URL}/get_bets")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to retrieve bets.")
        return []

def add_bet(name, amount, winnings):
    data = {
        "name": name,
        "amount": amount,
        "winnings": winnings
    }
    response = requests.post(f"{BASE_URL}/add_bet", json=data)
    if response.status_code == 201:
        st.success("Bet added successfully!")
    else:
        st.error("Failed to add bet.")

def remove_a_bet(bet_id):
    response = requests.delete(f"{BASE_URL}/remove_bet/{bet_id}")
    if response.status_code == 200:
        st.success("Bet removed successfully!")
    else:
        st.error("Failed to remove the bet.")

def build_chart(bets):

    st.subheader("Profits Over Time", divider=True)

    # Convert the bets to a DataFrame for easier manipulation
    df = pd.DataFrame(bets)

    # Convert the date from string to datetime
    df['date'] = df['date'].apply(lambda x: datetime.strptime(x, '%a, %d %b %Y %H:%M:%S %Z').strftime('%d/%m/%Y'))
    
    # Calculate the profit for each bet
    df['profit'] = df['winnings'] - df['amount']
    
    # Aggregate and get cumulative profit over time
    df.sort_values(by="date", inplace=True)
    df['cumulative_profit'] = df['profit'].cumsum()

    # Plotting
    st.line_chart(df.set_index('date')['cumulative_profit'])

def create_new_bet():
    # Display form to add a new bet
    st.subheader("Add a New Bet", divider=True)
    name = st.selectbox("Name", ["Yash", "Ved", "Chaitanya", "Ankith"])
    amount = st.number_input("Amount", min_value=0.0, step=0.01)
    winnings = st.number_input("Winnings", min_value=0.0, step=0.01)
    if st.button("Add Bet"):
        add_bet(name, amount, winnings)
    

def main():
    st.title("Sports Bets Tracker")

    bets = get_all_bets()

    build_chart(bets)

    create_new_bet()

    # Calculate how much is owed
    st.subheader("Amounts Owed", divider=True)
    total_amounts = {"Yash": 0, "Ved": 0, "Chaitanya": 0, "Ankith": 0}

    # Iterate over all bets
    for bet in bets:
        bettor = bet["name"]
        shared_cost = bet["amount"] / 4  # split the cost among all
        shared_winning = bet["winnings"] / 4  # split the winnings among all

        # Each person owes the bettor the shared cost
        for person in total_amounts.keys():
            if person != bettor:
                total_amounts[person] -= shared_cost  # Each non-bettor owes the bettor
                total_amounts[person] += shared_winning  # But also gets a share of the winnings

    # Display amounts owed
    for person, amount in total_amounts.items():
        st.subheader(f"{person} Summary:")
        if amount > 0:
            st.write(f"Total amount {person} is owed: ${amount}")
        elif amount < 0:
            st.write(f"Total amount {person} owes: ${-amount}")
        else:
            st.write(f"{person} is settled with everyone.")

        # Details of amounts owed to/from others
        for other_person in total_amounts.keys():
            if other_person != person:
                other_person_bets = [bet for bet in bets if bet["name"] == other_person]
                for bet in other_person_bets:
                    individual_owed = (bet["amount"] - bet["winnings"]) / 4
                    if individual_owed > 0:
                        st.write(f"{person} owes {other_person}: ${individual_owed}")
                    elif individual_owed < 0:
                        st.write(f"{person} is owed by {other_person}: ${-individual_owed}")

    st.subheader("All Bets")
    for bet in bets:
        bet_date = datetime.strptime(bet['date'], '%a, %d %b %Y %H:%M:%S %Z')
        date_str = bet_date.strftime('%m/%d/%y')  

        # list bets
        if bet['winnings'] > 0:
            st.write(f"On {date_str}, {bet['name']} placed a bet of {bet['amount']:.2f} and won {bet['winnings']:.2f}.")
        else:
            st.write(f"On {date_str}, {bet['name']} placed a bet of {bet['amount']:.2f} and did not win.")

        # add option to delete a bet
        if st.button(f"Remove {bet['name']}'s bet of ${bet['amount']}"):
            remove_a_bet(bet['id'])


if __name__ == "__main__":
    main()
