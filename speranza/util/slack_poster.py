import logging
from slackclient import SlackClient

from speranza.util import ERR_LOG

SLACK_TOKEN = 'xoxp-23808070245-23809034931-59911397713-e9163071cb'


def post_alert_to_slack(message):
    slack_client = SlackClient(SLACK_TOKEN)
    slack_post = slack_client.api_call(
        "chat.postMessage",
        channel='#alerts',
        text=message,
        username='error_bot',
        icon_emoji=':sob:'
    )

    if slack_post['ok'] is not True:
        logging.basicConfig(format='%(asctime)s : %(levelname)s - %(message)s', filename=ERR_LOG, level=logging.DEBUG)
        logging.error('SLACK FAILED WITH: ' + slack_post['error'])
