A discord bot that runs as an Azure Container App that connects to the underground bass radio station and streams the content into a discord voice chat.

# Running locally
## Installing dependencies
Run `pip install -r requirements.txt` (or the same command but with `uv`) to install most of the dependencies.

You'll then want to clone the [discord.py](https://github.com/Rapptz/discord.py) repo and install that with `pip install -e path/to/cloned/repo` so that the dependency is installed from that cloned repo. This is necessary due to a [bug](https://github.com/Rapptz/discord.py/issues/10207) in discord.py that has been fixed in their main branch but has not been pushed to PyPI yet.

## Running
Simply run with `python main.py` or `uv run .main.py`