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
import gspread
from oauth2client.service_account import ServiceAccountCredentials


line_bot_api = LineBotApi('SAdvc68i+4s9PMT7rGO3yYXod3Z0FX3umAAtYZf2EsszDq9wliFPdkYNweJqNyzu4pOwCOVKFW0NkESl092sqOty7PlhYJA7DeQ65FkaTM47oMt3KC/EJ2o3ynALkym8iQuvVPnBXmtstW6TAQZGXQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b870f02c816b775a2dd5013c84cac78d')
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("MyLineBotDataBaseSheetKey.json", scope)
client = gspread.authorize(creds)
SpreadSheet = client.open("MyLineBotData")
WorkSheet = SpreadSheet.worksheet("AA")


app = Flask(__name__)

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
        message = TextSendMessage(text="Hello#你好")
    else:
        message = TextSendMessage(text="抱歉我不了解#")
    if word == "Osu":
        message = TextSendMessage(text="Yes!")
        WorkSheet.update_cell(1, 1, "Yes!Yes!Yes!")
    if word == "天氣":
        @handler.add(MessageEvent, message=LocationMessage)
        def handle_message(event):
            lon = float(event.message.longitude)
            lat = float(event.message.latitude)
            result = WeatherForecast.ForeCast(lat, lon)
            message = TextSendMessage(text=result)
    line_bot_api.reply_message(event.reply_token, message)


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)