from helpers.Helpers import DateHelper
from models import SearchHistory
from services.DBService import DBService


class VkActions:
    def __init__(self, vk_service, user_id):
        self.vk_service = vk_service
        self.db_service = DBService()
        self.user_id = user_id

    def run_hi_action(self):
        return f"Хай, {self.user_id}"

    def run_bye_action(self):
        return "Пока"

    def run_unknown_action(self):
        return "Не понял вашего ответа..."

    def get_best_user_photos(self, user_id):
        photo_like_counts = self.vk_service.get_user_photo_likes(user_id)
        sorted_photos = dict(sorted(photo_like_counts.items(), key=lambda item: item[1]))
        best_photos = {}
        for photo_id in list(reversed(list(sorted_photos)))[:3]:
            best_photos[photo_id] = sorted_photos[photo_id]
        return best_photos

    def get_search_result_message(self, user_id, users):
        result_message = []
        for user in users:
            try:
                search_history = self.db_service.get_search_history(user_id, user['id'])
                if not isinstance(search_history, SearchHistory):
                    message = ''
                    attachment = ''
                    best_user_photos = self.get_best_user_photos(user['id'])
                    message += 'https://vk.com/id' + str(user['id']) + ' - ' + user['first_name'] + ' ' + user[
                        'last_name'] + '\n'
                    for item in best_user_photos.keys():
                        if len(attachment) > 0:
                            attachment += ','
                        attachment += 'photo' + str(user['id']) + '_' + str(item)
                        self.db_service.save_user_photo(user['id'], item)
                    self.db_service.save_search_history(user_id, user['id'])
                    result_message.append({'text': message, 'attachment': attachment})
            finally:
                continue
        return result_message

    @staticmethod
    def get_user_filter_from_info(user_info):
        user_filter = {
            'age_from': DateHelper.get_age_from_bdate(user_info['bdate']) - 5,
            'age_to': DateHelper.get_age_from_bdate(user_info['bdate']) + 5,
            'sex': 1 if user_info['sex'] == 2 else 2,
            'status': user_info['status'],
            'city': user_info['city']['id'],
            'is_closed': 0
        }
        return user_filter

    def run_find_action(self):
        user_info = self.vk_service.get_user_info(self.user_id)[0]
        self.db_service.save_user(user_info)
        user_filter = VkActions.get_user_filter_from_info(user_info)
        user_filter['offset'] = self.db_service.get_user_pairs_count(self.user_id)
        users_info = self.vk_service.get_users_by_filter(user_filter)
        self.db_service.save_users(users_info['items'])
        return self.get_search_result_message(self.user_id, users_info['items'])
