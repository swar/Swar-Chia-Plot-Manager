

from plotmanager.library.parse.configuration import get_notifications_settings
notifications_settings = get_notifications_settings()

#send Discord notification
sendDiscord = notifications_settings.get('notify_discord')
discordWebhook = r'%s' % notifications_settings.get('discord_webhook_url')

#play sound notification completed plots
playSound = notifications_settings.get('play_sound')
song = r'%s' % notifications_settings.get('song')

#send Push noticies to Pushover service
sendPushover = notifications_settings.get('notify_pushover')
pushoverUserKey = r'%s' % notifications_settings.get('pushoverUserKey')
pushoverAPIKey = r'%s' % notifications_settings.get('pushoverAPIKey')

#send Push noticies to Pushover service
sendTwilio = notifications_settings.get('notify_twilio')
twilio_account_sid = r'%s' % notifications_settings.get('twilio_account_sid')
twilio_auth_token = r'%s' % notifications_settings.get('twilio_auth_token')
twilio_from_phone = r'%s' % notifications_settings.get('twilio_from_phone')
twilio_to_phone = r'%s' % notifications_settings.get('twilio_to_phone')

def sendNotifications(msgTxt, msgTitle, discord = True, sound = True, pushover = True, twilio = True):

    if sendDiscord and discord:
        import discord_notify as dn
        notifier = dn.Notifier(discordWebhook)
        notifier.send(msgTxt, print_message=False)

    if playSound and sound:
        from playsound import playsound
        playsound(song)

    if sendPushover and pushover:
        from pushover import init, Client
        client = Client(pushoverUserKey, api_token=pushoverAPIKey)
        client.send_message(msgTxt, title=msgTitle) 


    if sendTwilio and twilio:
        import os
        from twilio.rest import Client

        client = Client(twilio_account_sid, twilio_auth_token)

        message = client.messages.create(body=msgTxt,from_=twilio_from_phone,to=twilio_to_phone)

#print(message.sid)


