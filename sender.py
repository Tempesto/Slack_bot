from slackeventsapi import SlackEventAdapter
from slack import WebClient, RTMClient
from config import SLACK_SIGNING_SECRET, SLACK_SIGNING_SECRET_TO_ADD_USERS, TOKENB, TOKENP, MINUTE, HOUR, \
    DAY_OF_WEEK, SLACK_CLIENT_ID, BOT_ID, GET, POST
import redis
import requests

from celery import Celery
from celery.schedules import crontab

import json
from flask import request, make_response, Flask, render_template, redirect
import threading

app = Flask(__name__)

cel = Celery('redis_start', broker='redis://localhost:6379//', backend='redis', )
cel.conf.enable_utc = False

slack_events_adapter = SlackEventAdapter(SLACK_SIGNING_SECRET, "/slack/events")
client = WebClient(TOKENB)

user_id = 'ULJ4829LL'
USER_ORDER = []
USER_INFO = []
r = redis.StrictRedis()
# post message for users
# @cel.task



def postMessage_test():
    print("Start postMessage")
    print("GET =", GET)
    print("BOT_ID =", BOT_ID)
  
   
    response = requests.get(GET+BOT_ID)
    responseJson = response.json()

    print('Data ==== ', responseJson['data'])
    if len(responseJson['data']) != 0:
        for i in responseJson['data']:
            if i['bot_step_id'] == 1:
                print('i=', i)
                print('channel', i['slack_channel_id'])
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
                assert order_dm["ok"]
                print('Assert : ok')
                print(order_dm)
                USER_ORDER.append(
                    {
                        "bot_uniq_id": 'UMQCJQ41Y',
                        # "completed_bot_step": None,
                        "bot_schedule_id": i['bot_schedule_id'],
                        "slack_client_id": i['slack_client_id'],
                        "slack_channel_id": order_dm["channel"],
                        "slack_ts": order_dm["ts"],
                        # "message": order_dm["message"]["text"],
                        # "ts": order_dm["ts"],
                        "focus": '',
                        "slack_access_token": i['slack_access_token'],
                        "bot_step_title": i['bot_step_title'],
                        "bot_next_step_success_title": i['bot_next_step_success_title'],
                        "objectives": i["objectives"]
                    })
                USER_INFO.append(
                    {
                        "slack_client_id": i['slack_client_id'],
                        "slack_channel_id": order_dm["channel"],
                        "message": order_dm["message"]["text"]
                    }
                )
                MESSAGE_SERVER= [
                        {
                            "bot_uniq_id":'UMQCJQ41Y',
                            "completed_bot_step": None,
                            "bot_schedule_id": i["bot_schedule_id"],
                            "slack_client_id": i['slack_client_id'],
                            "slack_ts": order_dm["ts"],
                            "data": {

                                "focus_title": "",
                                "objective_id": None
                            }
                        }
                    ]
                requests.post(POST, data=json.dumps(MESSAGE_SERVER))


            # elif i['bot_step_id'] == 2:
            #     print('i=', i)
            #     print('channel', i['slack_channel_id'])
            #     USER_ORDER.append(
            #         {
            #             "bot_uniq_id": 'UMQCJQ41Y',
            #             "completed_bot_step": 'None',
            #             "bot_schedule_id": i['bot_schedule_id'],
            #             "slack_client_id": i['slack_client_id'],
            #             "slack_channel_id": i['slack_channel_id'],
            #             "slack_ts": i['slack_ts'],
            #             # "ts": i['slack_ts'],
            #             "focus": '',
            #             "slack_access_token": i['slack_access_token'],
            #             "bot_step_title": i['bot_step_title'],
            #             "bot_next_step_success_title": i['bot_next_step_success_title'],
            #             "objectives": i["objectives"]
            #         })
            #     USER_INFO.append(
            #         {
            #             "slack_client_id": i['slack_client_id'],
            #             "slack_channel_id": i["slack_channel_id"],
            #             "message": i['bot_step_title']
            #         }
            #     )
            #     # MESSAGE_SERVER= [
            #     #         {
            #     #             "bot_uniq_id":'UMQCJQ41Y',
            #     #             "completed_bot_step": 1,
            #     #             "bot_schedule_id": i["bot_schedule_id"],
            #     #             "response": true,
            #     #             "slack_client_id": i['slack_client_id'],
            #     #             "slack_ts": order_dm["ts"],
            #     #             "data": {
            #     #
            #     #                 "focus_title": "",
            #     #                 "objective_id": null
            #     #             }
            #     #         }
            #     #     ]

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
                MESSAGE_SERVER = [
                    {
                        "bot_uniq_id":'UMQCJQ41Y',
                        "completed_bot_step": 4,
                        "bot_schedule_id": i["bot_schedule_id"],
                        "slack_client_id": i['slack_client_id'],
                        "slack_channel_id":i["slack_channel_id"],
                        "slack_ts": i['slack_ts'],
                        "data": {

                            "focus_title": "",
                            "objective_id": None
                        }
                    }
                ]
                requests.post(POST, data = json.dumps(MESSAGE_SERVER))
                USER_ORDER.append(
                    {
                        "bot_uniq_id": 'UMQCJQ41Y',
                        "completed_bot_step": 'None',
                        "bot_schedule_id": i['bot_schedule_id'],
                        "slack_client_id": i['slack_client_id'],
                        "slack_channel_id": order_dm["channel"],
                        "slack_ts": order_dm["ts"],
                        # "message": order_dm["message"]["text"],
                        # "ts": order_dm["ts"],
                        "focus": '',
                        "slack_access_token": i['slack_access_token'],
                        "bot_step_title": i['bot_step_title'],
                        "bot_next_step_success_title": i['bot_next_step_success_title'],
                        "objectives": i["objectives"]
                    })
                USER_INFO.append(
                    {
                        "slack_client_id": i['slack_client_id'],
                        "slack_channel_id": order_dm["channel"],
                        "message": order_dm["message"]["text"],
                        "completed_bot_step": 4,
                        "response": order_dm['ok'],
                    }
                )
            elif i['bot_step_id'] == 7:
                order_dm = WebClient(i['slack_access_token']).chat_delete(
                    channel=i['slack_channel_id'],
                    ts=i['slack_ts']
                )


                # print('USER_ORDER in step 4 ====', USER_ORDER)
        # print('USER_ORDER  = == = = ', USER_ORDER)

    r.set('USER_ORDER', json.dumps(USER_ORDER))
    r.set('USER_INFO', json.dumps(USER_INFO))


