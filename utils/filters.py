import json

from utils.file_system import get_json, filters_path, write_info, del_group
from utils.parsing import get_users, get_group_id, get_groups, justify

filters = {
    '': ['📌', 'Отслеживаемые', 'Группа'],
    'ban': ['⛔️', 'Заблокированные', 'Пользователь'],
    'bw': ['🚫', 'Запрещенные', 'Слово'],
    'lw': ['⭐️', 'Избранные', 'Слово']
}


def replace_many(string: str, strings_to_replace: list) -> str:
    for substring in strings_to_replace:
        string = string.replace(substring, '')
    return string


def move_element(need_to_del: bool, data: dict, filters_list: str, element: str):
    if filters_list == 'ban':
        element = int(element)

    is_in_list = element in data[filters_list] if filters_list else element in data
    action = 'удалено из списка' if need_to_del else 'добавлено в список'

    if is_in_list == need_to_del and filters_list:
        data[filters_list].remove(element) if need_to_del else data[filters_list].append(element)
    elif not filters_list:
        del_group(element) if need_to_del else write_info(get_group_id(element))
        action = action.replace('но', 'на')
    else:
        action = 'уже в списке' if is_in_list else 'не в списке'

    if filters_list == 'ban':
        action = 'разблокирован' if need_to_del else 'заблокирован'
        if is_in_list != need_to_del:
            action = 'уже' + action
        return action

    return f'{action} {filters[filters_list][1].lower()[:-1]}х'


def find_plural(obj: str):
    return obj.replace('ель', 'ели').replace('во', 'ва').replace('па', 'пы')


def filters_actions(command: str) -> str:
    need_to_del = command.startswith(('/un', '/del'))
    words = command.replace('  ', ' ').split(' ')
    command, elements = words[0], words[1:]
    filters_list = replace_many(command, ['/', 'un', 'add', 'del', '@SearchHome03_Bot'])

    emoji, title, obj = filters[filters_list]
    data = get_json('filters') if filters_list else get_json()

    if filters_list == 'ban':
        action = 'уже разблокирован' if need_to_del else 'уже заблокирован'
    else:
        action = 'не в списке'

    for element in elements:
        action = move_element(need_to_del, data, filters_list, element)

    if len(elements) > 1:
        action = action.replace('но', 'ны')
        obj = find_plural(obj)
        if filters_list == 'ban':
            action += 'ы'

    formatted_elements = [f"«<code>{element}</code>»" for element in elements]
    answer = f'{emoji} {obj} {", ".join(formatted_elements)} {action}!'

    if data and filters_list:
        with open(filters_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    return f'{answer}\n\nПосмотреть список: /list{filters_list}'


def get_filters_list(message: str) -> str:
    filters_list = replace_many(message[1:], ['list', '@SearchHome03_Bot'])
    emoji, title, obj = filters[filters_list][:3]
    data = get_json('filters')[filters_list] if filters_list else get_groups()

    answer = [f'<b>{emoji} {title} {find_plural(obj.lower())}:</b>']

    if filters_list == "ban":
        users = get_users(data)

    for i in range(len(data)):
        formatted_el = justify(data[i] if filters_list else data[i]['id'])
        element = f"— <code>{formatted_el}</code>"
        if filters_list == "ban":
            element += f" | {users[i]['first_name']} {users[i]['last_name']}"
        elif not filters_list:
            element += f" | <a href='https://vk.com/{data[i]['screen_name']}'>{data[i]['name']}</a>"
        answer.append(element)

    if len(answer) == 1:
        return f'{answer[0]}\n— список пуст 😇'
    return '\n'.join(answer)
