
import os
import csv
import json


def csv_to_json(file_path_):
    steps = {}

    with open(file_path_, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=',')

        next(reader)  # Пропускаем заголовок

        last_step_id = None
        last_media = None
        last_name = None
        last_text = None
        last_auto_step = None
        last_buttons = []

        for row in reader:
            step_id = row[2]
            media = row[6]
            name = row[1]
            text = row[3]
            button_text = row[5]
            next_step = int(row[4]) if row[4].isdigit() else -1

            if not step_id:
                step_id = last_step_id

            # Если текущий шаг отличается от предыдущего и у нас есть данные о предыдущем шаге
            if step_id != last_step_id and last_step_id:
                # Добавляем предыдущий шаг с кнопками
                steps[last_step_id] = {
                    "media": [last_media] if last_media else [],
                    "name": last_name,
                    "text": last_text,
                    "buttons": last_buttons,
                    "auto_step": last_auto_step if last_auto_step is not None else -1
                }

                # Обнуляем данные для нового шага
                last_media = None
                last_name = None
                last_text = None
                last_auto_step = None
                last_buttons = []

            # Обновляем данные для текущего шага
            if media:
                last_media = media
            if name:
                last_name = name
            if text:
                last_text = text
            if button_text:
                button = {
                    "text": button_text,
                    "to_step": next_step
                }
                last_buttons.append(button)
            if next_step != -1 and not button_text:
                last_auto_step = next_step

            last_step_id = step_id

        # Добавляем последний шаг после завершения чтения файла
        if last_step_id:
            steps[last_step_id] = {
                "media": [last_media] if last_media else [],
                "name": last_name,
                "text": last_text,
                "buttons": last_buttons,
                "auto_step": last_auto_step if last_auto_step is not None else -1
            }

    # Объединение шагов, содержащих только кнопки
    combined_steps = {}
    prev_step = None

    for step_id, step_data in steps.items():
        if prev_step and not step_data["media"] and not step_data["name"] and not step_data["text"]:
            combined_steps[prev_step]["buttons"].extend(step_data["buttons"])
        else:
            combined_steps[step_id] = step_data
            prev_step = step_id

    output_path = '/var/www/html/novells/BattyAndGrant/story/story.json'

    try:
        os.remove(output_path)
    except FileNotFoundError:
        pass

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(combined_steps, json_file, ensure_ascii=False, indent=2)
