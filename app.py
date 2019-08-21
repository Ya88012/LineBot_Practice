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

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
global players_amount
players_amount = 0

line_bot_api = LineBotApi('SAdvc68i+4s9PMT7rGO3yYXod3Z0FX3umAAtYZf2EsszDq9wliFPdkYNweJqNyzu4pOwCOVKFW0NkESl092sqOty7PlhYJA7DeQ65FkaTM47oMt3KC/EJ2o3ynALkym8iQuvVPnBXmtstW6TAQZGXQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b870f02c816b775a2dd5013c84cac78d')
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("MyLineBotDataBaseSheetKey.json", scope)
client = gspread.authorize(creds)
SpreadSheet = client.open("MyLineBotData")
WorkSheet_Index = SpreadSheet.worksheet("Index")
WorkSheet_Game = SpreadSheet.worksheet("Game")


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
        message = TextSendMessage(text="Hello~~~")

    if word == "#天黑請閉眼":
        WorkSheet_Game.clear()
        message = TextSendMessage(text="已創立新遊戲~~~")

    if word == "#準備完成":
        global players_amount
        Temp = []
        Temp.append(str(event.source.user_id))
        profile = line_bot_api.get_profile(event.source.user_id)
        player_name = profile.display_name
        Temp.append(player_name)       
        WorkSheet_Game.append_row(Temp)
        message = TextSendMessage(text="玩家 {} 已登入遊戲~~~".format(player_name))
        players_amount += 1

    if word == "#遊戲開始":
        message = [{"type":"text", "text"="GameStart~~~"}, {"type":"text", "text":"本次遊戲共 {} 人遊玩".format(players_amount)}]
        speciallist = random.sample(range(1, players_amount+1), 4)

        for i in range(1, players_amount+1):
            WorkSheet_Game.update_cell(i, 3, "Innocent")
        for j in range(0, 3):
            WorkSheet_Game.update_cell(speciallist[j], 3, "Murderer")
        for k in range(2, 5):
            WorkSheet_Game.update_cell(speciallist[k], 3, "Detective")

    if word == "#開發用_測試回覆":
        line_bot_api.multicast(WorkSheet_Game.col_values(1), TextSendMessage(text="本次遊戲你的身分為 {}".format(WorkSheet_Game.cell.value)))
        message = TextSendMessage(text="OuO")

    line_bot_api.reply_message(event.reply_token, message)


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)