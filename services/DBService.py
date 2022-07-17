from sqlalchemy.orm import Session
from models import *
from sqlalchemy import select
from helpers.Helpers import DateHelper
from sqlalchemy import create_engine

engine = create_engine("sqlite:///db.sqlite3", echo=True, future=True)


class DBService:
    def __init__(self):
        self.session = Session(engine)

    def get_search_history(self, user_id, pair_id):
        return self.session.scalars(select(SearchHistory).
                                    where(SearchHistory.user_id == user_id).
                                    where(SearchHistory.pair_id == pair_id)).first()

    def save_user(self, user_info):
        user = self.session.scalars(select(User).where(User.vk_id == user_info['id'])).first()
        if not isinstance(user, User):
            user = User(age=DateHelper.get_age_from_bdate(user_info['bdate']), sex=user_info['sex'],
                        name=user_info['first_name'] + ' ' + user_info['last_name'],
                        city=user_info['city']['title'], vk_id=user_info['id'])
            self.session.add(user)
            self.session.commit()

    def save_users(self, user_list):
        users_to_save = []
        for user_item in user_list:
            city = user_item['city']['title'] if 'city' in user_item else ''
            user = self.session.scalars(select(User).where(User.vk_id == user_item['id'])).first()
            if not isinstance(user, User):
                user = User(age=DateHelper.get_age_from_bdate(user_item['bdate']), sex=user_item['sex'],
                            name=user_item['first_name'] + ' ' + user_item['last_name'], city=city,
                            vk_id=user_item['id'])
            users_to_save.append(user)
        self.session.add_all(users_to_save)
        self.session.commit()

    def save_user_photo(self, user_id, item):
        photo = self.session.scalars(select(Photo).where(Photo.vk_id == item)).first()
        if not isinstance(photo, Photo):
            photo = Photo(user_id=user_id, vk_id=item)
            self.session.add(photo)
            self.session.commit()

    def save_search_history(self, user_id, pair_id):
        search_history = SearchHistory(user_id=user_id, pair_id=pair_id)
        self.session.add(search_history)
        self.session.commit()

    def get_user_pairs_count(self, user_id):
        pairs_count = self.session.query(SearchHistory).where(SearchHistory.user_id == user_id).count()
        return pairs_count
