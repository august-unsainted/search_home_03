import json

from utils.file_system import get_json, filters_path, write_info, del_group
from utils.parsing import get_users, get_group_id, get_groups

filters = {
    '': ['📌', 'Отслеживаемые сообщества', 'Группа', 'отслеживаемых'],
    'ban': ['⛔️', 'Заблокированные пользователи', 'Пользователь', ['заблокирован', 'разблокирован']],
    'bw': ['🚫', 'Запрещенные слова', 'Слово', 'запрещенных'],
    'lw': ['⭐️', 'Избранные слова', 'Слово', 'избранных']
}


def replace_many(string: str, strings_to_replace: list) -> str:
    for substring in strings_to_replace:
        string = string.replace(substring, '')
    return string


def move_element(need_to_del: bool, data: dict, filters_list: str, element: str):
    if filters_list == 'ban':
        element = int(element)

    is_in_list = element in data[filters_list] if filters_list else element in data

    if is_in_list and need_to_del:
        data[filters_list].remove(element) if filters_list else del_group(element)
        action = 'было удалено из списка'
    elif not is_in_list and not need_to_del:
        data[filters_list].append(element) if filters_list else write_info(get_group_id(element))
        action = 'было добавлено в список'
    elif is_in_list:
        action = 'уже в списке'
    else:
        action = 'не в списке'

    if filters_list == 'ban':
        action = 'был'
        # del data[filters_list]

    return action


def filters_actions(command: str) -> str:
    need_to_del = command.startswith(('/un', '/del'))
    words = command.replace('  ', ' ').split(' ')
    command, elements = words[0], words[1:]
    filters_list = replace_many(command, ['/', 'un', 'add', 'del', '@SearchHome03_Bot'])

    emoji, title, obj, declination = filters[filters_list]

    if filters_list:
        data = get_json('filters')
    else:
        data = get_json()

    action = 'не в списке'
    for element in elements:
        action = move_element(need_to_del, data, filters_list, element)

    if filters_list == 'ban':
        declination = declination[need_to_del]

    if len(elements) > 1:
        action = action.replace('было', 'был').replace('был', 'были').replace('но', 'ны')
        if filters_list == 'ban':
            declination += 'ы'
        obj = obj.replace('ватель', 'ватели').replace('во', 'ва').replace('ппа', 'ппы')

    elements_formatted = [f"«<code>{element}</code>»" for element in elements]
    answer = f'{emoji} {obj} {", ".join(elements_formatted)} {action} {declination}!'

    if data and filters_list:
        with open(filters_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
    return f'{answer}\n\nПосмотреть список: /list{filters_list}'


def get_filters_list(message: str) -> str:
    filters_list = replace_many(message[1:], ['list', '@SearchHome03_Bot'])
    emoji, title, obj = filters[filters_list][:3]
    data = get_json('filters')[filters_list] if filters_list else get_groups()
    ban = filters_list == "ban"
    answer = [f'<b>{emoji} {title} {obj.lower().replace('тель', 'тели').replace('слово', 'слова')}:</b>']
    if ban:
        users = get_users(data)
    for i in range(len(data)):
        not_formatted_str = data[i] if filters_list else data[i]['id']
        formatted_str = str(not_formatted_str).ljust(9, ' ')
        element = f"— <code>{formatted_str}</code>"
        if ban:
            element += f" | {users[i]['first_name']} {users[i]['last_name']}"
        elif not filters_list:
            element += f" | <a href='https://vk.com/{data[i]['screen_name']}'>{data[i]['name']}</a>"
        answer.append(element)
    if len(answer) == 1:
        return f'{answer[0]}\n— список пуст 😇'
    return '\n'.join(answer)
