import asyncio
import json

from aiogram import Bot, Dispatcher,F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = "8774784555:AAHn3GJl93oNc24WLa5EWnGWeTT1F9APFks"
ADMIN_ID = 7440303923
CHANNEL_USERNAME = "@kino_izlaydi"


bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

dp = Dispatcher()


# STATE
class AddMovie(StatesGroup):
    waiting_for_name = State()
    waiting_for_language = State()
    waiting_for_genre = State()


# JSON o'qish
def load_movies():
    with open("movies.json", "r") as file:
        return json.load(file)


# JSON yozish
def save_movies(data):
    with open("movies.json", "w") as file:
        json.dump(data, file, indent=4)


# START
# START
@dp.message(Command("start"))
async def start(message: Message):

    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Kanalga obuna bo'lish",
                    url="https://t.me/kino_izlaydi"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Kanalga obuna bo'lish",
                    url="https://t.me/+2F_jpYYFVhEwMThi"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Kanalga obuna bo'lish",
                    url="https://t.me/+2F_jpYYFVhEwMThi"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Tekshirish",
                    callback_data="check_sub"
                )
            ]
        ]
    )

    await message.answer(
        "📢 Botdan foydalanish uchun kanalga obuna bo'ling.",
        reply_markup=button
    )


# OBUNA TEKSHIRISH
@dp.callback_query(F.data == "check_sub")
async def check_sub(callback: CallbackQuery):

    user_id = callback.from_user.id

    member = await bot.get_chat_member(
        chat_id=CHANNEL_USERNAME,
        user_id=user_id
    )

    if member.status in ["member", "administrator", "creator"]:

        await callback.message.answer(
            "✅ Obuna tasdiqlandi.\n🎬 Endi kino kodini yuboring."
        )

    else:

        await callback.message.answer(
            "❌ Avval kanalga obuna bo'ling."
        )

    await callback.answer()

# VIDEO QABUL QILISH
@dp.message(lambda message: message.video is not None)
async def get_video(message: Message, state: FSMContext):

    # Faqat admin video qo'sha oladi
    if message.from_user.id != ADMIN_ID:
        await message.answer(
            "❌ Uzur, kino olish uchun kod yuboring."
        )
        return

    # Video ID saqlash
    await state.update_data(
        video_id=message.video.file_id
    )

    await message.answer(
        "🎬 Kino nomini kiriting:"
    )

    await state.set_state(
        AddMovie.waiting_for_name
    )


# KINO NOMI
@dp.message(AddMovie.waiting_for_name)
async def get_name(message: Message, state: FSMContext):

    await state.update_data(
        name=message.text
    )

    await message.answer(
        "🌐 Kino tilini kiriting:"
    )

    await state.set_state(
        AddMovie.waiting_for_language
    )


# KINO TILI
@dp.message(AddMovie.waiting_for_language)
async def get_language(message: Message, state: FSMContext):

    await state.update_data(
        language=message.text
    )

    await message.answer(
        "🎭 Kino janrini kiriting:"
    )

    await state.set_state(
        AddMovie.waiting_for_genre
    )


# KINO JANRI
@dp.message(AddMovie.waiting_for_genre)
async def get_genre(message: Message, state: FSMContext):

    data = await state.get_data()

    movies = load_movies()

    movie_id = str(len(movies) + 1)

    movies[movie_id] = {
        "video": data["video_id"],
        "name": data["name"],
        "language": data["language"],
        "genre": message.text
    }

    save_movies(movies)

    await message.answer(
        f"✅ Kino saqlandi\n🆔 Kod: {movie_id}"
    )

    await state.clear()


# KOD ORQALI KINO OLISH
@dp.message()
async def send_movie(message: Message):

    if not message.text:
        return

    movies = load_movies()

    code = message.text

    if code in movies:

        movie = movies[code]

        await message.answer_video(
            video=movie["video"]
        )

        text = (
            f"🎬 Nomi: {movie['name']}\n\n"
            f"🌐 Tili: {movie['language']}\n\n"
            f"🎭 Janri: {movie['genre']}\n\n"
            f"🆔 Kodi: {code}\n\n\n"
            f"Kanal: https://t.me/kino_izlaydi"
        )

        await message.answer(text)


    else:
        await message.answer(
            "❌ Bunday kino topilmadi."
        )


# BOTNI ISHGA TUSHIRISH
async def main():
    print("Bot ishga tushdi ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