def response_mess(i, id_issue):
    print("response_mess i ==", i)
    order_dm = WebClient(i['slack_access_token']).chat_update(
        channel=i["slack_channel_id"],
        ts=i["slack_ts"],
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
                        # "emoji": true
                    },
                    "value": "focus"
                }
            }]
    )
    MESSAGE_SERVER = [
        {
            "bot_uniq_id":'UMQCJQ41Y',
            "completed_bot_step": id_issue,
            "bot_schedule_id": i["bot_schedule_id"],
            "slack_client_id": i['slack_client_id'],
            "slack_channel_id":i["slack_channel_id"],
            "slack_ts": i['slack_ts'],
            "data": {

                "focus_title": "",
                "objective_id": null
            }
        }
    ]
    requests.post(POST, data=json.dumps(MESSAGE_SERVER))
    USER_ORDER.append(
        {
            "bot_uniq_id": 'UMQCJQ41Y',
            "completed_bot_step": None,
            "bot_schedule_id": i['bot_schedule_id'],
            "bot_step_id": i["bot_step_id"],
            "slack_client_id": i['slack_client_id'],
            "slack_channel_id": order_dm["channel"],
            "slack_ts": order_dm["ts"],
            "message": order_dm["message"]["text"],
            "ts": order_dm["ts"],
            "focus": '',
            "slack_access_token": i['slack_access_token'],
            "bot_step_title": i['bot_step_title'],
            "bot_next_step_success_title": i['bot_next_step_success_title'],
            "objectives": i["objectives"]
        })
    USER_INFO.append(
        {
            "slack_client_id": i['slack_client_id'],
            "slack_channel_id": i["slack_channel_id"],

            "completed_bot_step": id_issue,
            "response": order_dm['ok'],
        }
    )
    r.set('USER_ORDER', json.dumps(USER_ORDER))
    r.set('USER_INFO', json.dumps(USER_INFO))


# Configurate send message
# cel.conf.beat_schedule = {
#     'send massage user': {
#         'task': 'sender.postMessage',
#         'schedule': crontab(day_of_week=DAY_OF_WEEK, hour=HOUR, minute=MINUTE),
#     },
# }


