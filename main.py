import time
from twitchio.ext import commands, eventsub
from twitchio.ext.commands import Bucket
import sqlite3
from config import TOKEN, My_TOKEN, CLIENT_ID
import os
import random
import pygame
import asyncio
import datetime
from os import listdir
from os.path import isfile, join
import math
from twitchio.ext.commands.errors import (
    BadArgument,
    CommandNotFound,
    MissingRequiredArgument,
    CommandOnCooldown
)

bot_token = TOKEN
my_token = My_TOKEN

bot = commands.Bot(token=bot_token, prefix="!", initial_channels=["CHANNEL_NAME"])

connection = sqlite3.connect('user.db')
cursor = connection.cursor()

os.chdir(os.getcwd() + "\sounds")

sound_activety = True

pygame.init()

# Функция для отправки сообщения в чат
littleboss_users = []
littleboss_hp = 250
littleboss_spawn = False
littleboss_time = 300

bigboss_users = []
bigboss_hp = 500
bigboss_spawn = False
bigboss_time = 300


@bot.event()
async def event_ready():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        name TEXT,
        cash BIGINT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS config(
    cooldawnUser INT,
    cooldawnGlobal INT
    )""")
    connection.commit()
    print("Connected!")
    print(f"logged on as {bot.nick}")
    print(f"user id is {bot.user_id}")
    bot.loop.create_task(my_event())


async def my_event():
    while True:
        global bigboss_time
        global littleboss_time
        global littleboss_spawn
        global littleboss_hp
        global bigboss_hp
        global bigboss_spawn
        if littleboss_hp <= 0:
            bigboss_spawn = False
            littleboss_hp = 500
            users_active_with_littleboss = len(littleboss_users)
            print(users_active_with_littleboss)
            cash_value = 2500 / users_active_with_littleboss
            print(cash_value)
            print(round(cash_value))
            print(littleboss_users)
            cash_value = round(cash_value)
            for user in littleboss_users:
                cursor.execute("UPDATE users SET cash = cash + ? WHERE name = ?", (cash_value, user))
                connection.commit()
                print(user)
            for user in littleboss_users:
                littleboss_users.remove(user)
        elif bigboss_hp <= 0:
            bigboss_hp = 500
            bigboss_spawn = False
            users_active_with_bigboss = len(bigboss_users)
            print(users_active_with_bigboss)
            cash_value = 5000 / users_active_with_bigboss
            cash_value = round(cash_value)
            for user in bigboss_users:
                cursor.execute("UPDATE users SET cash = cash + ? WHERE name = ?", (cash_value, user))
                connection.commit()
                print(user)
            for user in bigboss_users:
                bigboss_users.remove(user)
        else:
            if bigboss_time <= 1:
                bigboss_spawn = False
                for user in bigboss_users:
                    bigboss_users.remove(user)
                bigboss_time -= 1
                littleboss_time -= 1
            elif littleboss_time <= 1:
                littleboss_spawn = False
                for user in littleboss_users:
                    littleboss_users.remove(user)
                bigboss_time -= 1
                littleboss_time -= 1
            else:
                bigboss_time -= 1
                littleboss_time -= 1
        await asyncio.sleep(1)  # Приостанавливаем выполнение на 1 секунду


@bot.command(name="youtube")
async def youtube_url(ctx: commands.Context):
    await ctx.send("Записи стримов - youtube.com/@man0fsky_streams ┊┊ Шортсы и др. - youtube.com/@Man0fSky_Channel ")


@bot.command(name="discord")
async def discord_url(ctx: commands.Context):
    await ctx.send("Дискорд нашей секты - discord.com/invite/FMzZZ2t6j7")


def get_cooldawnUser_from_config():
    # Получение значения volume из таблицы config
    cursor.execute('''
        SELECT cooldawnUser FROM config
    ''')

    # Извлечение результата запроса
    result = cursor.fetchone()

    # Возврат извлеченного значения или None, если записей не найдено
    if result:
        return result[0]
    else:
        return None


def get_cooldawnGlobal_from_config():
    # Получение значения volume из таблицы config
    cursor.execute('''
        SELECT cooldawnGlobal FROM config
    ''')

    # Извлечение результата запроса
    result = cursor.fetchone()

    # Возврат извлеченного значения или None, если записей не найдено
    if result:
        return result[0]
    else:
        return None


@bot.command(name="pistrun")
@commands.cooldown(1, 1200, Bucket.user)
async def penis_metr(ctx: commands.Context):
    author = ctx.author.name
    cursor.execute("UPDATE users SET cash = cash - ? WHERE name = ?", (5, author))
    connection.commit()
    await ctx.reply(f"Твой член сейчас: {random.randint(1, 35)}см")


@bot.command(name="volume")
async def volume_change(ctx: commands.Context, num: str):
    if ctx.author.is_mod and ctx.author.is_broadcaster:
        if num is None:
            await ctx.reply("Введите значение громкости!")
        else:
            with open('volume.txt', 'w') as file:
                file.write(f'{num}')

            print("Ready!")
            await ctx.reply(f"громкость изменена на {num}")
    else:
        print("non mod!")
        await ctx.reply("У вас нет прав модерации!")


def check_user(name):
    # Выполнение запроса на поиск пользователя по имени
    cursor.execute("SELECT * FROM users WHERE name=?", (name,))

    # Получение результата запроса
    result = cursor.fetchone()

    # Проверка результата
    if result is not None:
        return True
    else:
        return False


def check_cash(name):
    query = f"SELECT * FROM users WHERE name = ? AND cash >= 20"
    cursor = connection.execute(query, (name,))
    result = cursor.fetchone()

    if result is not None:
        return True
    else:
        return False


cooldown = 10  # Cooldown duration in seconds
last_called = 0  # Variable to store the timestamp of the last function call


@bot.event()
async def event_message(message):
    global last_called
    msg_send = message.content
    author = message.author.name
    print(msg_send)
    onlyfiles = [f for f in listdir(os.getcwd()) if
                 isfile(join(os.getcwd(), f))]  # прогоняем папку и имена файлов суем в список
    print(onlyfiles)
    if msg_send[:1] == "!":  # сверяем команда ли это
        msg_send = msg_send[1:]
        if msg_send + ".mp3" in onlyfiles:  # проверка есть ли данный звук в списке файлов
            current_time = time.time()
            if current_time - last_called < cooldown:
                print("Условие выполнилось!")
                print(current_time)
                print(last_called)
                return
            last_called = current_time
            name_sound = msg_send + ".mp3"
            print(name_sound)
            if check_cash(author):  # проверка бабла у пользователя
                with open('volume.txt', 'r') as File:  # это берем громкость для звука
                    Volume = File.read()
                """А тут алгоритм для воспроизведения звука"""
                pygame.mixer_music.load(f'{name_sound}')
                pygame.mixer_music.set_volume(float(Volume))
                pygame.mixer_music.play()
                """Отнимаем бабло и сохраняем"""
                cursor.execute("UPDATE users SET cash = cash - ? WHERE name = ?", (20, author))
                connection.commit()
            else:
                await message.channel.send(f"{author}, у вас недостаточно пряников!")


def check_cash_thief(name):
    query = f"SELECT * FROM users WHERE name = ? AND cash >= 300"
    cursor = connection.execute(query, (name,))
    result = cursor.fetchone()

    if result is not None:
        return True
    else:
        return False


def check_cash_thief_name(name):
    query = f"SELECT * FROM users WHERE name = ? AND cash == 0"
    cursor = connection.execute(query, (name,))
    result = cursor.fetchone()
    if result is not None:
        return True
    else:
        return False


@bot.command(name="вор")
@commands.cooldown(1, 3600, Bucket.user)
async def __theft(ctx: commands.Context, name: str):
    random_moment = random.randint(1, 100)
    name = name[1:]
    author = ctx.author.name.lower()
    key_random = random_moment
    cursor.execute("UPDATE users SET cash = cash - ? WHERE name = ?", (500, author))
    connection.commit()
    if author == name:
        await ctx.reply(f"Вы не можете себя обокрасть!")
    else:
        if key_random <= 95:
            if check_cash_thief(author):
                cursor.execute("UPDATE users SET cash = cash - ? WHERE name = ?", (500, author))
                connection.commit()
                await ctx.send(f"@{author} спалился за воровством и получил по шапке и штраф 500 пряников")
            else:
                await ctx.send(f"@{author} спалился за воровством и получил по шапке и штраф 500 пряников")
                print("Error 404")
        else:
            if check_cash_thief_name(name):
                await ctx.reply(f"@{author} , Вы удачно обокрали нищего, у которого ничего нет, поздравляю")
            else:
                print(get_cash_for_user(name))
                cash_name = int(get_cash_for_user(name)) / 3
                print(round(cash_name))
                random_moment_2 = random.randrange(1, round(cash_name))
                key2_random = random_moment_2
                cursor.execute("UPDATE users SET cash = cash - ? WHERE name = ?", (key2_random, name))
                cursor.execute("UPDATE users SET cash = cash + ? WHERE name = ?", (key2_random, author))
                connection.commit()
                await ctx.send(f"@{author} умыкнул у @{name} {key2_random} пряников")


@bot.command(name="offonsound")
async def off_sound(ctx: commands.Context):
    if ctx.author.is_mod and ctx.author.is_broadcaster:
        global sound_activety
        sound_activety = not sound_activety
        print("звук был изменен")
        await ctx.reply(f"звук был изменен на {sound_activety}")
    else:
        await ctx.reply("Вы не модератор!")


def get_cash_for_user(name):
    # Запрос для выборки значения столбца "cash" для указанного пользователя
    query = "SELECT cash FROM users WHERE name = ?"
    cursor.execute(query, (name,))

    result = cursor.fetchone()  # Получение первой строки результата запроса

    if result is None:
        return 'ERROR value(Возможно вас нет в базе данных)'
    else:
        cash = result[0]
        return cash


@bot.command(name="balance")
async def balance(ctx: commands.Context):
    author = ctx.author.name
    print(author)
    await ctx.reply(f"У вас сейчас {get_cash_for_user(author)} пряников")


@bot.command(name="littleboss")
@commands.cooldown(1, 3600, Bucket.channel)
async def littleboss_summon(ctx: commands.Context):
    global littleboss_time
    global littleboss_spawn
    global bigboss_spawn
    if bigboss_spawn:
        await ctx.send("Извините, но уже призван большой босс")
    else:
        author = ctx.author.name.lower()
        cursor.execute("UPDATE users SET cash = cash - ? WHERE name = ?", (10, author))
        connection.commit()
        await ctx.send(
            f"@{author}, вызвал лоу лвл бомжа, валите его на бок, ломайте ему хуй!")
        littleboss_spawn = True
        littleboss_time = 300


@bot.command(name="bigboss")
@commands.cooldown(1, 3600, Bucket.channel)
async def bigboss_summon(ctx: commands.Context):
    global bigboss_spawn
    global bigboss_time
    global littleboss_spawn
    if littleboss_spawn:
        await ctx.send("Извините, но уже призван маленький босс")
    else:
        author = ctx.author.name.lower()
        cursor.execute("UPDATE users SET cash = cash - ? WHERE name = ?", (50, author))
        connection.commit()
        await ctx.send(
            f"@{author}, вызвал серьёзного дядю в чат, покажите ему, кто босс этой качалки!")
        bigboss_spawn = True
        bigboss_time = 300


woord_for_0_damage = ["моя бабка сильнее бьёт!", "если продолжишь в том же духе, босс просто развернётся и уйдет!"]


@bot.command(name="attack")
@commands.cooldown(1, 15, Bucket.user)
async def attack_boss(ctx: commands.Context):
    global littleboss_spawn
    global littleboss_hp
    global littleboss_users
    global bigboss_spawn
    global bigboss_hp
    global bigboss_users
    author = ctx.author.name
    if check_user(author):  # проверка есть ли user в БД
        if littleboss_spawn:
            """логика рандома урона"""
            key_moment_random = random.randint(0, 50)
            key_moment_damage = key_moment_random
            littleboss_hp -= key_moment_damage
            if key_moment_damage == 0:
                await ctx.send(
                    f"{author}, нанес {key_moment_damage} урона, {random.choice(woord_for_0_damage)} HP: {littleboss_hp} Time: {littleboss_time}")
            elif key_moment_damage >= 1 and key_moment_damage <= 18:
                await ctx.send(
                    f"{author}, нанёс {key_moment_damage}, так держать, мамкин боец! HP: {littleboss_hp} Time: {littleboss_time}")
            elif key_moment_damage >= 19 and key_moment_damage <= 30:
                await ctx.send(
                    f"{author}, нанёс {key_moment_damage}, неплохой удар! HP: {littleboss_hp} Time: {littleboss_time}")
            elif key_moment_damage >= 31 and key_moment_damage <= 50:
                await ctx.send(
                    f"{author}, нанёс {key_moment_damage}, босс приахуел с такого поворота событий! HP: {littleboss_hp} Time: {littleboss_time}")

            if author in littleboss_users:  # условие если пользователь есть в списке
                print("Пользователь участвует!")
                if littleboss_hp <= 0:
                    littleboss_spawn = False
                    await ctx.send(
                        f"{author}, нанес решающий удар и завалил Лоу лвл бомжа, награда будет распределена между братьями по оружию! {', '.join(littleboss_users)}")
            else:
                if littleboss_hp <= 0:
                    littleboss_spawn = False
                    await ctx.send(
                        f"{author}, нанес решающий удар и завалил Лоу лвл бомжа, награда будет распределена между братьями по оружию! {', '.join(littleboss_users)}")

                littleboss_users.append(author)
        elif bigboss_spawn:
            """логика рандома урона"""
            key_moment_random = random.randint(0, 100)
            key_moment_damage = key_moment_random
            bigboss_hp -= key_moment_damage
            if key_moment_damage == 0:
                await ctx.send(
                    f"{author}, нанес {key_moment_damage} урона, {random.choice(woord_for_0_damage)} HP: {bigboss_hp} Time: {bigboss_time}")
            elif key_moment_damage >= 1 and key_moment_damage <= 32:
                await ctx.send(
                    f"{author}, нанёс {key_moment_damage}, так держать, мамкин боец! HP: {bigboss_hp} Time: {bigboss_time}")
            elif key_moment_damage >= 33 and key_moment_damage <= 62:
                await ctx.send(
                    f"{author}, нанёс {key_moment_damage}, неплохой удар! HP: {bigboss_hp} Time: {bigboss_time}")
            elif key_moment_damage >= 63 and key_moment_damage <= 100:
                await ctx.send(
                    f"{author}, нанёс {key_moment_damage}, босс приахуел с такого поворота событий! HP: {bigboss_hp} Time: {bigboss_time}")
            if author in bigboss_users:
                print("Пользователь участвует!")
                if bigboss_hp <= 0:
                    bigboss_spawn = False
                    await ctx.send(
                        f"{author}, нанес решающий удар и завалил серьезного дядю, награда будет распределена между братьями по оружию! {', '.join(bigboss_users)}")
            else:
                bigboss_users.append(author)
                if bigboss_hp <= 0:
                    bigboss_spawn = False
                    await ctx.send(
                        f"{author}, нанес решающий удар и завалил серьезного дядю, награда будет распределена между братьями по оружию! {', '.join(bigboss_users)}")
        else:
            await ctx.send("Босс уже мёртв или ещё не реснулся")
    else:
        print("Пользователя нет в БД!")
        cursor.execute(f"INSERT INTO users VALUES ('{author}', 0)")
        cursor.execute("UPDATE users SET cash = cash + ? WHERE name = ?", (100, author))
        connection.commit()
        key_moment_random = random.randint(0, 15)
        key_moment_damage = key_moment_random
        littleboss_hp -= key_moment_damage
        await ctx.send(f"{author}, нанёс {key_moment_damage}")
        littleboss_users.append(author)


nameDueller = []
cash_value_duel = []
active_duel = False
words_duel = ["Желающий сразиться, напиши !duel в чате, чтобы принять бой на шпагах",
              "Желающий сразиться, напиши !duel в чате, чтобы выяснить, чей член больше",
              "Желающий сразиться, напиши !duel в чате, чтобы столкнуться лицом к лицу с потерей пряников",
              "Желающий сразиться, напиши !duel в чате, чтобы узнать, чьё конг-фу сильнее"]


@bot.command(name="duel")
@commands.cooldown(1, 1500, Bucket.user)
async def duel_command(ctx: commands.Context, money: int = None):
    global active_duel
    global nameDueller
    if active_duel and money is None:
        if ctx.author.name in nameDueller:
            await ctx.send("Вы уже в ожиданиях дуэли")
        else:
            print("fight is active!")
            random_moment = random.randint(1, 100)
            oprediltel_num = random_moment  # определяем победителя вызвав рандом
            if oprediltel_num <= 50:
                Dueller = nameDueller[0]
                await ctx.send(f"в дуэли между {Dueller} и {ctx.author.name} победил в дуэле {Dueller}!")
                cursor.execute("UPDATE users SET cash = cash +? WHERE name =?", (cash_value_duel[0], Dueller))
                cursor.execute("UPDATE users SET cash = cash -? WHERE name =?",
                               (cash_value_duel[0], ctx.author.name.lower()))
                connection.commit()
                nameDueller.pop(0)
                cash_value_duel.pop(0)
            elif oprediltel_num >= 51:
                Dueller = nameDueller[0]
                await ctx.send(f"в дуэли между {Dueller} и {ctx.author.name} победил в дуэле {ctx.author.name}!")
                cursor.execute("UPDATE users SET cash = cash -? WHERE name =?", (cash_value_duel[0], Dueller))
                cursor.execute("UPDATE users SET cash = cash +? WHERE name =?",
                               (cash_value_duel[0], ctx.author.name.lower()))
                connection.commit()
                nameDueller.pop(0)
                cash_value_duel.pop(0)
    else:
        if money is None:
            await ctx.send("Введите сумму для дуэли")
        else:
            await ctx.send(f"{random.choice(words_duel)}")
            nameDueller.append(ctx.author.name.lower())
            cash_value_duel.append(100)
            active_duel = True


"""Обработчик событий ошибок команд
включает:(
    BadArgument,
    CommandNotFound,
    MissingRequiredArgument,
    CommandOnCooldown
)
"""

word_for_attack_cd = ["ты пока не можешь атаковать, идёт перезарядка сабли!",
                      "ля какой резвый, погоди немного, дай сабле остыть!"]


@bot.event()
async def event_command_error(context: commands.Context, error: Exception):
    if isinstance(error, commands.CommandOnCooldown):
        print(error.command.name)
        if error.command.name == "duel":
            await context.send(f"Дуэль нельзя {error.retry_after:.2f} секунд")
        elif error.command.name == "attack":
            await context.send(
                f"{context.author.name} - {random.choice(word_for_attack_cd)} {error.retry_after:.2f} секунд")
        elif error.command.name == "вор":
            await context.send(
                f"Не стоит привлекать много внимания так часто, попробуйте позже: {error.retry_after:.2f} сек.")
        elif error.command.name == "littleboss" or error.command.name == "bigboss":
            await context.send(
                f"Босс пока спит или на обеде, будет тогда, когда вернётся! {error.retry_after:.2f} сек.")
        else:
            await context.send(
                f"попробуйте позже через {error.retry_after:.2f} сек.")


@bot.command(name="duel_close")
async def duel_close_command(ctx: commands.Context):
    global active_duel
    if ctx.author.name in nameDueller:
        active_duel = False
        await ctx.send("Дуэль закрыта")
        nameDueller.remove(ctx.author.name.lower())
    else:
        await ctx.send("Вы не объявляли дуэль")


reward_id_1k1 = "d9be1c53-89ab-447f-8271-99234194cc34"
reward_id_1k2 = "c8d6e96f-197a-43fa-83af-ff9274ae5036"
reward_id_10k = "0cc1a659-385a-4f3c-925d-4d4184297c79"


@bot.event()
async def event_eventsub_notification_channel_reward_redeem(
        payload: eventsub.CustomRewardRedemptionAddUpdateData) -> None:
    author = payload.data.user.name
    author = author.lower()
    print('Received event!')
    print("time:\t", payload.data.redeemed_at)
    print("user:\t", payload.data.user.name)
    print("id Rewards:\t", payload.data.reward.id)
    id_reward = payload.data.reward.id
    if check_user(author):
        print("users in BD")
        if id_reward == reward_id_1k1:
            cursor.execute("UPDATE users SET cash = cash + ? WHERE name = ?", (1000, author))
            connection.commit()
            print(f"Добавлено {1000} к cash пользователю {author}! 😊")
        elif id_reward == reward_id_1k2:
            random_moment = random.randint(1, 100)
            key_moment = random_moment
            if key_moment <= 85:
                print(key_moment)
                cursor.execute("UPDATE users SET cash = cash + ? WHERE name = ?", (2000, author))
                connection.commit()
                print(f"Добавлено {2000} к cash пользователю {author}! 😊")
            else:
                print("неудача(")
        elif id_reward == reward_id_10k:
            cursor.execute("UPDATE users SET cash = cash + ? WHERE name = ?", (10000, author))
            connection.commit()
            print(f"Добавлено {10000} к cash пользователю {author}! 😊")
    else:
        print("Пользователя нет в БД!")
        cursor.execute(f"INSERT INTO users VALUES ('{author}', 0)")
        cursor.execute("UPDATE users SET cash = cash + ? WHERE name = ?", (100, author))
        connection.commit()
        print(f"Добавлено {100} к cash пользователю {author}! 😊")
        connection.commit()

    print("ready!")


async def sub():
    esclient = eventsub.EventSubWSClient(bot)
    await esclient.subscribe_channel_points_redeemed(broadcaster=704853458, token=my_token)


bot.loop.create_task(sub())
bot.run()
