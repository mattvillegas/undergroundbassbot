FROM python:3.13.5-bookworm

WORKDIR /app
RUN echo "deb http://deb.debian.org/debian bookworm-backports main contrib non-free" | tee /etc/apt/sources.list.d/backports.list

RUN apt update && apt install libffi-dev libnacl-dev python3-dev git ffmpeg/bookworm-backports -y
RUN ffmpeg -h long

# Joining voice is broken in 2.5.x so install from source since
# the fix is in the master branch
RUN git clone https://github.com/Rapptz/discord.py.git

RUN cd discord.py
RUN ls
RUN pip install -e 'discord.py[voice]'
RUN pip install asyncio

RUN cd /app

COPY . .

CMD ["python", "main.py"]
