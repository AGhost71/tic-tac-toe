from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asyncio import create_task, sleep
from db import database
import logging
import os

logging.basicConfig(
    level=logging.INFO,  # Set to logging.DEBUG for more detailed output
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)
# Replace with your own values
API_ID =  os.getenv('api_id')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')


games = {}
record = database()
app = Client(os.getenv('Bot_Name'), api_id=API_ID,api_hash=API_HASH, bot_token=BOT_TOKEN)

async def game_timeout(chat_id, message_id):
    await sleep(300)  
    if chat_id in games and games[chat_id]["message_id"] == message_id:
        logger.info(f"Game in chat {chat_id} ended due to inactivity.")
        del games[chat_id]
        await app.edit_message_text(chat_id, message_id, "Game has ended due to inactivity.")
def create_board():
    return [' ' for _ in range(9)]

# Function to create the inline keyboard for the game
def create_keyboard(board):
    keyboard = []
    for i in range(0, 9, 3):
        row = [InlineKeyboardButton(text=board[j], callback_data=f"move_{j}") for j in range(i, i+3)]
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def check_winner(board, player):
    win_conditions = [(0, 1, 2), (3, 4, 5), (6, 7, 8),
                        (0, 3, 6), (1, 4, 7), (2, 5, 8),
                        (0, 4, 8), (2, 4, 6)]
    return any(board[a] == board[b] == board[c] == player for a, b, c in win_conditions)

async def get_username(user_id):

    user = await app.get_users(user_id)
    return user.username if user.username else user.first_name

@app.on_message(filters.command('tic-tac-toe') & filters.group)
async def handle_start_command(client, message: Message):
    if message.chat.id in games:
        logger.warning(f"User {message.from_user.id} attempted to start a game, but one is already in progress in chat {message.chat.id}.")
        await message.reply("A game is already in progress!")
    else:
        board = create_board()
        games[message.chat.id] = {
            "board": board,
            "turn": 'X',
            "message_id":None,
            "player_x": message.from_user.id,
            "player_o": None,
        }
        button = InlineKeyboardMarkup([[InlineKeyboardButton("join",callback_data="join")]])
        logger.info(f"User {message.from_user.id} initiated a Tic-Tac-Toe game in chat {message.chat.id}.")
        await client.send_message(message.chat.id,'for joining the game press the button',reply_markup=button)

@app.on_callback_query(filters.regex(r"join"))
async def handle_join(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    if chat_id not in games:
        logger.error(f"User {user_id} attempted a move in chat {chat_id}, but no game is in progress.")
        await callback_query.answer("No game is in progress.")
        return

    game = games[chat_id]

    if user_id != game["player_x"] and game["player_o"] is None:
        logger.info(f"User {user_id} joined the game as Player O in chat {chat_id}.")
        game["player_o"] = user_id
        username_x = await get_username(game["player_x"])
        await client.send_message(chat_id,f"Tic-Tac-Toe Game Started!\n{username_x} turn.", reply_markup=create_keyboard(game['board']))
        record.add_user(user_id,chat_id)
        record.add_user(game['player_x'],chat_id)
@app.on_callback_query(filters.regex(r"move_\d"))
async def handle_move(client, callback_query):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.from_user.id

    if chat_id not in games:
        logger.error(f"User {user_id} attempted a move in chat {chat_id}, but no game is in progress.")
        await callback_query.answer("No game is in progress.")
        return
    game = games[chat_id]
    board = game["board"]
    turn = game["turn"]
    if not game['message_id']:
        game["message_id"] = callback_query.message.id
        create_task(game_timeout(callback_query.message.chat.id, callback_query.message.id))
    move = int(callback_query.data.split("_")[1])
    if user_id != game["player_x"] and user_id != game["player_o"]:
        logger.warning(f"User {user_id} attempted to join an ongoing game in chat {chat_id}, but the game is already full.")
        await callback_query.answer("You are not part of this game.")
        return
    if (turn == 'X' and user_id != game["player_x"]) or (turn == 'O' and user_id != game["player_o"]):
        logger.warning(f"User {user_id} tried to make a move out of turn in chat {chat_id}.")
        await callback_query.answer("It's not your turn!")
        return

    if board[move] == ' ':
        user1 = game["player_x"] if turn == 'X' else game["player_o"]
        user2 = game["player_o"] if turn == 'X' else game["player_x"]
        board[move] = turn
        if check_winner(board, turn):
            logger.info(f"Player {turn} ({await get_username(user1)}) won the game in chat {chat_id}.")
            await callback_query.message.edit_text(f"{await get_username(user1)} wins!", reply_markup=create_keyboard(board))
            record.update_record(user1,chat_id,True)
            record.update_record(user2,chat_id,False)
            del games[chat_id]
        elif ' ' not in board:
            logger.info(f"Game in chat {chat_id} ended in a tie.")
            await callback_query.message.edit_text("It's a tie!", reply_markup=create_keyboard(board))
            record.update_record(user1,chat_id,False)
            record.update_record(user2,chat_id,False)
            del games[chat_id]
        else:
            logger.info(f"It is now Player {game['turn']}'s turn in chat {chat_id}.")
            game["turn"] = 'O' if turn == 'X' else 'X'
            await callback_query.message.edit_text(f"{await get_username(user2)}'s turn.", reply_markup=create_keyboard(board))
    else:
        logger.warning(f"User {user_id} attempted an invalid move in chat {chat_id}.")
        await callback_query.answer("Invalid move, try again.")
@app.on_message(filters.command('record') & filters.group)
async def show_records(client, message):
    records = record.chat_record(message.chat.id)
    text = ''
    records = sorted(records,key=lambda x:x[4])
    for r in records:
        user = await get_username(r[1])
        text += f'\n {user} games = {r[3]}  wins = {r[4]}'
    await client.send_message(message.chat.id,text)
    logger.info(f"User {message.from_user.id} in {message.chat.id} get records.")

app.run()
