from slackeventsapi import SlackEventAdapter
from slack import WebClient, RTMClient
from config import SLACK_SIGNING_SECRET, SLACK_SIGNING_SECRET_TO_ADD_USERS, TOKENB, SLACK_CLIENT_ID, BOT_ID, GET, POST, COLLBACK
import redis
import requests
import threading

import json
from flask import request, make_response, Flask, render_template, redirect

app = Flask(__name__)

slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events")
client = WebClient(TOKENB)

user_id = 'ULJ4829LL'
USER_ORDER = []
USER_INFO = []
r = redis.Redis(host='127.0.0.1', port=6379, db=0)


def post_message():
    user_data_dict = {}
    print("Start postMessage")
    response = requests.get(GET+BOT_ID)
    responseJson = response.json()
    print('Data ==== responseJson (get)', responseJson['data'])
    print(("\n Objective in responseJson =", responseJson['data']['objectives'][0]))
    if len(responseJson['data']) != 0:
        for i in responseJson['data']:
            if i['bot_step_id'] == 1:
                print('bot_step_id === 1,  for data ==== ', i)
                print('\n i["objectives"]', i['objectives', '\n'])
                order_dm = WebClient(i['slack_access_token']).chat_postMessage(
                    as_user=False,
                    channel=i['slack_channel_id'],
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": i['bot_step_title']
                            },
                            "accessory": {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Send focus",
                                    # "emoji": true
                                },
                                "value": "focus"
                            }
                        }
                    ],
                    attachments=''
                )

                print(order_dm)
                obj_list = []
                for j in i["objectives"]:
                    x = {
                        "Id": j["Id"],
                        "Title": j["Title"]
                    }
                    obj_list.append(x)
                user_data_dict = {
                        "bot_uniq_id": BOT_ID,
                        "bot_schedule_id": int(i['bot_schedule_id']),
                        "slack_client_id": i['slack_client_id'],
                        "slack_channel_id": order_dm["channel"],
                        "slack_ts": order_dm["ts"],
                        "focus": '',
                        "slack_access_token": i['slack_access_token'],
                        "bot_step_title": i['bot_step_title'],
                        "bot_next_step_success_title": i['bot_next_step_success_title'],
                        "objectives": obj_list
                }

                print("user_data_dict ===", user_data_dict)
                USER_INFO.append(
                    {
                        "slack_client_id": i['slack_client_id'],
                        "slack_channel_id": order_dm["channel"],
                        "message": order_dm["message"]["text"]
                    }
                )

            elif i['bot_step_id'] == 5 or i['bot_step_id'] == 6:
                if i['bot_step_id'] == 5:
                    response_mess(i, 5)
                elif i['bot_step_id'] == 6:
                    response_mess(i, 6)
            elif i['bot_step_id'] == 4:
                order_dm = WebClient(i['slack_access_token']).chat_update(
                    channel=i["slack_channel_id"],
                    ts=i["slack_ts"],
                    blocks=
                    [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": i['bot_step_title']
                            },
                            "accessory": {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Select Objective",
                                    # "emoji": true
                                },
                                "value": "Objective"
                            }
                        }
                    ],
                    attachments=''
                )
            elif i['bot_step_id'] == 7:
                user_redis = json.loads(r.get("user_" + i['slack_client_id'] + "_" + str(i['bot_schedule_id'])).decode('utf-8'))
                order_dm = WebClient(i['slack_access_token']).chat_delete(
                    channel=i['slack_channel_id'],
                    ts=user_redis['slack_ts']
                )

            if i['bot_step_id'] == 4 or i['bot_step_id'] == 5 or i['bot_step_id'] == 6 or i['bot_step_id'] == 7:
                continue
            else:
                redis_user_key = "user_" + i['slack_client_id'] + "_" + str(i['bot_schedule_id'])
                print("redis_user_key", redis_user_key)
                print("saved to redis ===== ", user_data_dict)
                r.set(redis_user_key, json.dumps(user_data_dict))
    threading.Timer(60, post_message).start()
    print("End of post_message")




def response_mess(i, id_issue):
    print("response_mess i ==", i)
    user_redis = json.loads(r.get("user_" + i['slack_client_id'] + "_" + str(i['bot_schedule_id'])).decode('utf-8'))
    print("user_redis  ====",user_redis)
    order_dm = WebClient(i['slack_access_token']).chat_update(
        channel=i["slack_channel_id"],
        ts=user_redis["slack_ts"],
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": i["bot_step_title"]
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Send focus",
                    },
                    "value": "focus"
                }
            }]
    )