# @slack_events_adapter.on("message")
# def hendel_message(event_data):
#     print("Event = ", event_data, '\n')
#     message = event_data["event"]
#     print("message === ", message, '\n')
#     print('message channel =', message['channel'])
#     # client.users_info(
#     #     user='ULMA7FEMR'
#     # )
#     a = WebClient('xoxp-739261532001-747828510118-750197367735-f1e51021592f76995afaccd61adcd29b').users_identity(
#
#     )
#     print("a=", a)
#
#     text_user = message['text']
#     if message.get("subtype") is None and "focus" in text_user:
#         channel = message["channel"]
#         # send_message = "YA"
#         response = client.chat_postMessage(
#             channel=channel,
#             text='Hi',
#             attachments= ''
#         )
#         print(response)
#         assert response["ok"]
#
authed_teams = {}


# registrations users
@slack_events_adapter.server.route("/thanks", methods=["GET", "POST"])
def add():
    code_arg = request.args.get('code')
    us_id = request.args.get('state')

    print('User id =', us_id)
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
    # RTMClient(authed_teams[team_id]["bot_token"])
    tok = auth_response['access_token']
    us = auth_response['user_id']
    client_data = client.users_info(
        token=tok,
        user=us
    )

    send_data ={
        "user": us_id,
        "slack_client_name": client_data['name'],
        "slack_client_id": auth_response['user_id'],
        "slack_access_token": auth_response['access_token'],
        "slack_channel_id": auth_response['incoming_webhook']['channel_id'],
    }
    payload = {'json_payload': send_data}
    print('send_data ===', send_data)
    print("\n Client_data =", client_data, '\n')
    send_req = requests.post(POST, json==payload)
    print('send_req == =', send_req)
    print('respons===', send_req.content)
    return redirect('http://dev.unitonomy.com')


