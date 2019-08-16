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
    
    if word == "Osu":
        message = TextSendMessage(text="Yes!")
        WorkSheet.update_cell(1, 1, "Yes!Yes!Yes!")


    if word == "#獲得群組成員ID&資料內容":
        groupid = event.source.group_id
    i = 0
    member_ids_res = line_bot_api.get_group_member_ids(groupid)
    for member_id in member_ids_res:
        WorkSheet.append_row(member_id)
        profile = line_bot_api.get_profile(member_id)
        WorkSheet.update_cell(i, 2, profile.display_name)
        WorkSheet.update_cell(i, 3, profile.picture_url)
        WorkSheet.update_cell(i, 4, profile.status_message)
        i += 1
    message = TextSendMessage("完成資料獲取.")
    line_bot_api.reply_message(event.reply_token, message)


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)