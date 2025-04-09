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
        json.dump(data, file, indent=4)
        return


def ban_user(user_id: int | str) -> None:
    data = get_json('filters')
    with open(filters_path, 'w') as file:
        data['ban'].append(int(user_id))
        json.dump(data, file, indent=4, ensure_ascii=False)
        return
