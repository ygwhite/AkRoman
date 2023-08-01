from aiogram import types
from aiogram.types import (
    BotCommand,
)


class TextsManager:
    @staticmethod
    def first_message(lang):
        lang = lang.lower()
        res = None
        if lang == 'russian':
            res = '👋Добро пожаловать! \n\n👇Выберите язык👇'
        if lang == 'spanish':
            res = '👋Bienvenido! \n \ n👇Seleccione el idioma👇'
        if lang == 'chinese':
            res = '欢迎！ \n\n👇选择一种语言👇'
        if not res:
            res = '👋Welcome! \n\n👇Choose a language👇'
        return res

    @staticmethod
    def button_webapp_text(lang):
        lang = lang.lower()
        res = None
        if lang == 'russian':
            res = 'Торговый бот'
        if lang == 'spanish':
            res = 'Robot comercial'
        if lang == 'chinese':
            res = '交易机器人'
        if not res:
            res = 'Trading bot'
        return res

    @staticmethod
    def menu_text(lang):
        res = None
        if lang == 'russian':
            res = 'Помощь /support'
        if lang == 'spanish':
            res = 'Ayuda /support'
        if lang == 'chinese':
            res = '“帮助支持”'
        if not res:
            res = 'Help / support'
        return res

    @staticmethod
    def button_profile_text(lang):
        lang = lang.lower()
        res = None
        if lang == 'russian':
            res = 'Профиль'
        if lang == 'spanish':
            res = 'perfil'
        if lang == 'chinese':
            res = '轮廓'
        if not res:
            res = 'Profile'
        return res

    @staticmethod
    def bot_command(lang):
        lang = lang.lower()
        res = None
        if lang == 'russian':
            res = [BotCommand('start', 'Запустить бота'),
                   BotCommand("support", "Оатиться в поддержку")]
        if lang == 'spanish':
            res = [BotCommand('start', 'ejecutar un bot'),
                   BotCommand("support", "Soporte de contacto")]
        if lang == 'chinese':
            res = [BotCommand('start', '运行机器人'),
                   BotCommand("support", "联系支持")]
        if not res:
            res = [BotCommand('start', 'Start the bot'),
                   BotCommand("support", "Contact Support")]
        return res

    @staticmethod
    def profile(lang, timeframes, active_user_sub, is_binance_api):
        if is_binance_api:
            text_binance_api = TextsManager.binance_api_recieved(lang)
        else:
            text_binance_api = "❌ BINANCE API ❌"
        res = None
        if lang == 'russian':
            res = 'Доступные таймфреймы: {timeframes}\n\nВаша подписка {active_user_sub} \n\n {text_binance_api_connected} \n\nВыберите язык:'
        if lang == 'spanish':
            res = 'Plazos disponibles: {timeframes}\n\n {text_binance_api_connected} \n\nSeleccionar idioma:'
        if lang == 'chinese':
            res = '可用时间范围：{timeframes}\n\n {text_binance_api_connected} \n\n选择语言：'
        if not res:
            res = 'Available timeframes: {timeframes}\n\n Yours subscription: {active_user_sub} \n\n {text_binance_api_connected} \n\nChoose language: '
        return res.format(timeframes=timeframes, active_user_sub=active_user_sub,
                          text_binance_api_connected=text_binance_api)

    @staticmethod
    def pay_select(lang):
        res = None
        if lang == 'russian':
            res = '👇Выберите подписку👇'
        if lang == 'spanish':
            res = '👇Elige una suscripción👇'
        if lang == 'chinese':
            res = '👇选择订阅👇'
        if not res:
            res = '👇Choose a subscription👇'
        return res

    @staticmethod
    def binance_enter_api(lang):
        res = None
        if lang == 'russian':
            res = '👇Введите API ключ👇'
        if lang == 'spanish':
            res = '👇Introduzca la clave API👇'
        if lang == 'chinese':
            res = '👇输入API密钥👇'
        if not res:
            res = '👇Enter API key👇'
        return res

    @staticmethod
    def binance_api_key_recieved(lang):
        res = None
        if lang == 'russian':
            res = 'Введите секретный ключ'
        if lang == 'spanish':
            res = 'Introduzca la clave secreta'
        if lang == 'chinese':
            res = '输入密钥'
        if not res:
            res = 'Enter secret API key'
        return f"👇 {res}  👇 "

    @staticmethod
    def binance_api_recieved(lang):
        res = None
        if lang == 'russian':
            res = 'Binance API подключено'
        if lang == 'spanish':
            res = 'API de Binance conectada'
        if lang == 'chinese':
            res = '连接Binance API'
        if not res:
            res = 'Binance API connected'
        return f"✅ {res} ✅"

    @staticmethod
    def change_lang_reply(lang, new_lang_name):
        res = None
        if lang == 'russian':
            res = 'Сменили язык на {new_lang_name}'
        if lang == 'spanish':
            res = 'Idioma cambiado a {new_lang_name}'
        if lang == 'chinese':
            res = '将语言更改为 {new_lang_name}'
        if not res:
            res = 'Changed language to {new_lang_name}'
        return res.format(new_lang_name=new_lang_name)

    @staticmethod
    def stateless_input_text(lang):
        res = None
        if lang == 'russian':
            res = 'Если вам нужна поддержка, введите /support'
        if lang == 'spanish':
            res = 'Si necesita soporte escriba /soporte'
        if lang == 'chinese':
            res = '如果您需要支持类型 /support'
        if not res:
            res = 'If you need support type /support'
        return res

    @staticmethod
    def cancel_reply_text(lang):
        res = None
        if lang == 'russian':
            res = 'Отмена'
        if lang == 'spanish':
            res = 'Cancelar'
        if lang == 'chinese':
            res = '取消'
        if not res:
            res = 'Cancel'
        return res

    @staticmethod
    def cancel_monitoring_reply_text(lang):
        res = None
        if lang == 'russian':
            res = 'Мониторинг остановлен'
        if lang == 'spanish':
            res = 'Supervisión detenida'
        if lang == 'chinese':
            res = '监控停止'
        if not res:
            res = 'Monitoring stopped'
        return res

    @staticmethod
    def cancel_monitoring_button_text(lang):
        res = None
        if lang == 'russian':
            res = 'Остановить мониторинг'
        if lang == 'spanish':
            res = 'Dejar de monitorear'
        if lang == 'chinese':
            res = '停止监控'
        if not res:
            res = 'Stop monitoring'
        return res

    @staticmethod
    def support_reply_text(lang):
        res = None
        if lang == 'russian':
            res = 'Support'
        if lang == 'spanish':
            res = 'Support'
        if lang == 'chinese':
            res = 'Support'
        if not res:
            res = 'Support'
        return res

    @staticmethod
    def without_sub_txt(lang):
        res = None
        if lang == 'russian':
            res = 'Напиши боту /pay для продления подписки'
        if lang == 'spanish':
            res = 'Escribe un bot /pay para renovar tu suscripción'
        if lang == 'chinese':
            res = '写信给机器人/付费续订您的订阅'
        if not res:
            res = 'Write to the bot /pay to renew your subscription'
        return res
