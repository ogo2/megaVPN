import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from config import *
from functions import create_vpn_profile, is_valid_client_name

# Инициализация бота
bot = Bot(token=BOT_TOKEN)

# Инициализация диспетчера с памятью FSM
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class Form(StatesGroup):
    waiting_for_client_name = State()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот для создания VPN профилей. Используй команду /get_vpn, чтобы получить свой профиль.")

@dp.message(Command("get_vpn"))
async def cmd_get_vpn(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите желаемое имя клиента (только буквы, цифры и _):")
    await state.set_state(Form.waiting_for_client_name)

@dp.message(Form.waiting_for_client_name, F.text)
async def process_client_name(message: Message, state: FSMContext):
    client_name = message.text.strip()

    if not is_valid_client_name(client_name):
        await message.answer("Имя клиента содержит недопустимые символы. Пожалуйста, введите другое имя:")
        return

    await message.answer("Создаю ваш VPN профиль, это может занять несколько секунд...")

    profile_path = create_vpn_profile(client_name)
    if profile_path:
        vpn_file = FSInputFile(profile_path)
        await message.answer_document(vpn_file, caption="Ваш VPN профиль готов. Используйте его в вашем OpenVPN клиенте.")
    else:
        await message.answer("Произошла ошибка при создании вашего профиля VPN.")

    await state.clear()

async def main():
    # Удалить старые обновления
    await bot.delete_webhook(drop_pending_updates=True)

    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
