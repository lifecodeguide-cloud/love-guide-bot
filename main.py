import os
import asyncio

from urllib.parse import quote
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from calculators import (
    parse_date,
    calculate_soul,
    calculate_expression,
    calculate_destiny,
    calculate_varna,
    calculate_compatibility_percent,
)

from final_texts import (
    WELCOME_TEXT,
    ASK_FIRST_DATE_TEXT,
    ASK_SECOND_NAME_TEXT,
    ASK_SECOND_DATE_TEXT,
    WRONG_DATE_TEXT,
    CHECK_DATA_TEXT,
    CONFIRM_DATA_BUTTON_TEXT,
    RESTART_BUTTON_TEXT,
    FULL_ACCESS_BUTTON_TEXT,
    NEXT_BUTTON_TEXT,
    ANALYZING_TEXT,
    COMPATIBILITY_PREVIEW_BUTTON_TEXT,
    COMPATIBILITY_PREVIEW_TEXT,
    IMPORTANT_BUTTON_TEXT,
    IMPORTANT_RELATIONSHIPS_TEXT,
    FINAL_THANKS_TEXT,
    GIFT_BUTTON_TEXT,
    OTHER_PAIR_BUTTON_TEXT,
    LIFE_GUIDE_BUTTON_TEXT,
)

from love_profile_texts import (
    EXPRESSION_INTRO_TEXT,
    LOVE_PROFILE_TEXTS,
    SAME_EXPRESSION_INTRO,
)

from compatibility_texts import COMPATIBILITY_TEXTS

from soul_texts import (
    SOUL_COMPATIBILITY_INTRO,
    SOUL_COMPATIBILITY_TEXTS,
)

from destiny_compatibility_texts import (
    DESTINY_COMPATIBILITY_BUTTON_TEXT,
    DESTINY_COMPATIBILITY_INTRO,
    DESTINY_COMPATIBILITY_TEXTS,
)


PAYMENT_TEST_BUTTON_TEXT = "✅ Тест: оплата прошла"
LOVE_GUIDE_PRICE = 500
SOUL_COMPATIBILITY_BUTTON_TEXT = "🌱 Совместимость по числу души"

FIRST_PROFILE_BUTTON_TEXT = "💕 Как проявляет любовь партнёр"

FIRST_NAME_TEXT = "👇 Введите имя первого человека"
PAYMENT_SUCCESS_TEXT = "✅ Оплата прошла успешно."
SHARE_TEXT = "Нажмите кнопку ниже, чтобы поделиться ботом и забрать подарок 👇"

GIFT_PDF_LINK = (
    "https://drive.google.com/file/d/"
    "1y4akusdIYQ5bKHdIMk5GlF0Tk40ZRrmy/view?usp=sharing"
)

LIFE_GUIDE_LINK = "https://t.me/LifeGuideVitaBot?start=love"


class LoveGuideStates(StatesGroup):
    first_name = State()
    first_date = State()
    second_name = State()
    second_date = State()


def load_token():
    token = os.getenv("BOT_TOKEN")

    if token:
        return token

    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as file:
            for line in file:
                if line.startswith("BOT_TOKEN="):
                    return line.replace("BOT_TOKEN=", "").strip()

    return None


def make_pair_key(a, b):
    a = int(a)
    b = int(b)

    if a > b:
        a, b = b, a

    return f"{a}_{b}"


def get_expression_compatibility_text(expression1, expression2):
    key = make_pair_key(expression1, expression2)
    text = COMPATIBILITY_TEXTS.get(key, "")

    if isinstance(text, list):
        return "\n\n".join(text)

    return text


def get_soul_compatibility_text(soul1, soul2):
    key = make_pair_key(soul1, soul2)
    return SOUL_COMPATIBILITY_TEXTS.get(key, "")


def get_destiny_compatibility_text(destiny1, destiny2):
    key = tuple(sorted((int(destiny1), int(destiny2))))
    return DESTINY_COMPATIBILITY_TEXTS.get(key, "")


