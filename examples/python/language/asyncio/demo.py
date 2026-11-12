import asyncio
from time import perf_counter


async def fetch(name: str) -> str:
    await asyncio.sleep(0.2)  # Simulate waiting for a response.
    return name


async def main() -> None:
    started = perf_counter()
    first = await fetch("A")
    second = await fetch("B")
    elapsed = perf_counter() - started
    print(f"sequential: {first}, {second} ({elapsed:.2f} s)")

    started = perf_counter()
    async with asyncio.TaskGroup() as group:
        first_task = group.create_task(fetch("A"))
        second_task = group.create_task(fetch("B"))
    elapsed = perf_counter() - started
    print(f"concurrent: {first_task.result()}, {second_task.result()} ({elapsed:.2f} s)")


if __name__ == "__main__":
    asyncio.run(main())
