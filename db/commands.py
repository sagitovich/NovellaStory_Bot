import logging
from db.scenes import Scenes

logger = logging.getLogger(__name__)


async def user_scenes(user_id: int):
    try:
        user = await Scenes.query.where(Scenes.user_id == user_id).gino.first()
        if user is None:
            data = Scenes(user_id=user_id, scenes=[1], media=['-'])
            await data.create()
            logger.info(f'Пользователь id:{user_id} добавлен.')
            return [1]
        else:
            return user.scenes
    except Exception as e:
        logger.error(f'Ошибка /user_scenes. User_id:{user_id} | {e}')


async def add_scene(user_id: int, scene_: int):
    try:
        user = await Scenes.query.where(Scenes.user_id == user_id).gino.first()
        if user:
            if len(user.scenes) == 3:
                user.scenes.pop(0)
            user.scenes.append(scene_)
            await user.update(scenes=user.scenes).apply()
        else:
            logger.error(f'Пользователь {user_id} не найден.')
    except Exception as e:
        logger.error(f'Ошибка /add_scene: {e}')


async def pop_scene(user_id: int):
    try:
        user = await Scenes.query.where(Scenes.user_id == user_id).gino.first()
        user.scenes.pop()
        await user.update(scenes=user.scenes).apply()
    except Exception as e:
        logger.error(f'Ошибка /pop_scene: {e}')


async def user_media(user_id: int):
    try:
        user = await Scenes.query.where(Scenes.user_id == user_id).gino.first()
        return user.media
    except Exception as e:
        logger.error(f'Ошибка /user_scenes. User_id:{user_id} | {e}')


async def add_media(user_id: int, file: str):
    try:
        user = await Scenes.query.where(Scenes.user_id == user_id).gino.first()
        if user:
            if len(user.media) == 3:
                user.media.pop(0)
            user.media.append(file)
            await user.update(media=user.media).apply()
        else:
            logger.error(f'Пользователь {user_id} не найден.')
    except Exception as e:
        logger.error(f'Ошибка /add_media: {e}')
