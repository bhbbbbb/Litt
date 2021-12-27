import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ButtonsTemplate, TemplateSendMessage
from linebot.models.send_messages import QuickReply, SendMessage



channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

class QUICK_REPLY_OPTIONS:
    NEXT = {
        "type": "action",
        "action": {
            "type": "message",
            "label": "next",
            "text": "next",
        }
    }
    PREV = {
        "type": "action",
        "action": {
            "type": "message",
            "label": "prev",
            "text": "prev",
        }
    }
    BACK = {
        "type": "action",
        "action": {
            "type": "message",
            "label": "back",
            "text": "back",
        }
    }
    HOME = {
        "type": "action",
        "action": {
            "type": "message",
            "label": "home",
            "text": "home",
        }
    }
    HOT = {
        "type": "action",
        "action": {
            "type": "message",
            "label": "hot",
            "text": "hot",
        }
    }

def send_text_message(reply_token, text, quick_reply=None):
    line_bot_api = LineBotApi(channel_access_token)
    
    if quick_reply: quick_reply = QuickReply(quick_reply)
    line_bot_api.reply_message(reply_token,
        TextSendMessage(text=text, quick_reply=quick_reply))
    return "OK"


"""
def send_button_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TemplateSendMessage(alt_text="buttons", template=BUTTONS))
    return "OK"
def send_image_url(id, img_url):
    pass

"""
