import random

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

if __name__ == '__main__':
    """Main function to play Blackjack."""
    deck = create_deck()
    player_hand, dealer_hand, deck = get_initial_hands(deck)

    print("\nYour hand:")
    print(display_hand(player_hand))
    print("Dealer's hand:")
    print(display_hand(dealer_hand, hidden=True))

    # Player's turn
    while True:
        player_value = calculate_hand_value(player_hand)
        if player_value > BLACKJACK_VALUE:
            print("\nYou busted! Dealer wins.")
            exit()
        move = input("\nDo you want to [hit] or [stand]? ").lower()
        if move == 'hit':
            player_hand.append(deck.pop())
            print("\nYour hand:")
            print(display_hand(player_hand))
        elif move == 'stand':
            break
        else:
            print("Invalid input. Please type 'hit' or 'stand'.")

    # Dealer's turn
    print("\nDealer's turn:")
    print(display_hand(dealer_hand))
    dealer_hand, deck = dealer_play(dealer_hand, deck)
    print("\nDealer's hand:")
    print(display_hand(dealer_hand))

    # Determine winner
    print("\nFinal Hands:")
    print("Your hand:", display_hand(player_hand))
    print("Dealer's hand:", display_hand(dealer_hand))

    winner = determine_winner(player_hand, dealer_hand)
    if winner == 'player':
        print("\nYou win!")
    elif winner == 'dealer':
        print("\nDealer wins!")
    else:
        print("\nIt's a tie!")
