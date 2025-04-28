from flask import Flask, render_template, session
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this!
socketio = SocketIO(app)

# Constants for card values and game rules
CARD_VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}
DEALER_STAND_VALUE = 17
BLACKJACK_VALUE = 21

def create_deck():
    """Create a shuffled deck of cards."""
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    deck = [(rank, suit) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

def card_value(card):
    """Return the value of a card."""
    return CARD_VALUES[card[0]]

def calculate_hand_value(hand):
    """Calculate the value of a hand, adjusting for Aces."""
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card[0] == 'A')
    while value > BLACKJACK_VALUE and aces:
        value -= 10
        aces -= 1
    return value

def display_hand(hand, hidden=False):
    """Return a list of card strings.  Hide the first card if hidden is True."""
    if hidden:
        return ["Hidden", f"{hand[1][0]} of {hand[1][1]}"]
    else:
        return [f"{rank} of {suit}" for rank, suit in hand]

def get_initial_hands(deck):
    """Deal the initial hands for a new game."""
    player_hand = [deck.pop(), deck.pop()]
    dealer_hand = [deck.pop(), deck.pop()]
    return player_hand, dealer_hand, deck

def determine_winner(player_hand, dealer_hand):
    """Determine the winner of the game."""
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)

    if player_value > BLACKJACK_VALUE:
        return 'dealer'  # Player busts
    elif dealer_value > BLACKJACK_VALUE:
        return 'player'  # Dealer busts
    elif player_value > dealer_value:
        return 'player'
    elif dealer_value > player_value:
        return 'dealer'
    else:
        return 'tie'

def dealer_play(dealer_hand, deck):
    """Dealer's strategy: Hit until 17 or more."""
    while calculate_hand_value(dealer_hand) < DEALER_STAND_VALUE:
        dealer_hand.append(deck.pop())
    return dealer_hand, deck

@app.route('/')
def index():
    """Render the main game page."""
    if 'game' not in session:
        session['game'] = {'deck': create_deck(),
                           'player_hand': [],
                           'dealer_hand': [],
                           'game_over': False,
                           'message': '',
                           'player_score': 0,  # Add scores
                           'dealer_score': 0}
    game = session['game']
    if not game['player_hand'] and not game['dealer_hand']:
        game['player_hand'], game['dealer_hand'], game['deck'] = get_initial_hands(game['deck'])

    return render_template('blackjack.html',
                           player_hand=display_hand(game['player_hand']),
                           dealer_hand=display_hand(game['dealer_hand'], hidden=True),
                           message=game['message'],
                           game_over=game['game_over'],
                           player_score=game['player_score'], # Pass scores
                           dealer_score=game['dealer_score'])

@socketio.on('player_hit')
def handle_player_hit():
    """Handle the player's 'hit' action."""
    game = session['game']
    if game['game_over']:
        return  # Game is over, ignore moves

    game['player_hand'].append(game['deck'].pop())
    player_value = calculate_hand_value(game['player_hand'])

    if player_value > BLACKJACK_VALUE:
        game['game_over'] = True
        game['message'] = 'You busted! Dealer wins!'
        game['dealer_score'] += 1
        emit('update_game', {
            'player_hand': display_hand(game['player_hand']),
            'dealer_hand': display_hand(game['dealer_hand'], hidden=False),  # Show all dealer cards
            'message': game['message'],
            'game_over': game['game_over'],
            'player_value': player_value,
            'dealer_value': calculate_hand_value(game['dealer_hand']),
            'player_score': game['player_score'],
            'dealer_score': game['dealer_score']
        }, broadcast=True)
        session['game'] = game

    else:
        emit('update_game', {
            'player_hand': display_hand(game['player_hand']),
            'dealer_hand': display_hand(game['dealer_hand'], hidden=True),
            'message': game['message'],
            'game_over': game['game_over'],
            'player_value': player_value,
            'dealer_value': calculate_hand_value(game['dealer_hand']),
            'player_score': game['player_score'],
            'dealer_score': game['dealer_score']
        }, broadcast=True)
        session['game'] = game

@socketio.on('player_stand')
def handle_player_stand():
    """Handle the player's 'stand' action."""
    game = session['game']
    if game['game_over']:
        return  # Game is over, ignore moves

    game['game_over'] = True
    game['dealer_hand'], game['deck'] = dealer_play(game['dealer_hand'], game['deck'])
    player_value = calculate_hand_value(game['player_hand'])
    dealer_value = calculate_hand_value(game['dealer_hand'])
    winner = determine_winner(game['player_hand'], game['dealer_hand'])

    if winner == 'player':
        game['message'] = 'You win!'
        game['player_score'] += 1
    elif winner == 'dealer':
        game['message'] = 'Dealer wins!'
        game['dealer_score'] += 1
    else:
        game['message'] = "It's a tie!"

    emit('update_game', {
        'player_hand': display_hand(game['player_hand']),
        'dealer_hand': display_hand(game['dealer_hand'], hidden=False),  # Show all dealer cards
        'message': game['message'],
        'game_over': game['game_over'],
        'player_value': player_value,
        'dealer_value': dealer_value,
        'player_score': game['player_score'],
        'dealer_score': game['dealer_score']
    }, broadcast=True)
    session['game'] = game

@socketio.on('start_new_game')
def handle_new_game():
    """Start a new game."""
    session['game'] = {'deck': create_deck(),
                       'player_hand': [],
                       'dealer_hand': [],
                       'game_over': False,
                       'message': '',
                       'player_score': session['game']['player_score'],  # Keep scores
                       'dealer_score': session['game']['dealer_score']}
    game = session['game']
    game['player_hand'], game['dealer_hand'], game['deck'] = get_initial_hands(game['deck'])

    emit('update_game', {
        'player_hand': display_hand(game['player_hand']),
        'dealer_hand': display_hand(game['dealer_hand'], hidden=True),
        'message': game['message'],
        'game_over': game['game_over'],
        'player_value':  calculate_hand_value(game['player_hand']),
        'dealer_value':  calculate_hand_value(game['dealer_hand']),
        'player_score': game['player_score'],
        'dealer_score': game['dealer_score']
    }, broadcast=True)
    session['game'] = game

if __name__ == '__main__':
    socketio.run(app, debug=True)
