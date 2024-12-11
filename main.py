import asyncio

import uvicorn
from app import app

import os
from WallEve import client

async def start_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

# Main function to run both bot and server
async def main():
    # Create tasks for the Discord bot and FastAPI server
    bot_task = asyncio.create_task(client.start(os.environ.get("DISCORD_BOT_TOKEN")))
    server_task = asyncio.create_task(start_server())

    # Wait for both tasks to complete
    await asyncio.gather(bot_task, server_task)

# Run everything (compatible with running event loop)
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # Handle environments with running event loops
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
