# Telegram Tic-Tac-Toe Bot

This is a Telegram bot that allows users to play Tic-Tac-Toe in group chats. The bot is built using the [Pyrogram](https://docs.pyrogram.org/) library and utilizes SQLite for keeping track of game records.

## Features

- **Interactive Tic-Tac-Toe Game:** Users can start and join a Tic-Tac-Toe game directly in the chat.
- **Turn-Based Play:** The bot ensures that players take turns correctly and enforces game rules.
- **Persistent Records:** Keeps track of the total games played and wins for each player in the group.
- **Inactivity Timeout:** Games automatically end if no moves are made within 5 minutes.

## Installation

### Prerequisites

- Python 3.11+
- Telegram Bot API token from [BotFather](https://core.telegram.org/bots#botfather)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AGhost71/tic-tac-toe.git
   cd telegram-tic-tac-toe-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables:**

   Create a `.env` file in the root directory of your project and add the following:

   ```bash
   API_ID=<your_api_id>
   API_HASH=<your_api_hash>
   BOT_TOKEN=<your_bot_token>
   Bot_Name=<your_bot_name>
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

## Usage

### Start a Game

- **/tic-tac-toe:** Start a new game in the group chat. Other users can join the game by clicking the "Join" button.

### Play the Game

- Players make their moves by clicking the buttons on the inline keyboard.
- The bot will notify users whose turn it is, and will announce the winner or if the game ends in a tie.

### Show Records

- **/record:** Display the list of players in the chat along with their total games and wins.

## Code Overview

### `main.py`

- Contains the main bot logic, including handling commands, managing the game state, and interacting with users.
- Uses `pyrogram` for interacting with the Telegram API.

### `db.py`

- Handles database operations using SQLite, including adding users, updating records, and retrieving game statistics.

## Logging

The bot includes logging to track activities such as starting games, player moves, and errors. You can adjust the logging level in `main.py` by modifying the `logging.basicConfig` settings.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request for any changes.

1. Fork the repo.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.
