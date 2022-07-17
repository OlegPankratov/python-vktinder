from random import randrange

import vk_api

group_token = ''  # Токен группы
personal_token = ''  # Персональный токен


class VkService:
    def __init__(self):
        self.group_vk = vk_api.VkApi(token=group_token)
        self.personal_vk = vk_api.VkApi(token=personal_token)

    def get_group_vk(self):
        return self.group_vk

    def write_msg(self, user_id, message, attachment=''):
        self.group_vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7),
                                               'attachment': attachment})

    def get_user_info(self, user_id):
        return self.group_vk.method('users.get',
                                    {'user_ids': user_id, 'fields': 'sex,bdate,city,status', 'name_case': 'Nom'})

    def get_all_user_photos(self, user_id):
        all_user_photos = self.personal_vk.method('photos.getAll', {'owner_id': user_id})
        return all_user_photos

    def get_user_photo_likes(self, user_id):
        user_photos = self.get_all_user_photos(user_id)
        photo_like_counts = {}
        for user_photo in user_photos['items']:
            item_id = user_photo['id']
            likes = self.personal_vk.method('likes.getList', {'type': 'photo', 'owner_id': user_id, 'item_id': item_id})
            photo_like_counts[item_id] = likes['count']
        return photo_like_counts

    def get_users_by_filter(self, user_filter):
        request_body = user_filter
        request_body['fields'] = 'sex,bdate,city,status,nickname,photo_50'
        request_body['sort'] = 0
        return self.personal_vk.method("users.search", request_body)