# user click button
@slack_events_adapter.server.route("/after_button", methods=["POST", "GET"])
def respond():
    USER_ORDER = json.loads(r.get('USER_ORDER').decode('utf-8'))
    slack_payload = json.loads(request.form.get("payload"))
    print('\n USER_ORDER in start foo= ', USER_ORDER, '\n')
    print('\n slack_payload in start foo=', slack_payload, '\n')
    for i in USER_ORDER:
        print("\n i in for=", i, '\n')
        if slack_payload['type'] == 'block_actions':
            if slack_payload['actions'][0]['value'] == 'focus':
                print('slack_payload["trigger_id"]= ', slack_payload['trigger_id'])
                if slack_payload['container']['channel_id'] == i['slack_channel_id']:
                    WebClient(i['slack_access_token']).dialog_open(
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
                # print('slack_payload slack_ts =', slack_payload['container']["slack_ts"])
                if slack_payload['container']['channel_id'] == i['slack_channel_id']:
                    # sql = f"SELECT parent_id, company_id, item_type, description FROM items where company_id={i[1]['company_id']} and title='objective'"
                    # data = sql_query(sql)
                    # print('\n data in Objective =', data)
                    a = []
                    for objectives in i['objectives']:
                        print('objectives===', objectives)
                        a.append({
                            "label": objectives["Title"],
                            "value": objectives["Id"]
                        })
                    WebClient(i['slack_access_token']).dialog_open(
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
                                    # "options":
                                    #     [
                                    #     {
                                    #         "label": "Cappuccino",
                                    #         "value": "1"
                                    #     },
                                    #     {
                                    #         "label": "Latte",
                                    #         "value": "2"
                                    #     },
                                    #     {
                                    #         "label": "Pour Over",
                                    #         "value": "3"
                                    #     },
                                    #     {
                                    #         "label": "Cold Brew",
                                    #         "value": "4"
                                    #     }
                                    # ]
                                }
                            ]
                        }
                    )


        elif slack_payload['type'] == 'dialog_submission':
            if slack_payload['callback_id'] == 'focus':
                if slack_payload['channel']['id'] == i['slack_channel_id']:
                    MESSAGE_SERVER = [
                        {
                            "bot_uniq_id":'UMQCJQ41Y',
                            "completed_bot_step": 1,
                            "bot_schedule_id": i["bot_schedule_id"],
                            "slack_client_id": i['slack_client_id'],
                            "slack_channel_id":i['slack_channel_id'],
                            "slack_ts": i['slack_ts'],
                            "data": {

                                "focus_title": slack_payload['submission']['meal_preferences'],
                                "objective_id": null
                            }
                        }
                    ]
                    requests.post(POST, data=json.dumps(MESSAGE_SERVER))
                    WebClient(i['slack_access_token']).chat_update(
                        channel=i["slack_channel_id"],
                        ts=i["slack_ts"],
                        blocks=
                        [
                            {
                                "type": "section",
                                "text": {
                                    "type": "mrkdwn",
                                    "text": i['bot_next_step_success_title']
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
                    #сюда вставить запрос на сервер
                    client_data = requests.get(GET+BOT_ID)
                    data = json(client_data)
                    print("DATA SERVER ++++", data)
                    # if data['slack_channel_id'] == i['slack_channel_id']:
                    # i["bot_uniq_id"] = data["bot_uniq_id"]
                    # i["completed_bot_step"] = data["completed_bot_step"]
                    i["bot_schedule_id"] = data["bot_schedule_id"]
                    i["slack_client_id"] = data["slack_client_id"]
                    i["slack_channel_id"] = data["slack_channel_id"]
                    i["slack_ts"] = data["slack_ts"]
                    i["slack_access_token"] = data["slack_access_token"]
                    i["bot_step_title"] = data["bot_step_title"]
                    i["bot_next_step_success_title"] = data["bot_next_step_success_title"]
                    i["objectives"] = data["objectives"]

                    print('\n This i in dialog_submission =', i, '\n')
                    i['focus'] = slack_payload['submission']['meal_preferences']
                    print('slack_payload in oredr= ', slack_payload['submission']['meal_preferences'], '\n')
                    print('\n This i in dialog_submission +  meal_preferences =', i, '\n')
                    # USER_ORDER[i]['focus':slack_payload['submission']['meal_preferences']]
                    print('USER_ORDER All + i[focus]= ', USER_ORDER)
                    r.set("USER_ORDER", json.dumps(USER_ORDER))
                    USER_INFO.append(
                        {
                            "slack_client_id": i['slack_client_id'],
                            "slack_channel_id": i["slack_channel_id"],
                            "completed_bot_step": 2,
                            "text": i['bot_next_step_success_title']
                        }
                    )
                    r.set('USER_INFO', json.dumps(USER_INFO))
                    # timer3.start()
                    # print("timer3 start \n")

            elif slack_payload['callback_id'] == 'Objective':
                print('\n i in Objective =', i, '\n')
                if slack_payload['channel']['id'] == i['slack_channel_id']:
                    MESSAGE_SERVER = [
                        {
                                "bot_uniq_id":'UMQCJQ41Y',
                                "completed_bot_step": 2,
                                "bot_schedule_id": i["bot_schedule_id"],
                                "slack_client_id": i['slack_client_id'],
                                "slack_channel_id":i['slack_channel_id'],
                                "slack_ts": i['slack_ts'],
                                "data": {

                                    "focus_title": i['focus'],
                                    "objective_id": slack_payload['submission']['meal_preferences']
                                }
                            }
                    ]
                    requests.post(POST, data=json.dumps(MESSAGE_SERVER))

                    WebClient(i['slack_access_token']).chat_update(
                        channel=i['slack_channel_id'],
                        ts=i['slack_ts'],
                        blocks=[{
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": i["bot_next_step_success_title"]
                            }}],
                        attachments=''
                    )
                    MESSAGE_SERVER = [
                        {
                                "bot_uniq_id":'UMQCJQ41Y',
                                "completed_bot_step": 3,
                                "bot_schedule_id": i["bot_schedule_id"],
                                "slack_channel_id": i["slack_channel_id"],
                                "slack_client_id": i['slack_client_id'],
                                "slack_ts": i['slack_ts'],
                                "data": {

                                    "focus_title": "",
                                    "objective_id": None
                                }
                            }
                    ]
                    requests.post(POST, data=json.dumps(MESSAGE_SERVER))
                    # maks_data = [{"user_id": i[0], "company_id": i[1]['company_id'], "focus": i[1]['focus'], 'Objective': slack_payload['submission']['meal_preferences']}]
                    # r.set('Maks', json.dumps(maks_data))
                    # print(r.get('Maks'))
                    # USER_INFO.append(
                    #     {
                    #         "slack_client_id": i['slack_client_id'],
                    #         "slack_channel_id": i["slack_channel_id"],
                    #         "completed_bot_step": 3,
                    #         "text":
                    #     }
                    # )
                    # r.set('USER_INFO', json.dumps(USER_INFO))

    print("End of /after_button \n")
    return make_response("", 200)


if __name__ == "__main__":
    postMessage_test()
    slack_events_adapter.start(port=3000)