def build_first_profile_text(data):
    name1 = data["name1"]
    expression1 = data["expression1"]

    return (
        f"{name1}\n"
        f"{LOVE_PROFILE_TEXTS[expression1]}"
    )


def build_second_profile_text(data):
    name2 = data["name2"]
    expression1 = data["expression1"]
    expression2 = data["expression2"]

    if expression1 == expression2:
        return (
            f"💕 Как проявляет любовь партнёр\n"
            f"{name2}\n"
            f"{SAME_EXPRESSION_INTRO}"
        )

    return (
        f"💕 Как проявляет любовь партнёр\n"
        f"{name2}\n"
        f"{LOVE_PROFILE_TEXTS[expression2]}"
    )


def build_expression_compatibility_text(data):
    return (
        f"{get_expression_compatibility_text(data['expression1'], data['expression2'])}"
    )


def build_soul_compatibility_text(data):
    return get_soul_compatibility_text(data["soul1"], data["soul2"])


def build_destiny_compatibility_text(data):
    return get_destiny_compatibility_text(data["destiny1"], data["destiny2"])


def one_button(text, callback_data):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data=callback_data,
                )
            ]
        ]
    )


def confirm_data_buttons():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=CONFIRM_DATA_BUTTON_TEXT,
                    callback_data="confirm_data",
                )
            ],
            [
                InlineKeyboardButton(
                    text=RESTART_BUTTON_TEXT,
                    callback_data="restart_input",
                )
            ],
        ]
    )


def payment_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⭐ Оплатить 250 Stars",
                    callback_data="payment_info",
                )
            ],
            [
                InlineKeyboardButton(
                    text="💳 Оплатить PayPal — $6.99",
                    callback_data="paypal_payment",
                )
            ],
        ]
    )


def test_payment_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=PAYMENT_TEST_BUTTON_TEXT,
                    callback_data="test_payment_done",
                )
            ]
        ]
    )


def final_buttons(share_link):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Поделиться ботом",
                    url=share_link,
                )
            ],
            [
                InlineKeyboardButton(
                    text=GIFT_BUTTON_TEXT,
                    callback_data="gift_pdf",
                )
            ],
            [
                InlineKeyboardButton(
                    text=OTHER_PAIR_BUTTON_TEXT,
                    callback_data="other_pair",
                )
            ],
            [
                InlineKeyboardButton(
                    text=LIFE_GUIDE_BUTTON_TEXT,
                    url=LIFE_GUIDE_LINK,
                )
            ],
        ]
    )


bot = Bot(token=load_token())
dp = Dispatcher(storage=MemoryStorage())


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    if message.text and message.text.startswith("/start paid_"):
        paid_user_id = message.text.replace("/start paid_", "", 1).strip()

        if paid_user_id == str(message.from_user.id):
            await state.update_data(paid=True)

            await message.answer(
                PAYMENT_SUCCESS_TEXT,
                reply_markup=one_button(
                    SOUL_COMPATIBILITY_BUTTON_TEXT,
                    "show_soul_intro",
                ),
            )
            return

    await state.clear()
    await message.answer(WELCOME_TEXT)
    await state.set_state(LoveGuideStates.first_name)


@dp.message(LoveGuideStates.first_name)
async def get_first_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name1=name)

    await message.answer(ASK_FIRST_DATE_TEXT.format(name=name))
    await state.set_state(LoveGuideStates.first_date)


@dp.message(LoveGuideStates.first_date)
async def get_first_date(message: Message, state: FSMContext):
    birth_date = parse_date(message.text)

    if birth_date is None:
        await message.answer(WRONG_DATE_TEXT)
        return

    await state.update_data(date1=birth_date)

    await message.answer(ASK_SECOND_NAME_TEXT)
    await state.set_state(LoveGuideStates.second_name)


@dp.message(LoveGuideStates.second_name)
async def get_second_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name2=name)

    await message.answer(ASK_SECOND_DATE_TEXT.format(name=name))
    await state.set_state(LoveGuideStates.second_date)


