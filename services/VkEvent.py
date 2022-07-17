from vk_api.longpoll import VkEventType
from services.VkActions import VkActions


class VkEvent:
    def __init__(self, event, vk_service):
        self.event = event
        self.vk_service = vk_service

    def write_msg(self, message):
        if type(message) is dict:
            self.vk_service.write_msg(self.event.user_id, message['text'], message['attachment'])
        elif type(message) is list:
            for item in message:
                self.write_msg(item)
        else:
            self.vk_service.write_msg(self.event.user_id, message)

    def run_message_new_event_listener(self):
        if self.event.to_me:
            request = self.event.text
            if request == "Привет":
                message = self.vk_actions.run_hi_action()
            elif request == "Ищи":
                message = self.vk_actions.run_find_action()
            elif request == "Пока":
                message = self.vk_actions.run_bye_action()
            else:
                message = self.vk_actions.run_unknown_action()
            self.write_msg(message)

    def run_event(self):
        if self.event.type == VkEventType.MESSAGE_NEW:
            self.vk_actions = VkActions(self.vk_service, self.event.user_id)
            self.run_message_new_event_listener()
