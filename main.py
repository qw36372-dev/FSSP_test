import time
import telebot
from telebot import types

# === НАСТРОЙКИ ===
MAIN_BOT_TOKEN = "8240081744:AAFh10FoqtYtGRtpiR-
qFpBgP-pexGD04dM"
PHOTO_PATH = "welcome.jpg"  # путь к файлу картинки (логотип или фон)

# Сюда впишите ссылки или юзернеймы ботов‑тестов,
# соответствующих 11 специализациям.
SPECIALIZATION_BOTS = [
    ("ООУПДС", "https://t.me/OUPDS_fssptest_bot"),
    ("Исполнительное производство", "https://t.me/Ispolniteli_fssptest_bot"),
    ("Дознание", "https://t.me/Doznanie_fssptest_bot"),
    ("Алименты", "https://t.me/Aliment_fssptest_bot"),
    ("Исполнительный розыск и реализация имущества", "https://t.me/Rozisk_fssptest_bot"),
    ("Организация профессиональной подготовки", "https://t.me/Prof_fssptest_bot"),
    ("Организация управления и контроля", "https://t.me/OKO_fssptest_bot"),
    ("Информатизация и информационная безопасность", "https://t.me/Informatizaciya_fssptest_bot"),
    ("Кадровая работа", "https://t.me/Kadri_fssptest_bot"),
    ("Обеспечение собственной безопасности", "https://t.me/Bezopasnost_fssptest_bot"),
    ("Управленческая деятельность", "https://t.me/Starshie_fssptest_bot"),
]

# Антиспам: минимальный интервал (в секундах) между нажатиями для одного пользователя
ANTI_SPAM_INTERVAL = 2  # можно увеличить при необходимости

bot = telebot.TeleBot(MAIN_BOT_TOKEN)

# Временное хранилище последнего действия пользователя
last_user_action = {}


def is_spam(user_id: int) -> bool:
    """Простая проверка спама по времени последнего действия пользователя."""
    now = time.time()
    last_time = last_user_action.get(user_id, 0)
    if now - last_time < ANTI_SPAM_INTERVAL:
        return True
    last_user_action[user_id] = now
    return False


def main_menu_keyboard() -> types.InlineKeyboardMarkup:
    """Создает инлайн‑клавиатуру с 11 специализациями."""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = []

    for idx, (title, _) in enumerate(SPECIALIZATION_BOTS, start=1):
        # callback_data включает индекс специализации
        btn = types.InlineKeyboardButton(
            text=f"{idx}. {title}",
            callback_data=f"spec_{idx}"
        )
        buttons.append(btn)

    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=["start"])
def send_welcome(message: types.Message):
    """Отправка стартовой страницы с картинкой и приветственным текстом."""
    user_id = message.from_user.id
    if is_spam(user_id):
        # Мягкое игнорирование или короткое сообщение
        bot.reply_to(message, "Слишком часто. Попробуйте чуть позже.")
        return

    welcome_text = (
        "Привет! Добро пожаловать в тестовый бот ФССП\n\n"
        "Сейчас здесь пройдёт тест, по вашему профессиональному профилю.\n\n"
        "Выберите вашу специализацию ниже ⏬"
    )

    # Если есть фото, отправляем его с подписью и клавиатурой
    try:
        with open(PHOTO_PATH, "rb") as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=welcome_text,
                reply_markup=main_menu_keyboard()
            )
    except FileNotFoundError:
        # Если фото не найдено, отправить только текст
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=main_menu_keyboard()
        )


@bot.callback_query_handler(func=lambda call: call.data.startswith("spec_"))
def handle_specialization(call: types.CallbackQuery):
    """Обработка нажатий на кнопки специализаций."""
    user_id = call.from_user.id
    if is_spam(user_id):
        bot.answer_callback_query(call.id, "Слишком часто. Подождите немного.")
        return

    # Получаем индекс специализации
    try:
        idx = int(call.data.split("_")[1]) - 1
    except (IndexError, ValueError):
        bot.answer_callback_query(call.id, "Ошибка выбора.")
        return

    if 0 <= idx < len(SPECIALIZATION_BOTS):
        title, link = SPECIALIZATION_BOTS[idx]
        text = (
            f"Вы выбрали: {title}\n\n"
            f"Перейдите по ссылке на тестовый бот по этой специализации:\n{link}"
        )
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, text)
    else:
        bot.answer_callback_query(call.id, "Неверная специализация.")


# Дополнительно можно защитить любые текстовые сообщения от частого спама
@bot.message_handler(content_types=["text"])
def handle_all_text(message: types.Message):
    user_id = message.from_user.id
    if is_spam(user_id):
        bot.reply_to(message, "Слишком много сообщений. Подождите немного.")
        return
    bot.reply_to(message, "Нажмите /start, чтобы открыть список специализаций.")


if __name__ == "__main__":
    print("Бот запущен...")
    bot.infinity_polling()

# Обязательная для работы бота часть. Не дает боту перейти в спящий режим
bot.polling(none_stop=True, interval=0) 
