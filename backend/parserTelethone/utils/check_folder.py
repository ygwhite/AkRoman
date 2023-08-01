from telethon.tl import functions
async def is_in_folder(client, input_id: int, folders_names: tuple):
    all_filters = await client(functions.messages.GetDialogFiltersRequest())
    # получаем все папки с каналами внутри
    res = {}
    for x in all_filters:
        folder = x.to_dict()
        res[folder.get('title', None)] = folder
    for folder_name in folders_names:
        if res.get(folder_name, None):
            # проверяем есть ли искомая папка в списке all_filters
            # Если она есть - мы проходимся в цикле по каналам в этой папке

            # Если канал в прикрепленных - то мы прикрепленные каналы добавляем в include_peers
            res[folder_name]['include_peers'].extend(res[folder_name]['pinned_peers'])
            for dialog in res[folder_name]['include_peers']:
                chat_id = dialog.get('chat_id')
                channel_id = dialog.get('channel_id')
                # Проверяем канал является нашим каналом
                if (type(chat_id) is int and abs(chat_id) == abs(input_id)) or (
                        type(channel_id) is int and abs(channel_id) == abs(input_id)):
                    return folder_name

