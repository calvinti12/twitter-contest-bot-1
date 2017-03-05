
from settings.settings import *

import os
from slackclient import SlackClient

print SLACK_BOT_TOKEN

slack_client = SlackClient(SLACK_BOT_TOKEN)

slack_client.api_call("api.test")



def list_channels():
    channels_call = slack_client.api_call("channels.list")
    if channels_call['ok']:
        return channels_call['channels']
    return None


def channel_info(channel_id):
    channel_info = slack_client.api_call("channels.info", channel=channel_id)
    if channel_info:
        return channel_info['channel']
    return None


def send_message(channel_id, message):
    slack_client.api_call(
        "chat.postMessage",
        channel=channel_id,
        text=message,
        username='Twitter Competition Bot',
        icon_emoji=':robot_face:'
    )

def get_channel_id_from_name(name):
    channels = list_channels()
    if channels:
        for channel in channels:
            if channel['name'] == name:
                return channel['id']

    return False


if __name__ == '__main__':
    channels = list_channels()
    if channels:
        print("Bot activated")
    #     for channel in channels:
    #         print(channel['name'] + " (" + channel['id'] + ")")
    #         detailed_info = channel_info(channel['id'])
    #         if detailed_info:
    #             print('Latest text from ' + channel['name'] + ":")
    #             print(detailed_info)
    #         if channel['name'] == 'bots':
    #             send_message(channel['id'], "Hello " +
    #                          channel['name'] + "! It worked!")
    #     print('-----')
    else:
        print("Unable to authenticate.")