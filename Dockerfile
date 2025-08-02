FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt install ffmpeg libffi-dev libnacl-dev python3-dev git -y

# Joining voice is broken in 2.5.x so install from source since
# the fix is in the master branch
RUN git clone https://github.com/Rapptz/discord.py.git

RUN cd discord.py
RUN ls
RUN pip install -e 'discord.py[voice]'
RUN pip install asyncio

RUN cd /app

COPY . .

ENV DISCORD_TOKEN=$DISCORD_TOKEN

CMD ["python", "main.py"]
