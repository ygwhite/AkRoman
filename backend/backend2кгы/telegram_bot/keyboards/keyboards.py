from aiogram import types
from telegram_bot.langs_support import TextsManager


class KeyboardManager:
    @staticmethod
    def pay_button(sub_lst):
        kb = types.InlineKeyboardMarkup(row_width=1)
        for sub in sub_lst:
            kb.add(types.InlineKeyboardButton(f'🤑{sub["name"]}',
                                              callback_data=f'payment_{sub["name"]}_{sub["day"]}_{sub["price"]}'))
        return kb

    @staticmethod
    def lang_select_buttons():
        kb = types.InlineKeyboardMarkup(row_width=1)
        btn_ru = types.InlineKeyboardButton("Русский", callback_data='lang_ru')
        btn_en = types.InlineKeyboardButton("English", callback_data='lang_en')
        btn_spa = types.InlineKeyboardButton("Spanish", callback_data='lang_spa')
        btn_chi = types.InlineKeyboardButton("Chinese", callback_data='lang_chi')

        kb.add(
            btn_ru, btn_en, btn_spa, btn_chi
        )
        return kb
    @staticmethod
    def cancel_button_lang(lang):
        kb = types.InlineKeyboardMarkup(row_width=1)
        text = TextsManager.cancel_reply_text(lang)
        btn = types.InlineKeyboardButton(text, callback_data='btn_cancel')

        kb.add(
            btn
        )
        return kb

    @staticmethod
    def in_profile_buttons():
        kb = types.InlineKeyboardMarkup(row_width=1)
        btn_ru = types.InlineKeyboardButton("Русский", callback_data='lang_ru')
        btn_en = types.InlineKeyboardButton("English", callback_data='lang_en')
        btn_spa = types.InlineKeyboardButton("Spanish", callback_data='lang_spa')
        btn_chi = types.InlineKeyboardButton("Chinese", callback_data='lang_chi')
        binance = types.InlineKeyboardButton("🚀Binance 📈", callback_data='connect_binance')

        kb.add(
            btn_ru, btn_en, btn_spa, btn_chi, binance
        )
        return kb

    @staticmethod
    def menu_buttons(link, lang):
        rkm_mainmenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn_trading_bot = types.KeyboardButton(
            TextsManager.button_webapp_text(lang),
            web_app=types.WebAppInfo(url=link)
        )
        btn_user_profile = types.KeyboardButton(TextsManager.button_profile_text(lang))

        rkm_mainmenu.add(
            btn_trading_bot,
            btn_user_profile,
        )
        return rkm_mainmenu

    @staticmethod
    def pay_link_button(url):
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('✅PAY', url=url))
        return kb
