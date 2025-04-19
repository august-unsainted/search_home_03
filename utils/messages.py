CAPTION = (
    '📌 <b>{group_name}</b>\n'
    '📔 <code>{group_id}</code>\n'
    '🕓 {date}\n\n'
    '{description}\n\n'
    '{user_info}'
    '<a href="https://vk.com/club{group_id}?w=wall-{group_id}_{post_id}">Перейти к объявлению</a>\n\n'
    '<blockquote expandable>{text}</blockquote>'
)

REASON = {
    'bw':              '🚫 Запрещенное слово «{}».',
    'ban':             '⛔️ Пользователь в списке заблокированных.',
    'repost':          '📣 Репост.',
    'not_rent':        '🗑 Не является объявлением о сдаче квартиры/комнаты.',
    'overprice':       '💰 Превышает бюджет: {price} > {max_price}.',
    'undefined_price': '💰 Цена не указана.'
}

FILTER = {
    'groups': ['📌', 'Отслеживаемые', 'Группа'],
    'ban':    ['⛔️', 'Заблокированные', 'Пользователь'],
    'bw':     ['🚫', 'Запрещенные', 'Слово'],
}

ACTIONS = {
    '+': ['добавлен', 'в список'],
    '-': ['удален', 'из списка'],
    '=': ['уже', 'в списке']
}

COMMANDS = {
    'spam':  ['🧑‍💻', '‍🧑‍💻 У всех групп были сброшены позиции: {}.'],
    'delay': ['⏱️', '⏱️ Задержка парсинга была изменена {}!', 'сек.'],
    'price': ['💰', '💰 Бюджет был изменен {}!', 'руб.']
}

LIST = {
    "element": "— <code>{}</code>",
    "ban":     " | {0[i]['first_name']} {0[i]['last_name']}",
    "empty":   "{0[0]}\n— список пуст 😇",
    'show':    "{answer}\n\nПосмотреть список: /{filters_list}"
}

ERROR = "\t\tОшибка в функции: {}.\n"
