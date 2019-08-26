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

global players_amount
players_amount = 0

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import time

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
        WorkSheet_Game.update_cell(100, 20, event.source.group_id)

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
        global players_amount
        if players_amount == 8:
            message = [TextMessage(text="GameStart~~~"), TextMessage(text="本次遊戲共 {} 人遊玩".format(players_amount))]
            speciallist = random.sample(range(1, players_amount+1), 4)
            Murdereridlist = []
            Detectiveidlist = []
            Innocentidlist = []

            for i in range(1, players_amount+1):
                WorkSheet_Game.update_cell(i, 3, "Innocent")
                WorkSheet_Game.update_cell(i, 4, "Alive")
                WorkSheet_Game.update_cell(i, 5, "0")
                Innocentidlist.append(WorkSheet_Game.cell(i, 1).value)
            for j in speciallist[0:2]:
                WorkSheet_Game.update_cell(j, 3, "Murderer")
                Tempkiller = WorkSheet_Game.cell(j, 1).value
                Murdereridlist.append(Tempkiller)
                Innocentidlist.remove(Tempkiller)
            for k in speciallist[2:4]:
                WorkSheet_Game.update_cell(k, 3, "Detective")
                TempDetective = WorkSheet_Game.cell(k, 1).value
                Detectiveidlist.append(TempDetective)
                Innocentidlist.remove(TempDetective)

            # line_bot_api.multicast(Murdereridlist, [TextMessge(text="此次遊戲你的身分為『殺手』"), TextMessage(text="當個機掰人背刺所有人吧！")])
            # line_bot_api.multicast(Detectiveidlist, [TextMessge(text="此次遊戲你的身分為『偵探』"), TextMessage(text="生死就掌握在你的第六感了！")])
            # line_bot_api.multicast(Innocentidlist, [TextMessge(text="此次遊戲你的身分為『平民』"), TextMessage(text="這場就乖乖混分吧~")])
            
            print(Innocentidlist)
            print(Murdereridlist)
            print(Detectiveidlist)

        elif players_amount < 8:
            message = TextSendMessage(text="人數過少，無法進入遊戲~")
        else:
            message = TextSendMessage(text="人數過多，無法進入遊戲~")

        WorkSheet_Game.update_cell(100, 18, "Night")
        GameStatus = WorkSheet_Game.cell(100, 18).value
        line_bot_api.reply_message(event.reply_token, message)
        NightTimeVote(GameStatus)
    
    def NightTimeVote(GameStatus):
        @handler.add(MessageEvent, message=TextMessage)
        def handle_message(event):
            word = event.message.text
            if GameStaus != "Night":
                message = TextSendMessage(text="現在並不是晚上#")
            else:
                for i in range(1, players_amount+1):
                    if word == "#"+str(i):
                        checklist = WorkSheet_Game.col_values(3)
                        murderersnum = checklist.count("Murderer")
                        cell = WorkSheet_Game.find(event.source.user_id)
                        IdentityConfirm = WorkSheet_Game.cell(int(cell.row), 3).value
                        if IdentityConfirm == "Murderer":
                            Temp = int(WorkSheet_Game.cell(i, 5).value) + 1
                            WorkSheet_Game.update_cell(i, 5, str(Temp))
                            message.append(TextMessage(text="{} 已投票給 {} 號~").format(WorkSheet_Game.cell(int(cell.row), 2).value, i))
                            if int(WorkSheet_Game.cell(i, 5).value) >= murderersnum:
                                WorkSheet_Game.update_cell(i, 4, "Dead")
                                message.append(TextMessage(text="你們成功殺死了 {} 號").format(i))
                else:
                    message = TextSendMessage(text="指令操作錯誤")
        line_bot_api.reply_message(event.reply_token, message)

    if word == "#開發用_找不到ID.":
        cell = WorkSheet_Game.find("ABCDE")
        print(cell)

    line_bot_api.reply_message(event.reply_token, message)


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)