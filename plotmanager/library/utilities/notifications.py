import discord_notify
import playsound
import pushover
import requests


def _send_notifications(title, body, settings):
    if settings.get('notify_discord') is True:
        notifier = discord_notify.Notifier(settings.get('discord_webhook_url'))
        notifier.send(body, print_message=False)

    if settings.get('notify_sound') is True:
        playsound.playsound(settings.get('song'))

    if settings.get('notify_pushover') is True:
        client = pushover.Client(settings.get('pushover_user_key'), api_token=settings.get('pushover_api_key'))
        client.send_message(body, title=title)

    if settings.get('ifttt_webhook') is True:
        requests.post(settings.get('ifttt_webhook_url'), data={'value1': title, 'value2': body})

def send_notifications(title, body, settings):
    try:
        _send_notifications(title=title, body=body, settings=settings)
    except:
        pass
