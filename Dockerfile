FROM docker.io/jrottenberg/ffmpeg:7.1-ubuntu2404

WORKDIR /app

RUN apt update && apt install curl libffi-dev libnacl-dev python3-dev git -y
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv python install 3.13.5


# Joining voice is broken in 2.5.x so install from source since
# the fix is in the master branch
RUN git clone https://github.com/Rapptz/discord.py.git
RUN uv venv
RUN uv pip install -e 'discord.py[voice]'

COPY . .
RUN uv pip install -r requirements.txt

CMD ["uv", "run", "main.py"]
