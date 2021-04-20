

from plotmanager.library.parse.configuration import get_notifications_settings


notifications_settings = get_notifications_settings()
#send Discord notification
sendDiscord = notifications_settings.get('notify_discord')
discordWebhook = r'%s' % notifications_settings.get('discord_webhook_url')

#play sound notification completed plots
playSound = notifications_settings.get('notify_sound')
song = r'%s' % notifications_settings.get('song')

#send Push noticies to Pushover service
sendPushover = notifications_settings.get('notify_pushover')
pushover_user_key = r'%s' % notifications_settings.get('pushover_user_key')
pushover_api_key = r'%s' % notifications_settings.get('pushover_api_key')


def sendNotifications(msgTxt, msgTitle):

    if sendDiscord == True:
        import discord_notify as dn
        notifier = dn.Notifier(discordWebhook)
        notifier.send(msgTxt, print_message=False)

    if playSound == True:
        from playsound import playsound  # pip install playsound
        playsound(song)

    if sendPushover == True:
        from pushover import init, Client
        client = Client(pushover_user_key, api_token=pushover_api_key)
        client.send_message(msgTxt, title=msgTitle)  # pip install python-pushover





