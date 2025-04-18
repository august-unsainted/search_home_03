import vk_api

from config import VK_LOGIN, VK_PASS

vk_session = vk_api.VkApi(login=VK_LOGIN, password=VK_PASS)
vk_session.auth(token_only=True)
vk = vk_session.get_api()


def get_posts(group_id: str | int, count: int) -> dict:
    return vk.wall.get(domain="club" + str(group_id), offset=0, count=count)['items']


def get_group_id(link: str) -> int:
    if 'https' in link:
        domain = link.split('/')[-1].split('?')[0]
        group = vk.groups.getById(group_id=domain)
        return group[0]['id']
    return int(link)


def get_info(data: list | int, info_type: str = 'groups') -> list:
    if data is list:
        data = ', '.join(data)
    if info_type == 'groups':
        return vk.groups.getById(group_ids=data)
    else:
        return vk.users.get(user_ids=data)
