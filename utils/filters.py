import os
import json
import locale

from aiogram.filters import CommandObject

from utils.file_system import get_json, write_info, del_group, json_dir
from utils.parsing import get_info, get_group_id, get_posts
from utils.string_funcs import find_plural, justify
from utils.logger import logger
from utils.messages import *


def move_element(need_to_del: bool, data: dict, filters_list: str, element: str):
    try:
        if filters_list == 'ban':
            element = int(element)

        is_in_list = element in data[filters_list] if filters_list != 'groups' else str(element) in data
        actions = ACTIONS['-'] if need_to_del else ACTIONS['+']

        if is_in_list and not need_to_del:
            actions = ACTIONS['=']
        elif filters_list == 'groups':
            del_group(element) if need_to_del else write_info(get_group_id(element))
        else:
            data[filters_list].remove(element) if need_to_del else data[filters_list].append(element)

        list_name = FILTER[filters_list][1]
        return actions[0], actions[1], list_name.lower()[:-1] + 'х'
    except Exception as err:
        logger.error(f'Ошибка в фильтрах: {err}')
        logger.info('')
        return


def filters_actions(command: CommandObject) -> str:
    need_to_del = command.command.endswith('-')
    filters_list = command.command.replace('-', '')
    elements = command.args.split()

    emoji, title, obj = FILTER[filters_list]
    data = get_json() if filters_list == 'groups' else get_json('filters')

    verb, in_list, list_name = '', '', ''
    flag = False
    for i in range(len(elements)):
        if flag:
            i -= 1
        answer = move_element(need_to_del, data, filters_list, elements[i])
        if answer:
            verb, in_list, list_name = answer
        else:
            del elements[i]
            flag = True

    verb += {'bw': 'о', 'groups': 'а'}.get(filters_list, '') if verb != 'уже' else ''

    if len(elements) > 1:
        if verb != 'уже':
            if verb[-1] != 'н':
                verb = verb[:-1]
            verb += 'ы'
        obj = find_plural(obj)

    formatted_elements = [f"«<code>{element}</code>»" for element in elements]
    answer = f'{emoji} {obj} {", ".join(formatted_elements)} {verb} {in_list} {list_name}!'

    if data and filters_list != 'groups':
        file_path = os.path.join(json_dir, 'filters.json')
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    return LIST['show'].format(answer=answer, filters_list=filters_list)


def get_filters_list(filters_list: str) -> str:
    emoji, title, obj = FILTER[filters_list][:3]
    data = get_info(list(get_json().keys())) if filters_list == 'groups' else get_json('filters')[filters_list]
    answer = [f'<b>{emoji} {title} {find_plural(obj.lower())}:</b>']

    if filters_list == "ban":
        users = get_info(data, 'users')
        user_ids = [user['id'] for user in users]
        if len(users) < len(data):
            does_not_exist = {'first_name': 'Пользователя', 'last_name': 'не существует'}
            [users.insert(i, does_not_exist) for i in range(len(data)) if data[i] not in user_ids]

    for i in range(len(data)):
        formatted_el = justify(data[i] if filters_list != 'groups' else data[i]['id'])
        element = f'<code>{formatted_el}</code>'
        if filters_list == "ban":
            element += f" | {users[i]['first_name']} {users[i]['last_name']}"
        elif filters_list == 'groups':
            element += f" | <a href='https://vk.com/{data[i]['screen_name']}'>{data[i]['name']}</a>"
        answer.append(element)
    if len(answer) == 1:
        return FILTER['empty'].format(answer)
    return '\n'.join(answer)


def test_groups(count: str) -> None:
    count = int(count)
    data = get_json()
    for group in data:
        # if group == '230000411':
        #     continue

        posts = get_posts(group, count + 2)
        print('Посты:', [post['id'] for post in posts])
        posts = posts[1:] if posts[0].get('is_pinned', False) else posts[:-1]
        print('Посты после удаления закрепа:', [post['id'] for post in posts])
        last_post = posts[-1]['id']
        data_post = data[group] - count
        if data_post < last_post:
            last_post = data_post
        write_info(group, last_post)


def tools_actions(command: CommandObject):
    command, value = command.command, command.args
    emoji, onchange, measure = COMMANDS[command]
    if value and value.isdigit():
        if command == 'spam':
            test_groups(value)
        else:
            old_value = get_json('filters')[command]
            write_info(command, int(value), 'filters')
            value = f'с {old_value} на {value} {measure}'
        answer = onchange.format(value)
    elif command != 'spam' and not value:
        obj = onchange[:onchange.find(' ', 4)]
        old_value = get_json('filters')[command]
        answer = f'{obj}: {old_value} {measure}'
    else:
        answer = f'{emoji} Ошибка: не поддерживаемое значение!'
    return answer
