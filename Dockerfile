# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt install ffmpeg libffi-dev libnacl-dev python3-dev git -y

# Joining voice is broken in 2.5.x so install from source since
# the fix is in the master branch
RUN git clone https://github.com/Rapptz/discord.py.git

RUN cd discord.py
RUN ls
RUN pip install -e 'discord.py[voice]'
RUN pip install asyncio

RUN cd /app

# Copy the rest of the application's code
COPY . .

# Set the Discord token from an environment variable
ENV DISCORD_TOKEN=$DISCORD_TOKEN

# Define the command to run your bot
CMD ["python", "main.py"]
