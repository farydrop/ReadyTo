from flask import Flask, request, jsonify
import pysrt
import deepl
import os
from collections import defaultdict

app = Flask(__name__)

# Получение API-ключа из переменной окружения
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
translator = deepl.Translator(DEEPL_API_KEY)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    srt_content = file.read().decode('utf-8')
    subtitles = pysrt.from_string(srt_content)
    translations = []

    id_counter = 0
    translation_cache = {}
    word_count = defaultdict(int)

    # Подсчет количества повторений слов
    for subtitle in subtitles:
        words = subtitle.text.split()
        for word in words:
            word_count[word] += 1

    # Перевод слов и создание структуры данных
    for subtitle in subtitles:
        words = subtitle.text.split()
        for word in words:
            if word not in translation_cache:
                translated_word = translator.translate_text(word, source_lang='ES', target_lang='RU').text
                translation_cache[word] = translated_word

                translations.append({
                    "id": id_counter,
                    "original": word,
                    "translate": translated_word,
                    "context": subtitle.text,
                    "count": word_count[word],  # Количество повторений слова
                })
                id_counter += 1

    translations.sort(key=lambda x: x['count'], reverse=True)
    return jsonify(translations)

if __name__ == '__main__':
    app.run(debug=True)
