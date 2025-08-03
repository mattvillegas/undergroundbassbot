FROM python:3.13.5-bookworm

WORKDIR /app

RUN  apt-get update && apt install deb libffi-dev libnacl-dev python3-dev git -y
RUN deb http://deb.debian.org/debian bookworm-backports main contrib non-free && apt update && apt install ffmpeg/bookworm-backports
RUN ffmpeg -h long

# Joining voice is broken in 2.5.x so install from source since
# the fix is in the master branch
RUN git clone https://github.com/Rapptz/discord.py.git
WORKDIR /app/discord.py
RUN pip install -e '.[voice]'

WORKDIR /app
COPY . .

RUN chmod +x run.sh

CMD ["bash", "run.sh"]