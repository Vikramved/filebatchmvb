import os

import pymongo

from pyrogram import Client, filters

from pyrogram.types import Message

# MongoDB connection setup

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")

db = mongo_client["file_batch_bot"]

subscribers_collection = db["subscribers"]

# Telegram bot setup

api_id = os.environ.get("API_ID")

api_hash = os.environ.get("API_HASH")

bot_token = os.environ.get("BOT_TOKEN")

app = Client("file_batch_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Command to start the bot

@app.on_message(filters.command("start"))

def start_command(_, message: Message):

    chat_id = message.chat.id

    # Check if the user is already subscribed

    if subscribers_collection.find_one({"chat_id": chat_id}):

        message.reply_text("You are already subscribed!")

    else:

        subscribers_collection.insert_one({"chat_id": chat_id})

        message.reply_text("Welcome! You have subscribed to the bot.")

# Command to create a file batch (restricted to admins)

@app.on_message(filters.command("create_batch") & filters.chat(admins=True))

def create_batch_command(_, message: Message):

    # Check if the user is subscribed

    chat_id = message.chat.id

    if not subscribers_collection.find_one({"chat_id": chat_id}):

        message.reply_text("You are not subscribed to the bot.")

        return

    # Check if files, photos, and text messages are present in the message

    if not message.document and not message.photo and not message.text:

        message.reply_text("Please upload files, photos, or send text messages to batch.")

        return

    # Get all the content from the message

    content = []

    if message.document:

        content.append(message.document.file_id)

    if message.photo:

        content.extend([photo.file_id for photo in message.photo])

    if message.text:

        content.append(message.text)

    # Perform batch logic here

    # ...

    # Get the batched message

    batched_message = "This is the batched message."

    # Reply with the batched message and provide a link to it

    message.reply_text("Batched message: {}".format(batched_message))

    message.reply_text("Click [here](https://example.com/batch_link) to view the batched message.")

# Command to force subscription

@app.on_message(filters.command("force_subscribe") & filters.chat(admins=True))

def force_subscribe_command(_, message: Message):

    chat_id = message.chat.id

    user_ids = [member.user.id for member in message.chat.get_members()]

    subscribed_users = subscribers_collection.find({}, {"chat_id": 1})

    for user in subscribed_users:

        if user["chat_id"] not in user_ids:

            subscribers_collection.delete_one({"chat_id": user["chat_id"]})

    message.reply_text("Subscription enforced.")

# Run the bot

if __name__ == "__main__":

    app.run()

