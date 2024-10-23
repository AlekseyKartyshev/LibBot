import asyncio
import psycopg2
from decouple import config
from aiogram import F, types
from aiogram.enums import ParseMode


class Db:

    def __init__(self, message):
        try:
            # !Пробуем подключиться к БД
            self.connection = psycopg2.connect(
                host=config("HOST"),
                user=config("USER"),
                password=config("PASSWORD"),
                database=config("DB_NAME"),
            )

            self.connection.autocommit = True

            with self.connection.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS public."{message.chat.id}"
                    (
                        author text COLLATE pg_catalog."default" NOT NULL,
                        book_name text COLLATE pg_catalog."default" NOT NULL,
                        id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
                        cycle text COLLATE pg_catalog."default",
                        cycleid integer NOT NULL DEFAULT 1,
                        genres text COLLATE pg_catalog."default" NOT NULL,
                        CONSTRAINT "{message.chat.id}_pkey" PRIMARY KEY (id)
                    )

                    TABLESPACE pg_default;

                    ALTER TABLE IF EXISTS public."{message.chat.id}"
                        OWNER to postgres;
                    """
                )

        except Exception as e:
            print("[INFO] Error while working with PostgreSQL", e)

    async def add(self, message, list: list):
        if len(message.text.split()) == 2:
            try:
                # !Добавление книги в частную библиотеку
                with self.connection.cursor() as cur:
                    cur.execute(
                        f"""
                            INSERT INTO public."{message.chat.id}" (AUTHOR,BOOK_NAME,ID,CYCLE,CYCLEID,GENRES)
                            SELECT * FROM public.library where id = {message.text.split()[1]}
                        """
                    )
                    cur.execute(
                        f"""
                        SELECT * FROM public."{message.chat.id}"  where id = {message.text.split()[1]}
                        """)
                    await message.answer(f'Книга "{cur.fetchone()[1]}" добавлена в вашу библиотеку')

            except Exception as e:
                print("[INFO] Error while working with PostgreSQL", e)

            return True
        else:
            try:
                # !Добавление книги в общую библиотеку
                with self.connection.cursor() as cur:
                    cur.execute(
                        f"""
                            INSERT INTO library (AUTHOR,BOOK_NAME,CYCLE,CYCLEID,GENRES) VALUES ('{list[1]}','{list[2]}','{list[3]}',{list[4]},'{list[5]}')
                        """
                    )

                try:
                    # !Добавление книги в частную библиотеку
                    with self.connection.cursor() as cur:
                        cur.execute(
                            f"""
                                INSERT INTO public."{message.chat.id}" (AUTHOR,BOOK_NAME,ID,CYCLE,CYCLEID,GENRES)
                                SELECT * FROM public.library where author = '{list[1]}' and BOOK_NAME='{list[2]}' and CYCLE='{list[3]}' and CYCLEID={list[4]} and GENRES='{list[5]}'
                            """
                        )

                except Exception as e:
                    print("[INFO] Error while working with PostgreSQL", e)

                await message.answer('Успешно добавлено')

                return True

            except Exception as e:
                print("[INFO] Error while working with PostgreSQL", e)

    async def mylib(self, message):
        try:
            # !Считывание всех книг в частной библиотеке
            with self.connection.cursor() as cur:
                cur.execute(
                    f"""
                        SELECT * FROM public."{message.chat.id}"
                        ORDER BY "author" ASC, "cycle" ASC, "cycleid" ASC
                        """
                )
                s = ""
                for i in cur.fetchall():
                    s += f"[{i[2]}] " + i[0] + ": " + i[1] + "\n"
                try:
                    await message.answer(s)
                except:
                    await message.answer(
                        "Ваша библиотека пуста, попробуйте добавить в нее книги через комаду /add"
                    )

        except Exception as e:
            print("[INFO] Error while working with PostgreSQL", e)

    async def delete(self, message, list):
        try:
            # !Удаление книги по индексу
            with self.connection.cursor() as cur:
                cur.execute(
                    f"""
                        DELETE FROM public."{message.chat.id}"
	                        WHERE id = {list[1]};
                        """
                )
                
                await message.answer('Книга удалена')

        except Exception as e:
            print("[INFO] Error while working with PostgreSQL", e)

    async def genres(self, message):
        try:
            # !Все жанры которые есть в библиотеке
            with self.connection.cursor() as cur:
                cur.execute(
                    f"""
                        SELECT * from library
                        ORDER BY "author" ASC, "cycle" ASC, "cycleid" ASC
                        """
                )
                s = []
                for i in cur.fetchall():
                    s += i[5].split(", ")
                s = sorted(set(s), key=lambda x: x[0])
                j = ""
                for i in s:
                    j += f"`{i}`\n"
                await message.answer(j, parse_mode=ParseMode.MARKDOWN)

        except Exception as e:
            print("[INFO] Error while working with PostgreSQL", e)

    async def findgen(self, message):
        try:
            # !Все книги в библиотеке по жанру
            with self.connection.cursor() as cur:
                cur.execute(
                    f"""
                        SELECT * FROM public.library WHERE genres LIKE '%{' '.join(message.text.split()[1:])}%'
                        ORDER BY "author" ASC, "cycle" ASC, "cycleid" ASC
                        """
                )
                s=''
                for i in cur.fetchall():
                    s+=f"[{i[2]}] " + i[0] + ": " + i[1] + "\n"
                try:
                    await message.answer(s)
                except:
                    await message.answer(
                        "Книг с таким жанром к сожалению нет:("
                    )

        except Exception as e:
            print("[INFO] Error while working with PostgreSQL", e)
