import asyncio
import logging
import psycopg2
from db import Db
from decouple import config
from create_bot import bot, dp
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram import F,types



@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('''Это бот-библиотека 
Он может добавлять книги в библиотеку, может удалять книги из нее, а так же осуществляет поиск книг из общей библиотеки по жанрам''')


@dp.message(Command("about"))
async def cmd_start(message: types.Message):
    await message.answer(
        """
        Этот бот был разработан в качестве итогового проекта студентом СмолГУ 

Он предназначен для поиска книг по жанрам

На данный момент добавлены не все книги, но я стараюсь это исправить:)
        """
    )

@dp.message(Command("help"))
async def cmd_start(message: types.Message):
    await message.answer(
        """
        После того как вы отправили команду start (если вы читаете этот текст, то вы это уже сделали) бот создал вашу личную библиотеку

Однако она еще пуста, и чтобы добавить в нее книги есть 2 способа:

1. С помощью команды /genres или /g бот выведет вам список всех жанров всех книг, что есть в общей библиотеке. Далее при помощи тех же команд, приписав к ним жанр, вы получите список всех книг в библиотеке с этим жанром. Не стоит бояться что вы ошибетесь в названии жанра, чтобы этого избежать все названия сделаны при помощи текста который можно скопировать, нажав на него (`как этот текст`)
Команда должна иметь вид /g <жанр>
После того как отобразились книги, в самом начале в квадратных скобках вы можете найти индекс книги в библиотеке
Осталось написать команду /add <индекс желаемой книги>

2. Второй способ предполагает, что книги еще нет в нашей библиотеке и вам придется добавить ее самому
Однако это не так сложно как кажется:
/add
<Автор>
<Название произведения>
<Название цикла>
<Порядковый номер книги в цикле>
<Жанры через запятую>
Главное точно указать все данные на разных строках

Чтобы удостовериться, что вы правильньно добавили все книги напишите команду /my 
Отобразится вся ваша библиотека и вы сможете проверить наличие книг

Если вы желаете удалить книгу из библиотеки, то напишите команду /del <индекс книги> и она удалится из вашей библиотеки

Спасибо, что выбрали этот бот:)
        """, parse_mode=ParseMode.MARKDOWN
    )


@dp.message(F.text[:4]=='/add')
async def cmd_add(message: types.Message):
    db = Db(message)
    if await db.add(message,message.text.split('\n')):
        pass
    else:
        await message.answer("""Проверьте введенные данные на правильность:
&#60;Автор&#62;
&#60;Название произведения&#62;
&#60;Название цикла&#62;
&#60;Порядковый номер книги в цикле&#62;
&#60;Жанры&#62;""")
        
@dp.message(Command('my'))
async def cmd_add(message: types.Message):
    db = Db(message)
    await db.mylib(message)

@dp.message(Command('genres'))
async def cmd_add(message: types.Message):
    db = Db(message)
    if len(message.text.split()) >1:
        pass
        await db.findgen(message)
    else:
        await db.genres(message)

@dp.message(Command('g'))
async def cmd_add(message: types.Message):
    db = Db(message)
    if len(message.text.split()) >1:
        pass
        await db.findgen(message)
    else:
        await db.genres(message)

@dp.message(F.text[:4]=='/del')
async def cmd_add(message: types.Message):
    db = Db(message)
    await db.delete(message,message.text.split())

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
