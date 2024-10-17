import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from  checkWord import  checkWord
from aiogram.filters import Command
from transliterate import to_latin, to_cyrillic

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "7561833317:AAErJUMSThTBuAfJ2PxwoBbU40tCkneWuGw"

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command(commands='start'))
async def start(message: types.Message):
    await message.answer("Uz imlo botiga xush Kelibsiz!")

@dp.message(Command(commands='help'))
async def help(message: types.Message):
    await message.answer("Ushbu botdan foydalanish uchun so'z yuboring)")

@dp.message()
async def checkImlo(message: types.Message):
    words = message.text.split()
    for word in words:
        is_latin = word.isascii()  # Check if the word is in Latin script

        if is_latin:
            word_in_cyrillic = to_cyrillic(word)  # Convert to Cyrillic for checking
        else:
            word_in_cyrillic = word  # Already in Cyrillic, no need to convert

        # Check the word using the checkWord function
        result = checkWord(word_in_cyrillic)

        # Generate response based on the result
        if result['available']:
            response = f"✅ {word.capitalize()}"  # Use the original word (either Latin or Cyrillic)
        else:
            response = f"❌ {word.capitalize()}\n"
            for text in result['matches']:
                response += f"✅ {text.capitalize()}\n"

        # Return the response in the original script
        if is_latin:
            await message.answer(to_latin(response))  # Convert the response back to Latin
        else:
            await message.answer(response)  # Already in Cyrillic, no need to convert


async def main():
    # Fetch and discard all pending updates (if you want to skip them)
    await bot.delete_webhook(drop_pending_updates=True)

    # Start polling
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