@dp.message(LoveGuideStates.second_date, F.text)
async def get_second_date(message: Message, state: FSMContext):
    birth_date = parse_date(message.text)

    if birth_date is None:
        await message.answer(WRONG_DATE_TEXT)
        return

    await state.update_data(date2=birth_date)
    data = await state.get_data()

    text = CHECK_DATA_TEXT.format(
        name1=data["name1"],
        date1=data["date1"].strftime("%d.%m.%Y"),
        name2=data["name2"],
        date2=birth_date.strftime("%d.%m.%Y"),
    )

    await message.answer(
        text,
        reply_markup=confirm_data_buttons(),
    )


@dp.callback_query(F.data == "restart_input")
async def restart_input(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(FIRST_NAME_TEXT)
    await state.set_state(LoveGuideStates.first_name)
    await callback.answer()


@dp.callback_query(F.data == "confirm_data")
async def confirm_data(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    date1 = data["date1"]
    date2 = data["date2"]

    expression1 = calculate_expression(date1)
    expression2 = calculate_expression(date2)

    soul1 = calculate_soul(date1)
    soul2 = calculate_soul(date2)

    destiny1 = calculate_destiny(date1)
    destiny2 = calculate_destiny(date2)

    # Варны используются только внутри старого расчёта общего процента.
    # Пользователю они не показываются.
    varna1 = calculate_varna(date1)["main_varna"]
    varna2 = calculate_varna(date2)["main_varna"]

    percent = calculate_compatibility_percent(
        varna1,
        varna2,
        expression1,
        expression2,
    )

    await state.update_data(
        expression1=expression1,
        expression2=expression2,
        soul1=soul1,
        soul2=soul2,
        destiny1=destiny1,
        destiny2=destiny2,
        percent=percent,
        paid=False,
    )

    await callback.message.answer(ANALYZING_TEXT)
    await callback.message.answer(EXPRESSION_INTRO_TEXT)

    data = await state.get_data()

    await callback.message.answer(
        build_first_profile_text(data),
        reply_markup=one_button(
            FIRST_PROFILE_BUTTON_TEXT,
            "show_second_profile",
        ),
    )

    await callback.answer()


@dp.callback_query(F.data == "show_second_profile")
async def show_second_profile(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    await callback.message.answer(
        build_second_profile_text(data),
        reply_markup=one_button(
            COMPATIBILITY_PREVIEW_BUTTON_TEXT,
            "show_expression_compatibility",
        ),
    )

    await callback.answer()


@dp.callback_query(F.data == "show_expression_compatibility")
async def show_expression_compatibility(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()

    await callback.message.answer(
        build_expression_compatibility_text(data),
        reply_markup=one_button(
            NEXT_BUTTON_TEXT,
            "show_preview",
        ),
    )

    await callback.answer()


@dp.callback_query(F.data == "show_preview")
async def show_preview(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    text = COMPATIBILITY_PREVIEW_TEXT.format(
        name1=data["name1"],
        name2=data["name2"],
        percent=data["percent"],
    )

    await callback.message.answer(
        text,
        reply_markup=payment_button(),
    )

    await callback.answer()


@dp.callback_query(F.data == "payment_info")
async def payment_info(callback: CallbackQuery):
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Love Guide",
        description="Полный персональный анализ совместимости",
        payload="love_guide_full_analysis",
        currency="XTR",
        prices=[
            LabeledPrice(
                label="Полный анализ",
                amount=LOVE_GUIDE_PRICE,
            )
        ],
    )

    await callback.answer()

@dp.callback_query(F.data == "paypal_payment")
async def paypal_payment(callback: CallbackQuery):
    await callback.message.answer(
        "💳 Для оплаты через PayPal нажмите кнопку ниже:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Оплатить $6.99",
                        url=f"https://love-guide-pay.onrender.com/?user_id={callback.from_user.id}"
                    )
                ]
            ]
        )
    )
    await callback.answer()    

@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout: PreCheckoutQuery):
    await pre_checkout.answer(ok=True)

