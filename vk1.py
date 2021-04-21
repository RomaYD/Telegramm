import vk_api
import datetime
import config_vk

def main(count_posts):
#     Логинимся для просмотра стены
    login, password = config_vk.login, config_vk.password
    vk_session = vk_api.VkApi(login, password)
#     Попытка подключения
    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    vk = vk_session.get_api()
    # Используем метод wall.get чтобы брать информацию постов
    response = vk.wall.get(count=count_posts, owner_id=-199427155)
    if response['items']:
        return response['items']
        # for i in response['items']:
        #     print(i)
        #     print(datetime.datetime.fromtimestamp(i['date']))



if __name__ == '__main__':
    main()
