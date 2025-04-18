import os
import json

current_file = os.path.abspath(__file__)
utils_dir = os.path.dirname(current_file)
project_dir = os.path.dirname(utils_dir)
json_dir = os.path.join(project_dir, 'json')


def get_json(file_path: str = 'last_posts') -> dict:
    file_path = os.path.join(json_dir, file_path + '.json')
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def write_info(key: int | str, value: int = None, file_path: str = 'last_posts') -> None:
    data = get_json(file_path)
    data[str(key)] = value
    file_path = os.path.join(json_dir, file_path + '.json')
    if data:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)


def del_group(group: int | str) -> bool:
    data = get_json()
    if str(group) not in data:
        return False

    del data[str(group)]
    path = os.path.join(json_dir, 'last_posts.json')
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        return True


def test_groups(count: str) -> None:
    count = int(count)
    data = get_json()
    for group in data:
        if group != '230000411':
            write_info(group, data[group] - count)
