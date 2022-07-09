from datetime import date, datetime

from sqlalchemy import select
from vk_api.longpoll import VkLongPoll, VkEventType
from services import VkService
from sqlalchemy.orm import Session
from models import *

vk_service = VkService.VkService()
longpoll = VkLongPoll(vk_service.get_group_vk())


# engine = create_engine("sqlite:///db.sqlite3", echo=True, future=True)


def get_user_filter_from_info(user_info):
    user_filter = {
        'age_from': get_age_from_bdate(user_info['bdate']) - 5,
        'age_to': get_age_from_bdate(user_info['bdate']) + 5,
        'sex': 1 if user_info['sex'] == 2 else 2,
        'status': user_info['status'],
        'city': user_info['city']['id'],
        'is_closed': 0
    }
    return user_filter


def get_best_user_photos(user_id):
    photo_like_counts = vk_service.get_user_photo_likes(user_id)
    sorted_photos = dict(sorted(photo_like_counts.items(), key=lambda item: item[1]))
    best_photos = {}
    for photo_id in list(reversed(list(sorted_photos)))[:3]:
        best_photos[photo_id] = sorted_photos[photo_id]
    return best_photos


def save_users(user_list):
    users_to_save = []
    for user_item in user_list:
        city = user_item['city']['title'] if 'city' in user_item else ''
        user = session.scalars(select(User).where(User.vk_id == user_info['id'])).first()
        if not isinstance(user, User):
            user = User(age=get_age_from_bdate(user_item['bdate']), sex=user_item['sex'],
                        name=user_item['first_name'] + ' ' + user_item['last_name'], city=city, vk_id=user_item['id'])
        users_to_save.append(user)
    session.add_all(users_to_save)
    session.commit()


def save_user_photo(user_id, item):
    photo = session.scalars(select(Photo).where(Photo.vk_id == item)).first()
    if not isinstance(photo, Photo):
        photo = Photo(user_id=user_id, vk_id=item)
        session.add(photo)
        session.commit()


def save_search_history(user_id, pair_id):
    search_history = SearchHistory(user_id=user_id, pair_id=pair_id)
    session.add(search_history)
    session.commit()


def send_search_result_message(user_id, users):
    for user in users:
        try:
            search_history = session.scalars(select(SearchHistory).
                                             where(SearchHistory.user_id == user_id).
                                             where(SearchHistory.pair_id == user['id'])).first()
            if not isinstance(search_history, SearchHistory):
                message = ''
                attachment = ''
                best_user_photos = get_best_user_photos(user['id'])
                message += 'https://vk.com/id' + str(user['id']) + ' - ' + user['first_name'] + ' ' + user[
                    'last_name'] + '\n'
                for item in best_user_photos.keys():
                    if len(attachment) > 0:
                        attachment += ','
                    attachment += 'photo' + str(user['id']) + '_' + str(item)
                    save_user_photo(user['id'], item)
                save_search_history(user_id, user['id'])
                vk_service.write_msg(user_id, message, attachment)
        except:
            continue


def get_age_from_bdate(bdate):
    today = date.today()
    try:
        birthday = datetime.strptime(bdate, "%d-%m-%Y").date()
    except:
        return 30
    age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
    return age


def get_user_pairs_count(user_id):
    pairs_count = session.query(SearchHistory).where(SearchHistory.user_id == user_id).count()
    return pairs_count


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            if request == "привет":
                vk_service.write_msg(event.user_id, f"Хай, {event.user_id}")
            if request == "Ищи":
                user_info = vk_service.get_user_info(event.user_id)[0]
                with Session(engine) as session:
                    user = session.scalars(select(User).where(User.vk_id == user_info['id'])).first()
                    if not isinstance(user, User):
                        new_user = User(age=get_age_from_bdate(user_info['bdate']), sex=user_info['sex'],
                                        name=user_info['first_name'] + ' ' + user_info['last_name'],
                                        city=user_info['city']['title'], vk_id=user_info['id'])
                        session.add(new_user)
                        session.commit()
                user_filter = get_user_filter_from_info(user_info)
                user_filter['offset'] = get_user_pairs_count(event.user_id)
                users_info = vk_service.get_users_by_filter(user_filter)
                save_users(users_info['items'])
                send_search_result_message(event.user_id, users_info['items'])
            elif request == "пока":
                vk_service.write_msg(event.user_id, "Пока")
            else:
                vk_service.write_msg(event.user_id, "Не понял вашего ответа...")
