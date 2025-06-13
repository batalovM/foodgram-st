# Foodgram - "Продуктовый помощник"

![Workflow Status](https://github.com/batalovM/foodgram-st/actions/workflows/docker-publish.yml/badge.svg)

## Описание проекта

"Продуктовый помощник" - это веб-приложение, которое позволяет пользователям публиковать рецепты, добавлять понравившиеся рецепты в избранное, подписываться на авторов и формировать список покупок на основе выбранных рецептов.

## Технологии
- Python 
- Django 
- Django REST Framework
- PostgreSQL
- Docker
- Nginx
- React

## Инструкция по запуску проекта

### Предварительные требования
- Docker и Docker Compose
- Git

### Шаг 1: Клонирование репозитория
```bash
git clone https://github.com/batalovM/foodgram-st.git
cd foodgram-st
```
### Шаг 2: Настройка переменных окружения
Создайте файл .env в корне проекта со следующими переменными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key_here
```
### Шаг 3: Запуск проекта
Находясь в папке infra, выполните команду:
```bash
docker-compose up -d
```
При выполнении этой команды:

Контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу
Будет запущен backend на Django, выполнены миграции и загружены начальные данные
Nginx будет настроен как прокси-сервер

### Шаг 4: проверка работоспособности
- Фронтенд доступен по адресу: http://localhost
- Документация API доступна по адресу: http://localhost/api/docs/
- Панель администратора: http://localhost/admin/
Доступные учетные записи
После запуска проекта автоматически создаются тестовые учетные записи:

| Логин      | Пароль     | Роль           |
|------------|------------|----------------|
| admin@example.com      | admin      | Администратор  |
| test1@example.com | password123 | Пользователь   |
| test2@example.com | password123 | Пользователь   |
| test3@example.com | password123 | Пользователь   |
| test4@example.com | password123 | Пользователь   |
| test5@example.com | password123 | Пользователь   |

Основная функциональность
Просмотр рецептов
Создание, редактирование и удаление собственных рецептов
Добавление рецептов в избранное
Подписки на авторов
Формирование списка покупок
Фильтрация рецептов
### API
Полная документация API доступна по адресу http://localhost/api/docs/

Основные эндпоинты:
- /api/users/ - Управление пользователями
- /api/recipes/ - Управление рецептами
- /api/ingredients/ - Просмотр ингредиентов
- /api/auth/token/login/ - Получение токена для авторизации
### Автор проекта
Максим Баталов 
