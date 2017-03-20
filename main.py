import time
import datetime
from slackclient import SlackClient

token = 'slack-bot-auth-token'
member = ['JohnDoe', 'JaneDoe']
channelId = 'channel-id'
bot = 'bot-id'
releaseMessage = 'I deployed production today'

def in_today(timestamp):
    begin = time.mktime(datetime.datetime.combine(datetime.date.today(), datetime.time.min).timetuple())
    end = time.mktime(datetime.datetime.combine(datetime.date.today(), datetime.time.max).timetuple())

    return begin <= float(timestamp) <= end

def get_next_member(current):
    nextMember = (member.index(current) + 1) % len(member)

    return member[nextMember]

client = SlackClient(token)
lastDeploy = member[0]

if client.rtm_connect():
    while True:
        response = client.rtm_read()
        for event in response:
            print(event)
            if event['type'] == 'message':
                if 'text' in event and '@{}'.format(bot) in event['text']:
                    messages = client.api_call(
                        'groups.history',
                        channel=channelId,
                    )
                    for message in messages['messages']:
                        if releaseMessage in message['text']:
                            userInfo = client.api_call(
                                'users.info',
                                user=message['user'],
                            )
                            userName = userInfo['user']['name']
                            content = 'It\'s <@{}>\'s turn to deploy' . format(member[0])
                            if not in_today(message['ts']):
                                nextDeploy = get_next_member(userName)
                                content = 'It\'s <@{}>\'s turn to deploy' . format(nextDeploy)
                            else:
                                content = '<@{}> already deployed prod' . format(userName)
                            client.api_call(
                                'chat.postMessage',
                                channel=channelId,
                                text=content
                            )
                            # print content
                            break
        time.sleep(0.5)
else:
    print 'Connection Failed, invalid token?'
