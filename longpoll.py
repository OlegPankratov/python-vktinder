from vk_api.longpoll import VkLongPoll
from services.VkService import VkService
from services.VkEvent import VkEvent

vk_service = VkService()
longpoll = VkLongPoll(vk_service.get_group_vk())

for event in longpoll.listen():
    vk_event = VkEvent(event, vk_service)
    vk_event.run_event()
