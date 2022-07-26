import aiohttp
import asyncio
import requests

from funcy import print_durations


async def get_pokemon(session, url):
    async with session.get(url) as resp:
        pokemon = await resp.json()
        return pokemon['name']


async def main():
    async with aiohttp.ClientSession() as session:

        tasks = []
        for number in range(1, 20):
            url = f'https://pokeapi.co/api/v2/pokemon/{number}'
            tasks.append(asyncio.ensure_future(get_pokemon(session, url)))

        original_pokemon = await asyncio.gather(*tasks)
        for pokemon in original_pokemon:
            print(pokemon)


with print_durations:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())


def get_pokemon(url):
    with requests.get(url) as resp:
        pokemon = resp.json()
        return pokemon['name']


def sync_main():
    for number in range(1, 20):
        url = f'https://pokeapi.co/api/v2/pokemon/{number}'
        original_pokemon = get_pokemon(url)

        print(original_pokemon)


with print_durations:
    sync_main()
