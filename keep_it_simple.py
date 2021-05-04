import os
import re
import jira
import CONSTS

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

MANAGER = os.environ.get("MANAGER", "the manager")
MAX_MESSAGE_LEN = os.environ.get("MAX_MESSAGE_LEN", CONSTS.MAX_MESSAGE_LEN)

JIRA_SERVER = "https://issues.redhat.com"
jira_creds = os.environ.get("JIRA_CREDS", None)
if jira_creds:
    jira_user, jira_pass = jira_creds.split(":")
    jira_client = jira.JIRA(JIRA_SERVER, basic_auth=(jira_user, jira_pass))
else:
    jira_user = None


# Check liveness
@app.event("app_mention")
def event_test(say):
    say("Hi there!")

@app.event("message")
def make_it_short(client, message):
    channel_id = message["channel"]
    keep_it_short(channel_id, client, message)
    enrich_jira_mention(channel_id, client, message)


def keep_it_short(channel_id, client, message):
    if message["channel_type"] in ["group", "channel"] and "thread_ts" not in message and len(
            message["text"]) > CONSTS.MAX_MESSAGE_LEN:
        message_len = len(message["text"])
        result = client.chat_postMessage(
            channel=channel_id,
            thread_ts=message["ts"],
            text=CONSTS.MAX_MESSAGE_COMMENT.format(max_message_len=CONSTS.MAX_MESSAGE_LEN, message_len=message_len,
                                                   manager=MANAGER)
        )


def enrich_jira_mention(channel_id, client, message):
    if not jira_user:
        return
    jira_links = re.findall("<https:\/\/issues\.redhat\.com\/browse\/MGMT-.*?>", message["text"])
    if not jira_links:
        return
    new_message = message["text"]
    for link in jira_links:
        ticket_description = get_jira_info(link)
        link_with_description = f"{link} \n> :jira: {ticket_description}\n"
        new_message = new_message.replace(link, link_with_description)
    client.chat_update(
        text=new_message,
        channel=channel_id,
        ts=message["ts"]
    )

def get_jira_info(ticket):
    ticket_key = re.findall("MGMT-.*[1-9]",ticket)[0]
    issue = jira_client.search_issues(f"key={ticket_key}")[0]
    title = issue.raw['fields']['summary']
    return title

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