authed_teams = {}

# registrations users
@slack_events_adapter.server.route("/thanks", methods=["GET", "POST"])
def add():
    code_arg = request.args.get('code')
    state = request.args.get('state')
    print(type(state))
    print('State  =', state)
    sub_dom, us_id = state.split('.')
    print('sub_dom =', sub_dom)
    print('us_id =', us_id)
    print('CODE ====', code_arg)
    auth_response = client.oauth_access(
        client_id=SLACK_CLIENT_ID,
        client_secret=SLACK_SIGNING_SECRET_TO_ADD_USERS,
        code=code_arg
    )
    print("\n auth_response =", auth_response, '\n')
    team_id = auth_response["team_id"]
    authed_teams[team_id] = {
        "bot_token": auth_response["bot"]["bot_access_token"]
    }
    tok = auth_response['access_token']
    us = auth_response['user_id']
    client_data = client.users_info(
        token=tok,
        user=us
    )

    send_data ={
        "user": int(us_id),
        "bot_uniq_id": BOT_ID,
        "slack_client_name": client_data['name']['name'],
        "slack_client_id": auth_response['user_id'],
        "slack_access_token": auth_response['access_token'],
        "slack_channel_id": auth_response['incoming_webhook']['channel_id'],
    }
    print('send_data ===', send_data)
    print("\n Client_data =", client_data, '\n')
    print('\n client_data[name]===', client_data['name'])
    send_req = requests.post(COLLBACK, json=send_data)
    print('send_req == =', send_req)
    print('respons===', send_req.content)
    return redirect('https://'+sub_dom+'.'+'dev.unitonomy.com')


