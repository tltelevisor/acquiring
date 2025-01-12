# Файл подгатавливает схему в базе данных "с нуля"
# Все старые таблицы в базе данных нужно удалить
# (вклюячая alembic_version)
# скрипт выполнять в корневой папке проекта
rm -r app/migration
cd app
alembic init -t async migration
cp env.py ./migration/
cd ..
alembic revision --autogenerate -m "Initial revision"
alembic upgrade head