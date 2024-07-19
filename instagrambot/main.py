import os
import shutil
from uuid import uuid4
import instaloader
from moviepy.editor import VideoFileClip
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
import logging
from buttons.default import *
from buttons.inline import *
from state import *
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from database import add_user, get_user, add_link, get_links, get_registration_time, delete_user, delete_links, get_all_users, get_bot_stats

L = instaloader.Instaloader()

logging.basicConfig(level=logging.INFO)

TOKEN = '7414116835:AAEQ__efrvIl7NmBBk1-a-LvzKqvNNAzTWU'
ADMIN_CHAT_ID = 1921911753
ADMIN_PASSWORD = '08080707'

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    if user:
        await message.reply(f"Salom <b>{user[1]}</b> Havolani joylang 🔗", reply_markup=ReplyKeyboardRemove())
        await state.finish()
    else:
        await message.answer("Kerakli tilni tanlang:", reply_markup=get_language)
        await state.set_state("choose_language")

@dp.callback_query_handler(lambda c: c.data.startswith('lang_'), state="choose_language")
async def process_language_selection(callback_query: types.CallbackQuery, state: FSMContext):
    lang_code = callback_query.data.split('_')[1]
    if lang_code == 'uz':
        await bot.send_message(callback_query.from_user.id, "Siz O'zbek tilini tanladingiz.\nTo'liq ismingizni kiriting:")
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=None)
    elif lang_code == 'ru':
        await bot.send_message(callback_query.from_user.id, "Вы выбрали русский язык.\nВведите ваше полное имя:")
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=None)
    elif lang_code == 'eng':
        await bot.send_message(callback_query.from_user.id, "You selected English.\nPlease enter your full name:")
        await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, reply_markup=None)

    await Registration.full_name.set()
    await state.update_data(language=lang_code)

@dp.message_handler(state=Registration.full_name)
async def name_handler(message: types.Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)
    data = await state.get_data()
    lang_code = data.get('language')

    if lang_code == 'uz':
        prompt = "Telefon raqamingizni yuboring:" 
    elif lang_code == 'ru':
        prompt = "Отправьте ваш номер телефона:"
    else:
        prompt = "Please send your phone number:"

    await message.answer(prompt, reply_markup=phone_button)
    await Registration.phone_number.set()

@dp.message_handler(content_types=types.ContentTypes.CONTACT, state=Registration.phone_number)
async def phone_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number

    user_data = await state.get_data()
    full_name = user_data['full_name']

    add_user(user_id, full_name, phone_number)
    lang_code = user_data.get('language')

    if lang_code == 'uz':
        msg = "Tabriklaymiz siz ro'yxatdan muvaffaqiyatli o'tdingiz!\nBotimizdan bemalol foydalanishingiz mumkin!!!\nIltimos botimizdan foydalanoyatganingizda biroz kuting!!!"
    elif lang_code == 'ru':
        msg = "Поздравляем, вы успешно зарегистрировались!\nВы можете использовать наш бот!"
    else:
        msg = "Congratulations, you have successfully registered!\nYou can use our bot now!"

    await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    await state.finish()

@dp.message_handler(commands=['myregistration'])
async def registertime_handler(message: types.Message):
    user_id = message.from_user.id
    registration_time = get_registration_time(user_id)
    
    if registration_time:
        await message.answer(f"Sizning ro'yxatdan o'tgan vaqtingiz: {registration_time}")
    else:
        await message.answer("Siz hali ro'yxatdan o'tmagansiz. Iltimos, /start buyrug'ini bosing va ro'yxatdan o'ting!")

@dp.message_handler(lambda message: 'instagram.com' in message.text)
async def handle_instagram_url(message: types.Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if not user:
        await message.answer("Iltimos, avval ro'yxatdan o'ting /start buyrug'idan foydalaning!")
        return
    
    chat_id = message.chat.id
    url = message.text
    shortcode = url.split("/")[-2]
    try:
        target_directory = str(uuid4())
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target=target_directory)
        video_file = next(os.path.join(target_directory, f) for f in os.listdir(target_directory) if f.endswith('.mp4'))
        
        await bot.send_message(chat_id, 'Video yuklanmoqda...')
        with open(video_file, 'rb') as video:
            await bot.send_video(chat_id, video, caption="Ushbu video @uzinstamagbot orqali yuklandi.")
        
        await bot.send_message(chat_id, 'Audio yuklanmoqda...')
        audio_path = extract_audio(video_file, target_directory)
        with open(audio_path, 'rb') as audio:
            await bot.send_audio(chat_id, audio, caption="Ushbu audio @uzinstamagbot orqali yuklandi.")
            await bot.send_photo(chat_id, "https://t4.ftcdn.net/jpg/04/37/16/01/360_F_437160139_2VTiftCalZrVajUiiu3e49474wu76knz.jpg", caption="Iltimos ishimizni baholang", reply_markup=rate_it)
            await Registration.rate_it_user.set()
        
        shutil.rmtree(target_directory)
        
        add_link(user_id, url)
    except Exception as e:
        await bot.send_message(chat_id, f'Kechirasiz Serverda Xatolik yuz berdi.\nIltimos keyinroq albatda urinib ko\'ring')

def extract_audio(video_file, target_directory):
    video_clip = VideoFileClip(video_file)
    audio_path = os.path.join(target_directory, 'audio.mp3')
    video_clip.audio.write_audiofile(audio_path)
    video_clip.close()
    return audio_path