# user click button
@slack_events_adapter.server.route("/after_button", methods=["POST", "GET"])
def respond():
    print("Start after_button")
    redis_keys = r.keys()
    print("keys = = =  ", redis_keys)
    for key in redis_keys:
        if "user_" in key.decode("utf-8"):
            USER = json.loads(r.get(key).decode('utf-8'))
            slack_payload = json.loads(request.form.get("payload"))
            print('\n USER ========== ', USER, '\n')
            print('\n slack_payload in start foo=', slack_payload, '\n')
            if slack_payload['type'] == 'block_actions':
                print(" if slack_payload['type'] == 'block_actions':")
                if slack_payload['actions'][0]['value'] == 'focus':
                    print('slack_payload["trigger_id"]= ', slack_payload['trigger_id'])
                    if slack_payload['user']['id'] == USER['slack_client_id']:
                        print("focus if slack_payload['container']['channel_id'] == i['slack_channel_id']:")
                        WebClient(USER['slack_access_token']).dialog_open(
                            type='section',
                            text='Focus',
                            trigger_id=slack_payload['trigger_id'],
                            dialog={
                                "title": "Focus ",
                                "submit_label": "Submit",
                                "callback_id": "focus",
                                "elements": [
                                    {
                                        "label": "Send your focus",
                                        "type": "text",
                                        "name": "meal_preferences",
                                        "placeholder": "",
                                    }
                                ]
                            }
                        )

                elif slack_payload['actions'][0]['value'] == 'Objective':
                    print("elif slack_payload['actions'][0]['value'] == 'Objective':")
                    print("USER SLACK ID=", USER)
                    if slack_payload['user']['id'] == USER['slack_client_id']:
                        print("Objective if slack_payload['container']['channel_id'] == i['slack_channel_id']:")
                        a = []
                        for objective in USER['objectives']:
                            print('objectives===', objective)
                            a.append({
                                "label": objective["Title"],
                                "value": objective["Id"]
                            })
                        print('\n All objective in  USER=====', a +'\n')
                        WebClient(USER['slack_access_token']).dialog_open(
                            trigger_id=slack_payload['trigger_id'],
                            dialog={
                                "title": "Focus ",
                                "submit_label": "Submit",
                                "callback_id": "Objective",
                                "elements": [
                                    {
                                        "label": "Select your Objective",
                                        "type": "select",
                                        "name": "meal_preferences",
                                        "placeholder": "",
                                        "options": a
                                    }
                                ]
                            }
                        )

            elif slack_payload['type'] == 'dialog_submission':
                print("elif slack_payload['type'] == 'dialog_submission':")
                if slack_payload['callback_id'] == 'focus':
                    if slack_payload['user']['id'] == USER['slack_client_id']:
                        print(" if slack_payload['user']['id'] == USER['slack_client_id']:")
                        MESSAGE_SERVER = {
                                "bot_uniq_id": BOT_ID,
                                "completed_bot_step": 1,
                                "bot_schedule_id": int(USER["bot_schedule_id"]),
                                "slack_client_id": USER['slack_client_id'],
                                "slack_channel_id":USER['slack_channel_id'],
                                "slack_ts": USER['slack_ts'],
                                "data": {

                                    "focus_title": slack_payload['submission']['meal_preferences'],
                                    "objective_id": None
                                }
                            }
                        print("MESSAGE_SERVER === ", MESSAGE_SERVER)
                        response_client_data = requests.post(POST, json=MESSAGE_SERVER)
                        print("response_client_data ==== ", response_client_data)
                        client_data_dict = json.loads(response_client_data.text)
                        print("client_data_dict ==== ", client_data_dict)
                        client_data_list = client_data_dict['data']
                        print("client_data_list ==== ", client_data_list)
                        WebClient(USER['slack_access_token']).chat_update(
                            channel=USER["slack_channel_id"],
                            ts=USER["slack_ts"],
                            blocks=
                            [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": USER['bot_next_step_success_title']
                                    },
                                    "accessory": {
                                        "type": "button",
                                        "text": {
                                            "type": "plain_text",
                                            "text": "Select Objective",
                                        },
                                        "value": "Objective"
                                    }
                                }
                            ],
                            attachments=''
                        )

                        if len(client_data_list) != 0:
                            for j in client_data_list:
                                USER["bot_schedule_id"] = str(j["bot_schedule_id"])
                                USER["slack_client_id"] = j["slack_client_id"]
                                USER["slack_channel_id"] = j["slack_channel_id"]
                                USER["slack_ts"] = j["slack_ts"]
                                USER["slack_access_token"] = j["slack_access_token"]
                                USER["bot_step_title"] = str(j["bot_step_title"])
                                USER["bot_next_step_success_title"] = j["bot_next_step_success_title"]
                                USER['focus'] = slack_payload['submission']['meal_preferences']
                                print('slack_payload in oredr= ', slack_payload['submission']['meal_preferences'], '\n')
                                print('\n This i in dialog_submission +  meal_preferences =', USER, '\n')
                                print('USER', USER)
                                redis_user_key = "user_" + USER['slack_client_id'] + "_" + str(USER['bot_schedule_id'])
                                r.set(redis_user_key, json.dumps(USER))
                                print('USER454==', USER)

                elif slack_payload['callback_id'] == 'Objective':
                    print('\n i in Objective =', USER, '\n')
                    if slack_payload['user']['id'] == USER['slack_client_id']:
                        MESSAGE_SERVER = {
                                    "bot_uniq_id": BOT_ID,
                                    "completed_bot_step": 2,
                                    "bot_schedule_id": int(USER["bot_schedule_id"]),
                                    "slack_client_id": USER['slack_client_id'],
                                    "slack_channel_id":USER['slack_channel_id'],
                                    "slack_ts": USER['slack_ts'],
                                    "data": {

                                        "focus_title": USER['focus'],
                                        "objective_id": int(slack_payload['submission']['meal_preferences'])
                                    }
                                }
                        print("MESSAGE_SERVER in end", MESSAGE_SERVER)
                        reply_from_post = requests.post(POST, json=MESSAGE_SERVER)
                        print("reply from post =", reply_from_post.text)
                        this_respons_text = json.loads(reply_from_post.text)
                        print("this_respons_text =", this_respons_text)
                        this_respons_data = this_respons_text['data']
                        print("this_respons_data =", this_respons_data[0])
                        WebClient(USER['slack_access_token']).chat_update(
                            channel=USER['slack_channel_id'],
                            ts=USER['slack_ts'],
                            blocks=[{
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": USER["bot_next_step_success_title"] + " " + "https://dev.unitonomy.com/#/alignment-map"
                                }}],
                            attachments=''
                        )
                        MESSAGE_SERVER = [
                            {
                                    "bot_uniq_id": BOT_ID,
                                    "completed_bot_step": 3,
                                    "bot_schedule_id": USER["bot_schedule_id"],
                                    "slack_channel_id": USER["slack_channel_id"],
                                    "slack_client_id": USER['slack_client_id'],
                                    "slack_ts": USER['slack_ts'],
                                    "data": {
                                        "focus_title": "",
                                        "objective_id": None
                                    }
                                }
                        ]
                        requests.post(POST, json=MESSAGE_SERVER)
            print("End of /after_button \n")
    return make_response("", 200)


if __name__ == "__main__":
    post_message()
    slack_events_adapter.start(port=3000)
