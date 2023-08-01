from aiogram import types


class KeyboardManager:
    @staticmethod
    def signal_correct(id):
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(types.InlineKeyboardButton('✅️Correct', callback_data=f'signal_{id}_correct'))
        kb.insert(types.InlineKeyboardButton('❌Uncorrect', callback_data=f'signal_{id}_uncorrect'))
        return kb
