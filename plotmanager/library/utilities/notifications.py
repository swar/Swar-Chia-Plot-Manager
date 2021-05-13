def _send_notifications(title, body, settings):
    if settings.get('notify_discord') is True:
        import discord_notify
        notifier = discord_notify.Notifier(settings.get('discord_webhook_url'))
        notifier.send(body, print_message=False)

    if settings.get('notify_sound') is True:
        import playsound
        playsound.playsound(settings.get('song'))

    if settings.get('notify_pushover') is True:
        import pushover
        client = pushover.Client(settings.get('pushover_user_key'), api_token=settings.get('pushover_api_key'))
        client.send_message(body, title=title)


def send_notifications(title, body, settings):
    try:
        _send_notifications(title=title, body=body, settings=settings)
    except:
        pass
