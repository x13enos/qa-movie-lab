# Movie QA Lab — Iteration 1

Учебный каталог для black-box QA через HTTP. FastAPI отдаёт API и минимальный HTML/CSS/JavaScript frontend с одного origin. Реализован **только MVP**: список фильмов и пагинация. QA самостоятельно пишет `pytest` + `requests`; готовых тестов и решений в репозитории нет.

## Установка и запуск

Требуется **Python 3.12+**. Выполняйте команды из корня репозитория. Установка зависимостей требует доступа к PyPI; после установки fixture-режим работает без внешней сети, API-ключа и внешних ресурсов UI.

macOS / Linux:

```bash
cd /path/to/qa-movie-lab
python3 --version  # должен быть 3.12 или новее; при необходимости используйте python3.12
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- UI: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json
- Остановка: **Ctrl+C**, затем `deactivate`, если нужно выйти из venv.
- Для разработки можно добавить `--reload`. Для HTTP-проверок используйте запуск без reload.
- `/docs` использует стандартные CDN-ресурсы Swagger UI: HTML и OpenAPI доступны локально, но интерактивный интерфейс требует сети либо кешированных ресурсов. Сам каталог в fixture полностью локален.

## Конфигурация

| Переменная | По умолчанию | Значение |
| --- | --- | --- |
| `DATA_SOURCE` | `fixture` | `fixture` или `tmdb`; другое значение — ошибка запуска |
| `TMDB_READ_TOKEN` | пусто | TMDB API Read Access Token, нужен только для `tmdb` |

Переменные читаются при запуске. `.env` **не подхватывается автоматически**. Для него:

```bash
cp .env.example .env
# Измените .env при необходимости; не публикуйте его.
python -m uvicorn app.main:app --env-file .env --host 127.0.0.1 --port 8000
```

Внешние environment variables имеют приоритет над `.env`. Не коммитьте токен и не вставляйте его в URL или frontend.

### Переключение на TMDB

1. Зарегистрируйтесь на [TMDB](https://www.themoviedb.org/).
2. В [Settings → API](https://www.themoviedb.org/settings/api) запросите доступ и скопируйте **API Read Access Token** (Bearer), не `api_key`.
3. Остановите сервер. В `.env` установите `DATA_SOURCE=tmdb` и `TMDB_READ_TOKEN=<ваш токен>`.
4. Запустите команду с `--env-file .env` выше. Нужны действующий токен и доступ к TMDB API/изображениям.
5. Вернуться к demo: остановите сервер, установите `DATA_SOURCE=fixture` и снова запустите. Токен можно удалить.

Альтернатива для текущего shell (macOS / Linux, без записи токена в историю):

```bash
export DATA_SOURCE=tmdb
read -r -s TMDB_READ_TOKEN
export TMDB_READ_TOKEN
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
# После Ctrl+C:
unset DATA_SOURCE TMDB_READ_TOKEN
```

Backend вызывает только TMDB `GET /3/discover/movie` с `include_adult=false`, `language=en-US`, `sort_by=popularity.desc` и запрошенной страницей. Токен отправляется только в серверном Authorization header. HTTP timeout — 10 секунд на upstream-запрос; при восстановлении totals для отклонённой страницы возможен второй запрос. Без токена в TMDB-режиме `/api/movies` возвращает безопасный `502`, но `/api/health` продолжает отвечать `200`. Автоматического fallback на fixture нет.

## Endpoints и ручные примеры

Главный документ для QA: **[docs/API_CONTRACT.md](docs/API_CONTRACT.md)**.

```bash
curl -i http://localhost:8000/api/health             # 200, {"status":"ok"}
curl -i http://localhost:8000/api/movies             # 200, 20 фильмов
curl -i 'http://localhost:8000/api/movies?page=2'     # 200, 5 фильмов
curl -i 'http://localhost:8000/api/movies?page=3'     # 200, results=[]
curl -i 'http://localhost:8000/api/movies?page=0'     # 422
curl -i 'http://localhost:8000/api/movies?page=501'   # 422
curl -i 'http://localhost:8000/api/movies?page=abc'   # 422
curl -i 'http://localhost:8000/api/movies?page=1.5'   # 422
curl -I http://localhost:8000/static/style.css       # 200
curl -i http://localhost:8000/docs                   # 200, HTML
```

В fixture ровно 25 вымышленных фильмов, фиксированный порядок и ID 1001–1025. Есть `0`, `7.9`, `8.0`, `8.1`, `10.0`, отсутствующие даты/постер и пустое описание. Локальные постеры не требуют сети. Абсолютные URL постеров используют origin текущего запроса; сравнивайте стабильность данных на одном base URL.

## Структура

```text
app/
  main.py                 # приложение, конфигурация, frontend
  models.py               # схемы публичных ответов
  routes/movies.py         # HTTP endpoint каталога
  providers/
    fixture_provider.py
    tmdb_provider.py
  services/movie_service.py
  static/
    index.html
    style.css
    app.js
    tmdb-logo.svg
    posters/              # 5 локальных SVG-иллюстраций
 data/movies.json
 docs/API_CONTRACT.md
 docs/ROADMAP.md
 docs/CHANGES.md
 docs/SMOKE_CHECK.md
 PRODUCT.md
 DESIGN.md
 .impeccable/design.json   # описание фактических UI-паттернов
 .env.example
 .gitignore
 pyproject.toml
 README.md
```

Пустые `__init__.py` обозначают Python-пакеты. Установка — editable из клонированного репозитория; запуск wheel вне репозитория не является поддерживаемым сценарием MVP.

## Совместная работа

QA использует только публичный контракт, HTTP и UI. Создайте собственный `tests/`, зависимости QA и тесты по своему усмотрению. Для детерминированных проверок используйте fixture, для внешнего smoke — TMDB. Issue: окружение, шаги, ожидаемый/фактический результат, HTTP-ответ. Developer делает небольшой PR с критериями приёмки; QA добавляет регрессию самостоятельно.

Поиск, фильтрация по рейтингу, сортировка, детали и избранное **не реализованы**. Каждый будущий этап — отдельный PR с обновлением API_CONTRACT и CHANGES; см. [ROADMAP](docs/ROADMAP.md).

## Credits / About

Demo-фильмы и SVG-постеры вымышлены и созданы для проекта; это не данные TMDB.

В TMDB-режиме источник данных и постеров — [The Movie Database (TMDB)](https://www.themoviedb.org/).

**This product uses the TMDB API but is not endorsed or certified by TMDB.**

Официальный неизменённый логотип сохранён локально в `app/static/tmdb-logo.svg`, источник: https://files.readme.io/29c6fee-blue_short.svg (логотип официальной документации TMDB). Он показан в Credits менее заметно, чем название приложения; исходные пропорции и цвета сохранены.

Официальные материалы:
- [Discover movie](https://developer.themoviedb.org/reference/discover-movie)
- [Application authentication](https://developer.themoviedb.org/docs/authentication-application)
- [FAQ: attribution requirements](https://developer.themoviedb.org/docs/faq)
- [Approved logos and attribution](https://www.themoviedb.org/about/logos-attribution)

Для использования TMDB вне этого учебного сценария проверьте актуальные условия TMDB и требования к лицензированию.
