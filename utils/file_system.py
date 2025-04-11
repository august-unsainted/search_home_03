import os
import json

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
parent_dir = os.path.dirname(current_dir)
path = os.path.join(parent_dir, 'last_posts.json')
filters_path = os.path.join(parent_dir, 'filters.json')


def get_json(file_path: str = path) -> dict:
    if file_path == 'filters':
        file_path = filters_path
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def write_info(key: int | str, value: int = None, file_path: str = path) -> None:
    data = get_json(file_path)
    if file_path == 'filters':
        file_path = filters_path
    with open(file_path, 'w') as file:
        data[str(key)] = value
        json.dump(data, file, indent=4, ensure_ascii=False)
        return


def del_group(group: int | str) -> None:
    data = get_json()
    with open(path, 'w') as file:
        del data[str(group)]
        json.dump(data, file, indent=4, encoding='utf-8')
        return


def replace_many(string: str, strings_to_replace: list) -> str:
    for substring in strings_to_replace:
        string = string.replace(substring, '')
    return string


filters = {
    'ban': ['ban', '⛔️', 'Заблокированные пользователи', ['заблокирован', 'разблокирован']],
    'bw': ['blacklist', '🚫', 'Запрещенные', 'запрещенных'],
    'lw': ['whitelist', '⭐️', 'Избранные', 'избранных']
}


def filters_actions(command: str) -> str:
    need_to_del = command.startswith(('/un', '/del'))
    command, element = command.split(' ')
    command = replace_many(command, ['/', 'un', 'add', 'del'])

    filters_list, emoji, title, declination = filters[command]
    data = get_json('filters')
    if filters_list == 'ban':
        element = int(element)
        declination = declination[need_to_del]
    with open(filters_path, 'w', encoding='utf-8') as file:
        if need_to_del:
            data[filters_list].remove(element)
            action = 'было удалено из списка'
        else:
            data[filters_list].append(element)
            action = 'было добавлено в список'

        if filters_list == 'ban':
            action = 'был'

        answer = f'{emoji} {"Пользователь" if emoji == "⛔️" else "Слово"} «<code>{element}</code>» {action} {declination}!'
        json.dump(data, file, indent=4, ensure_ascii=False)
        return answer


def get_filters_list(message: str) -> str:
    filters_list, emoji, title = filters[message[1:-4]][:3]
    data = get_json('filters')[filters_list]
    answer = [f'<b>{emoji} {title} слова</b>']
    for i in range(len(data)):
        answer.append(f"{str(i + 1).rjust(2, '0')} | <code>{data[i]}</code>")
    return '\n'.join(answer)
