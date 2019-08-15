from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from engine import WeatherForecast

app = Flask(__name__)

line_bot_api = LineBotApi('SAdvc68i+4s9PMT7rGO3yYXod3Z0FX3umAAtYZf2EsszDq9wliFPdkYNweJqNyzu4pOwCOVKFW0NkESl092sqOty7PlhYJA7DeQ65FkaTM47oMt3KC/EJ2o3ynALkym8iQuvVPnBXmtstW6TAQZGXQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b870f02c816b775a2dd5013c84cac78d')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=event.message.text))
    word = event.message.text
    if word == "你好":
        message = TextSendMessgae(text="Hello#你好")
    else:
        message = TextSendMessage(text="抱歉我不了解#")
    if word == "幹":
        message = TextSendMessage(text="派欸")
    if word == "AMD":
        message = TextSendMessage(text="Yes!")
    # if word == "天氣":
    #     WeatherForeCast.ForeCast()
    line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    app.run()