@dp.callback_query_handler(text="like", state=Registration.rate_it_user)
async def get_inline_btn(query:types.CallbackQuery, state: FSMContext):  
    user_id = query.from_user.id  
    user = get_user(user_id)
    await query.message.reply(f"Hurmatli <b>{user[1]}</b>\nBizning botni tanlaganingiz uchun raxmat 😉")
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=None)
    await state.finish()

@dp.callback_query_handler(text="dislike", state=Registration.rate_it_user)
async def get_inline_btn(query:types.CallbackQuery):  
    user_id = query.from_user.id  
    user = get_user(user_id)
    await query.message.reply(f"Hurmatli <b>{user[1]}</b>\nBotimizda noqulayliklar va kamchiliklarni albatta yozib keting 👇")
    await bot.edit_message_reply_markup(chat_id=query.message.chat.id, message_id=query.message.message_id, reply_markup=None)
    await Registration.rate_it.set()

@dp.message_handler(content_types=types.ContentType.TEXT, state=Registration.rate_it)
async def qaytarish(message:types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)
    text = message.text
    
    feedback_message = (
        f"Foydalanuvchi Fikr-mulohazalari 👇\n"
        f"Ismi: {user[1]}\n"
        f"Telefon raqami: {user[2]}\n"
        f"Fikr-mulohazasi: {text}"
    )
    
    await bot.send_message(ADMIN_CHAT_ID, feedback_message)
    await message.answer("Qoldirgan izohingiz uchun raxmat!\nTez orada muammo va kamchiliklar bartaraf etiladi!!!")
    await state.finish()

@dp.message_handler(commands=['myhistory'])
async def history_handler(message: types.Message):
    user_id = message.from_user.id
    links = get_links(user_id)
    
    if not links:
        await message.answer("Siz hali hech qanday havola yubormagansiz.")
    else:
        history = "\n".join([link[0] for link in links])
        await message.answer(f"Sizning yuborgan havolalaringiz:\n\n{history}")

@dp.message_handler(commands=['exit'])
async def clear_handler(message: types.Message):
    user_id = message.from_user.id
    
    delete_links(user_id)
    delete_user(user_id)
    
    await message.answer("Ma'lumotlaringiz muvaffaqiyatli o'chirildi.")

@dp.message_handler(commands=['help'])
async def start_handler(message: types.Message):
    await message.answer("""<b>Hurmatli foydalanuvchi</b> Ushbu bot sizga kerak bo'lgan rasm, video, audiolarni qiyinchiliklarsiz yuklab beradi\nBotimizdagi qulayliklar bilan tanishing 👇\n\n/start 📌- Boshlashingiz uchun, Botni ishga tushirishingiz uchun\n\n/myregistration 🧾 - Ro'yxatdan o'tgan yil, oy, sana va vaqtlarni taqdim etadi\n\n/myhistory 📄 - Buyrug'i orqali botimizga joylagan havolalaringiz tarixini taqdim etadi\n\n/clear 🗑 - Botdan ro'yxatdan o'tganingizni va barcha havolalaringizni o'chiradi\n\n
<b>Уважаемый пользователь!</b> Этот бот без труда загрузит нужные вам изображения, видео, аудио\nПознакомьтесь с возможностями нашего бота 👇\n\n/start 📌- Для начала запустите бота \n\n/myregistration 🧾 - Предоставляет год, месяц, дату и время регистрации.\n\n/myhistory 📄 - Предоставляет историю ссылок, которые вы разместили в нашем боте с помощью команды\n\n/clear 🗑 - Удаляет вашу регистрацию и все ссылки, которые вы отправили боту\n\n
<b>Dear user!</b> This bot will easily download the images, videos, audio you need\nGet to know the capabilities of our bot 👇\n\n/start 📌- First, launch the bot\n\n/myregistration 🧾 - Provides the year, month, date and time of registration.\n\n/myhistory 📄 - Provides the history of links that you placed in our bot using the command\n\n/clear 🗑 - Deletes your registration and all the links you have sent to the bot.""")

@dp.message_handler(commands=['admin'])
async def admin_handler(message: types.Message):
    await message.answer("Parolni kiriting:")
    await Admin.password.set()

@dp.message_handler(state=Admin.password)
async def password_handler(message: types.Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await message.answer("<b>Mutalov Nuriddin</b> xush kelibsiz!", reply_markup=admin_buttons)
        await state.finish()
    else:
        await message.answer("Noto'g'ri parol, iltimos qaytadan urinib ko'ring.")

@dp.callback_query_handler(lambda c: c.data == 'view_users')
async def view_users(callback_query: types.CallbackQuery):
    users = get_all_users()
    if users:
        users_list = "\n".join([f"{i+1}. {user[1]} - {user[2]}" for i, user in enumerate(users)])
        await bot.send_message(callback_query.from_user.id, f"Foydalanuvchilar ro'yxati:\n\n{users_list}")
    else:
        await bot.send_message(callback_query.from_user.id, "Hech qanday foydalanuvchi topilmadi.")

@dp.callback_query_handler(lambda c: c.data == 'view_stats')
async def view_stats(callback_query: types.CallbackQuery):
    stats = get_bot_stats()
    await bot.send_message(callback_query.from_user.id, f"Bot statistikasi:\n\n{stats}")

async def on_start_up(dp):
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot ishga tushdi!')

async def on_shutdown(dp):
    await bot.send_message(chat_id=ADMIN_CHAT_ID, text='Bot o\'chdi!')

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start_up, on_shutdown=on_shutdown)
