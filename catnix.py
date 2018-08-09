#!/usr/bin/env python3

import praw
import json
import time
import discord
import threading
import asyncio
import pickle

discord_client  = None

class RedditScraper(threading.Thread):
    def __init__(self, reddit_config, discord_channel):
        threading.Thread.__init__(self)
        self.setName('reddit scraper thread')

        self.reddit  = praw.Reddit(client_id=reddit_config['client_id'],
                                   client_secret=reddit_config['client_secret'],
                                   user_agent='catpix')
        self.channel = discord_client.get_channel(discord_channel)
        self.config = reddit_config

        try:
            with open('reddit_visited.temp', 'rb') as f:
                self.visited = pickle.load(f)
        except Exception:
            self.visited = set()


    def run(self):
        while True:
            for sr in self.config['subreddits']:
                for submission in self.reddit.subreddit(sr).hot(limit=10):
                    if submission.fullname not in self.visited and submission.url:
                        self.visited.add(submission.fullname)
                        sendco = discord_client.send_message(self.channel, '```{}```{}'.format(submission.title, submission.url))
                        asyncio.run_coroutine_threadsafe(sendco, discord_client.loop)
                        time.sleep(3)
            
            with open('reddit_visited.temp', 'wb') as f:
                pickle.dump(self.visited, f)
                
            time.sleep(600)


if __name__ == '__main__':
    discord_client = discord.Client()
    config = None

    with open('config.json') as f:
        config = json.load(f)

    @discord_client.event
    async def on_ready():
        print('Logged in as')
        print(discord_client.user.name)
        print(discord_client.user.id)
        print('------')

        RedditScraper(config['reddit'], config['discord']['channel']).start()

    discord_client.run(config['discord']['token'])