@dp.message(F.successful_payment)
async def successful_payment(message: Message, state: FSMContext):
    if message.successful_payment.invoice_payload != "love_guide_full_analysis":
        return

    await state.update_data(paid=True)

    await message.answer(
        PAYMENT_SUCCESS_TEXT,
        reply_markup=one_button(
            SOUL_COMPATIBILITY_BUTTON_TEXT,
            "show_soul_intro",
        ),
    )    

@dp.callback_query(F.data == "test_payment_done")
async def test_payment_done(callback: CallbackQuery, state: FSMContext):
    await state.update_data(paid=True)

    await callback.message.answer(
        PAYMENT_SUCCESS_TEXT,
        reply_markup=one_button(
            SOUL_COMPATIBILITY_BUTTON_TEXT,
            "show_soul_intro",
        ),
    )

    await callback.answer()


@dp.callback_query(F.data == "show_soul_intro")
async def show_soul_intro(callback: CallbackQuery):
    await callback.message.answer(
        SOUL_COMPATIBILITY_INTRO,
        reply_markup=one_button(
            NEXT_BUTTON_TEXT,
            "show_soul_compatibility",
        ),
    )

    await callback.answer()


@dp.callback_query(F.data == "show_soul_compatibility")
async def show_soul_compatibility(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()

    await callback.message.answer(
        build_soul_compatibility_text(data),
        reply_markup=one_button(
            DESTINY_COMPATIBILITY_BUTTON_TEXT,
            "show_destiny_intro",
        ),
    )

    await callback.answer()


@dp.callback_query(F.data == "show_destiny_intro")
async def show_destiny_intro(callback: CallbackQuery):
    await callback.message.answer(
        DESTINY_COMPATIBILITY_INTRO,
        reply_markup=one_button(
            NEXT_BUTTON_TEXT,
            "show_destiny_compatibility",
        ),
    )

    await callback.answer()


@dp.callback_query(F.data == "show_destiny_compatibility")
async def show_destiny_compatibility(
    callback: CallbackQuery,
    state: FSMContext,
):
    data = await state.get_data()

    await callback.message.answer(
        build_destiny_compatibility_text(data),
        reply_markup=one_button(
            IMPORTANT_BUTTON_TEXT,
            "important",
        ),
    )

    await callback.answer()


@dp.callback_query(F.data == "important")
async def important(callback: CallbackQuery):
    await callback.message.answer(
        IMPORTANT_RELATIONSHIPS_TEXT,
        reply_markup=one_button(
            NEXT_BUTTON_TEXT,
            "finish_analysis",
        ),
    )

    await callback.answer() 


@dp.callback_query(F.data == "finish_analysis")
async def finish_analysis(callback: CallbackQuery):
    bot_info = await bot.get_me()
    bot_link = f"https://t.me/{bot_info.username}?start=share"
    share_link = (
    "https://t.me/share/url?"
    f"url={quote(bot_link)}&"
    f"text={quote('💕 Попробуйте Love Guide')}"
)

    await callback.message.answer(FINAL_THANKS_TEXT, parse_mode="HTML")

    await callback.message.answer(
    f"{SHARE_TEXT}\n\n"
    f"🔗 Или скопируйте ссылку и отправьте её в любом мессенджере:\n\n"
    f"{bot_link}",
    reply_markup=final_buttons(share_link),
)

    await callback.message.answer(
    """💞 Если вы уже в отношениях, возвращайтесь к этому разбору в моменты непонимания или конфликтов.

    Иногда то, что сейчас кажется просто интересной информацией, в конкретной ситуации помогает лучше понять реакцию партнёра и увидеть причину разногласий.

    Этот разбор останется у вас — вы сможете возвращаться к нему и перечитывать столько раз, сколько захотите."""
    )

    await callback.answer()


@dp.callback_query(F.data == "gift_pdf")
async def send_gift(callback: CallbackQuery):
    await callback.message.answer_document(
        FSInputFile("gift.pdf"),
        caption="🎁 Ваш подарок"
    )
    await callback.answer()


@dp.callback_query(F.data == "other_pair")
async def other_pair(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(FIRST_NAME_TEXT)
    await state.set_state(LoveGuideStates.first_name)
    await callback.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
