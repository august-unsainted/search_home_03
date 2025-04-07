import os
import json

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
parent_dir = os.path.dirname(current_dir)
path = os.path.join(parent_dir, 'last_posts.json')


def get_json() -> dict:
    with open(path, 'r') as file:
        return json.load(file)


def write_info(group: int | str, post_id: int = None) -> None:
    data = get_json()
    with open(path, 'w') as file:
        data[str(group)] = post_id
        json.dump(data, file, indent=4)
        return


def del_group(group: int | str) -> None:
    data = get_json()
    with open(path, 'w') as file:
        del data[str(group)]
        # data[str(group)] = post_id
        json.dump(data, file, indent=4)
        return
