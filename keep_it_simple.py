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
JIRA_TICKET_TEMPLATE = "https://issues.redhat.com/browse/{issue_key}"

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

    if "text" not in message:
        return

    print(f"Got message {message['text']}")

    channel_id = message["channel"]
    keep_it_short(channel_id, client, message)
    enrich_jira_mention(channel_id, client, message)


def keep_it_short(channel_id, client, message):
    message_len = len(message["text"])
    if message["channel_type"] in ["group", "channel"] and "thread_ts" not in message and message_len > CONSTS.MAX_MESSAGE_LEN:
        print("Message is too long, informing user")

        result = client.chat_postMessage(
            channel=channel_id,
            thread_ts=message["ts"],
            text=CONSTS.MAX_MESSAGE_COMMENT.format(max_message_len=CONSTS.MAX_MESSAGE_LEN, message_len=message_len,
                                                   manager=MANAGER)
        )



def enrich_jira_mention(channel_id, client, message):
    print("Checking message for enrichment")
    if not jira_user:
        return

    jira_links = re.findall("<https:\/\/issues\.redhat\.com\/browse\/MGMT-.*?>", message["text"])

    jira_mention = re.findall("(?:^|\s)(?:MGMT|mgmt)-[1-9]{4,}", message["text"])

    print(f"Message jira links: {jira_links+jira_mention}")

    if not jira_links and not jira_mention:
        return

    new_message = message["text"]

    for link in jira_links:
        ticket_key = re.findall("MGMT-.*[1-9]", link)[0]
        ticket_description = get_jira_info(ticket_key)
        link_with_description = f"{link} \n> :jira: {ticket_description}\n"
        new_message = new_message.replace(link, link_with_description)

    for mention in jira_mention:
        try:
            ticket_key = mention.upper().strip()
            ticket_description = get_jira_info(ticket_key)
            link = JIRA_TICKET_TEMPLATE.format(issue_key=ticket_key)
            link_with_description = f"{link} \n> :jira: {ticket_description}\n"
            new_message = new_message.replace(mention, link_with_description)
        except Exception as ex:
            print(ex)
            continue

    client.chat_update(
        text=new_message,
        channel=channel_id,
        ts=message["ts"]
    )

def get_jira_info(ticket_key):
    issue = jira_client.search_issues(f"key={ticket_key}")[0]
    title = issue.raw['fields']['summary']
    return title

if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
