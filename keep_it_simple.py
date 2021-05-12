import os
import re
import CONSTS

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

MANAGER = os.environ.get("MANAGER", "the manager")
MAX_MESSAGE_LEN = os.environ.get("MAX_MESSAGE_LEN", CONSTS.MAX_MESSAGE_LEN)
LINK_PATTERN = re.compile('<.+?\|(.+?)>')
# Check liveness
@app.event("app_mention")
def event_test(say):
    say("Hi there!")

def strip_links(message):
    for match in LINK_PATTERN.finditer(message):
        message = re.sub(LINK_PATTERN, match.groups()[0], message, 1)
    return message

@app.event("message")
def make_it_short(client, message):
    channel_id = message["channel"]
    if message["channel_type"] in ["group", "channel"] and "thread_ts" not in message:
        message_len = len(strip_links(message["text"]))
        if message_len > CONSTS.MAX_MESSAGE_LEN:
            result = client.chat_postMessage(
                channel=channel_id,
                thread_ts=message["ts"],
                text=CONSTS.MAX_MESSAGE_COMMENT.format(max_message_len=CONSTS.MAX_MESSAGE_LEN, message_len=message_len, manager=MANAGER)
            )

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
