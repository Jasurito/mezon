# Озвучка реплик (TTS)

Реплики персонажей озвучиваются **заранее**: MP3-файлы собираются на машине разработчика и лежат в S3-хранилище (RustFS на vm1). Сервер модели не запускает, при старте игры клиент сразу получает ссылку на готовый звук.

```
scenarios/<дело>/texts.*.json ──> python -m app.tts build (Silero, ваша машина) ──> backend/.tts-out/
                                                                                       │ make tts-upload
бэкенд при старте читает manifest.json ◄── бакет mezon-audio (RustFS, vm1) ──> nginx /audio/*.mp3 ──> браузер
        └─> audio_url в SayEvent / NpcAnswer
```

## Что озвучивается

| Источник | Говорит | Озвучка |
|---|---|---|
| `say` в `scenario.json` (этапы, действия, последствия решений) | персонаж или `narrator` | да |
| заготовленные ответы NPC (`npc_questions[].answer_key`) | персонаж | да |
| ответы NPC, написанные AI; ответы наставника; «переформулируйте вопрос» | — | нет, только текст |

## Голоса

| Язык | Мужской | Женский | Модель Silero |
|---|---|---|---|
| ru | `eugene` | `xenia` | `v5_6_ru` |
| uz | `uzb_0` (читает только кириллицу) | `dilnavoz` (только латиницу) | `v5_turkic` / `v4_uz` |

Узбекская озвучка одна на `uz-Latn` и `uz-Cyrl`: источник — `texts.uz-Latn.json`. Для `uzb_0` текст переводится в кириллицу (`app/i18n/translit.py`, та же функция, что для показа), для `dilnavoz` апострофы и буквы алфавита 2026 года (ö ğ ş ç) приводятся к обычной латинице. Цифры заменяются словами: «15-moddasiga» → «oʻn beshinchi moddasiga», «с 8 августа» → «с восьмого августа», «2 500 000 сумов» → «два миллиона пятьсот тысяч сумов».

### Кто каким голосом говорит

Пол персонажа определяется так (`app/tts/voices.py`), по порядку:

1. `"voice": "male" | "female"` у персонажа в `scenario.json` — всегда главнее;
2. персонаж игрока (`intro.player_role`, «Вы») — мужской;
3. имя: список имён в `app/tts/names.py` (Малика, Шерзод, Нилуфар…) или фамилия (-ова/-ов, -eva/-ev);
4. роль на русском: первое слово («Истица», «Продавщица») или родство в скобках («(сын)»);
5. персонаж только с должностью («Судья», «Эксперт») — мужской.

Рассказчик (`narrator`) — женский, меняется полем `"narrator_voice"` в `scenario.json`. Если имя похоже на имя человека («Зумрад Х.»), но его нет в списке, сборка **останавливается**: добавьте имя в `names.py` или задайте `voice`.

Проверить без синтеза: `make tts-voices`.

## Как собрать и залить

Один раз: `cd backend && pip install -e ".[tts]"` (torch, lameenc, boto3; в образ бэкенда не попадают). Веса (35–150 МБ на модель) скачиваются при первой сборке в `backend/.tts-models/` и проверяются по sha256.

```bash
make tts-voices                      # кто каким голосом говорит
make tts-build                       # синтез изменённых реплик в backend/.tts-out (4 дела: ~1,5 мин, 20 МБ)
make tts-build ARGS="--scenario rent_deposit_003 --lang uz"
make tts-upload                      # нужен root по SSH на vm1; в конце перезапускает mezon-backend
make tts-upload ARGS="--prune"       # ещё и удалить из бакета реплики, которых больше нет
```

Сборка пересинтезирует только реплики, у которых изменился хэш (голос + текст + версия обработки текста). В конце печатается список реплик с цифрами — их стоит прослушать: падежи после чисел («около 4 лет» → «около четыре лет») генератор не согласует. Такую реплику проще переписать словами в `texts.*.json`.

Изменили обработку текста в `app/tts/text.py` (числа, транслитерация)? Увеличьте `TEXT_PIPELINE_VERSION` в `app/tts/voices.py`: у всех реплик сменится хэш, они пересоберутся и получат новые адреса (браузеры кэшируют MP3 на год).

## Хранилище

Бакет `mezon-audio`, раскладка:

```
scenarios/<scenario_id>/<ru|uz>/manifest.json
scenarios/<scenario_id>/<ru|uz>/<speaker>/<text_key>.mp3
common/...                                        (на будущее: общие фразы)
```

`manifest.json`: `lines["<speaker>/<text_key>"] = {speaker, text_key, voice, path, hash, duration_ms, bytes}`.

- vm1: RustFS (S3-совместимый; официальные образы MinIO больше не публикуются), `docker compose` в `/opt/mezon/storage` (`deploy/vm1/storage`), контейнер `mezon-storage` в сети `mezon`. Порты только на 127.0.0.1: API 9000, консоль 9001 (`ssh -L 9001:127.0.0.1:9001 root@vm1.modeus.cc`, ключи в `/etc/mezon/storage.env`).
- Публично читаются только `scenarios/*` и `common/*` (`mezon-audio.policy.json`), через nginx: `https://mezon.modeus.cc/audio/...mp3`, только GET.
- Локально: сервис `storage` в `docker-compose.yml` (консоль http://localhost:9001).

## API

| Где | Поле |
|---|---|
| `GameState.events[]` с `type: "say"` | `audio_url`, `audio_duration_ms` (null — только текст) |
| `POST /api/sessions/{id}/npc/{character_id}/ask` | `audio_url`, `audio_duration_ms` — только для заготовленного ответа (`ai_generated: false`) |
| `GET /api/scenarios/{scenario_id}/audio?locale=ru` | `[{speaker, text_key, url, duration_ms}]` — для предзагрузки при открытии дела |
| `GET /api/health` | `audio_lines` — сколько реплик со звуком загружено |

`audio_url` выдаётся, только если запись совпадает с текущим текстом: отредактировали текст и не пересобрали — звука у реплики нет (а не старая запись). Хранилище недоступно или `AUDIO_PUBLIC_BASE_URL` пуст — игра идёт без звука.

Настройки бэкенда (`/etc/mezon/backend.env`): `AUDIO_PUBLIC_BASE_URL=https://mezon.modeus.cc/audio`, `AUDIO_MANIFEST_BASE_URL=http://mezon-storage:9000/mezon-audio`. Новые манифесты бэкенд читает при старте.

## Лицензии

Модели Silero, насколько известно, распространяются под некоммерческой лицензией (проверьте условия на github.com/snakers4/silero-models перед коммерческим использованием).
