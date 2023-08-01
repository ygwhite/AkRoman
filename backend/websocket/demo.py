# Мини модель websocket сервера (в проекте не используется)
import asyncio as aio
from random import randint, choice

loop = aio.new_event_loop()
queue = aio.Queue()  # очередь задач
count = [0]  # порядковый номер подключения
exec_limit = 3  # лимит задач извлекаемых из очереди
data = dict()  # какие-то данные приходящие от задач


async def open():
    "Обработчик нового подключения"
    global loop
    global queue
    global count
    global data

    await queue.put(loop.create_task(open_task(count, data)))


async def open_task(count, data):
    await aio.sleep(0)
    k = count[0]
    data[k] = True
    count[0] += 1
    await aio.sleep(randint(0, 2))
    print(f"Open", k)


async def close():
    "Обработчик закрытия подключения"
    global loop
    global queue
    global data

    await queue.put(loop.create_task(close_task(data)))


async def close_task(data):
    await aio.sleep(0)
    if len(data.keys()) > 0:
        k = choice(tuple(data.keys()))
        data.pop(k)
        await aio.sleep(randint(0, 2))
        print(f"Close", k)


async def spawn():
    "Цикл симуляции происшествия событий open/close"

    while True:
        f = choice([open, close])
        await f()
        await aio.sleep(randint(0, 3))


async def cycle():
    "Конкурентный цикл исполнения задач"
    global queue
    global data
    global exec_limit

    while True:
        print("Entering queue")

        for i in range(exec_limit):
            try:
                task = await queue.get()
                await task
            except Exception as e:
                print(e)

        print(f"Processing data {data}")
        await aio.sleep(0.5)


def main():
    "Запуск конкурентных циклов"
    global loop

    g = aio.gather(
        loop.create_task(spawn()),
        loop.create_task(cycle())
    )

    loop.run_until_complete(g)


if __name__ == "__main__":
    main()
