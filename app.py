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
import time
import re

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
        line_bot_api.reply_message(event.reply_token, message)

    elif word == "#天黑請閉眼":
        WorkSheet_Game.clear()
        message = TextSendMessage(text="已創立新遊戲~~~")
        WorkSheet_Game.update_cell(1, 1, event.source.group_id)
        WorkSheet_Game.update_cell(1, 2, "0")
        line_bot_api.reply_message(event.reply_token, message)

    elif word == "#準備完成":
        Temp = []
        Temp.append(str(event.source.user_id))
        profile = line_bot_api.get_profile(event.source.user_id)
        player_name = profile.display_name
        Temp.append(player_name)       
        WorkSheet_Game.append_row(Temp)
        message = TextSendMessage(text="玩家 {} 已登入遊戲~~~".format(player_name))
        players_amount = int(WorkSheet_Game.cell(1, 2).value)
        players_amount += 1
        WorkSheet_Game.update_cell(1, 2, str(players_amount))
        line_bot_api.reply_message(event.reply_token, message)

    elif word == "#遊戲開始":
        players_amount = int(WorkSheet_Game.cell(1, 2).value)
        if players_amount == 8:
            message = [TextMessage(text="GameStart~~~"), TextMessage(text="本次遊戲共 {} 人遊玩".format(players_amount))]
            speciallist = random.sample(range(2, players_amount+2), 4)
            Murdereridlist = []
            Detectiveidlist = []
            Innocentidlist = []
            Murderernumlist = []
            Detectivenumlist = []

            cell_list = WorkSheet_Game.range("C2:C9")
            for cell in cell_list:
                cell.value = "Innocent"
            WorkSheet_Game.update_cells(cell_list)
            cell_list = WorkSheet_Game.range("D2:D9")
            for cell in cell_list:
                cell.value = "Alive"
            WorkSheet_Game.update_cells(cell_list)
            cell_list = WorkSheet_Game.range("E2:E9")
            for cell in cell_list:
                cell.value = "0"
            WorkSheet_Game.update_cells(cell_list)

            for i in range(2, players_amount+2):
                Innocentidlist.append(WorkSheet_Game.cell(i, 1).value)
            for j in speciallist[0:2]:
                WorkSheet_Game.update_cell(j, 3, "Murderer")
                Tempkiller = WorkSheet_Game.cell(j, 1).value
                Murderernumlist.append(j-1)
                Murdereridlist.append(Tempkiller)
                Innocentidlist.remove(Tempkiller)
            for k in speciallist[2:4]:
                # WorkSheet_Game.update_cell(k, 3, "Detective")
                # TempDetective = WorkSheet_Game.cell(k, 1).value
                # Detectivenumlist.append(k-1)
                # Detectiveidlist.append(TempDetective)
                # Innocentidlist.remove(TempDetective)
                Detectiveidlist = ["U5c8e120e0b051e6998f4966d74d79a75", "A1"]
                Detectivenumlist = [1, 2]

            WorkSheet_Game.insert_row(Murdereridlist, 21)
            WorkSheet_Game.insert_row(Detectiveidlist, 22)

            # line_bot_api.multicast(Murdereridlist, [TextMessage(text="殺手一方：{} {}".format(WorkSheet_Game.cell(speciallist[0], 2).value, WorkSheet_Game.cell(speciallist[1], 2).value)), TextMessge(text="此次遊戲你們的身分為『殺手』"), TextMessage(text="當個機掰人背刺所有人吧！")])
            # line_bot_api.multicast(Detectiveidlist, [TextMessage(text="偵探一方：{} {}".format(WorkSheet_Game.cell(speciallist[2], 2).value, WorkSheet_Game.cell(speciallist[3], 2).value)), TextMessge(text="此次遊戲你的身分為『偵探』"), TextMessage(text="生死就掌握在你的第六感了！")])
            # line_bot_api.multicast(Innocentidlist, [TextMessge(text="此次遊戲你的身分為『平民』"), TextMessage(text="這場就乖乖混分吧~")])

        elif players_amount < 8:
            message = TextSendMessage(text="人數過少，無法進入遊戲~")
        else:
            message = TextSendMessage(text="人數過多，無法進入遊戲~")

        NightKillerVote = []
        NightDetectiveVote = []
        WorkSheet_Game.update_cell(1, 3, "Night")
        GameStatus = WorkSheet_Game.cell(1, 3).value
        print(GameStatus)
        line_bot_api.reply_message(event.reply_token, message)
        line_bot_api.push_message(WorkSheet_Game.cell(1, 1).value, [TextMessage(text="現在是第1天晚上~~~"), TextMessage(text="該做事的別睡了哦~~~")])
        
        print(Murdereridlist)
        print(Detectiveidlist)

        for i in range(90):
            time.sleep(1)
            print(i+1)
        for i in Murderernumlist:
            if WorkSheet_Game.cell(i+1, 4).value != "Alive":
                Murderernumlist.remove(i)
                Murdereridlist.remove(WorkSheet_Game.cell(i+1, 1).value)
        for j in Murderernumlist:
            NightKillerVote.append(int(WorkSheet_Game.cell(j+1, 5).value))
        for k in NightKillerVote:
            Temp = NightKillerVote.count(k)
            print(Temp)
            if Temp > len(NightKillerVote)/2:
                WorkSheet_Game.update_cell(k+1, 4, "Dead")
                # message = TextSendMessage(text="你們成功殺死了 {} 號".format(k))
                print("你們成功殺死了 {} 號".format(k))
                break
            else:
                # message = TextSendMessage(text="本回合無任何死者~~~傻眼#")
                k = "無死者"
                print("本回合無任何死者~~~傻眼#")
        # line_bot_api.multicast(Murdereridlist, message)
        for i in Detectivenumlist:
            if WorkSheet_Game.cell(i+1, 4).value != "Alive":
                Detectivenumlist.remove(i)
                Detectiveidlist.remove(WorkSheet_Game.cell(i+1, 1).value)
        for j in Detectivenumlist:
            NightDetectiveVote.append(int(WorkSheet_Game.cell(j+1, 5).value))
        for k in NightDetectiveVote:
            Temp = NightDetectiveVote.count(k)
            print(Temp)
            if Temp > len(NightDetectiveVote)/2:
                Surveyresult = WorkSheet_Game.cell(k+1, 3).value
                # message = TextSendMessage(text="{} 號的身分為 {}".format(k, Surveyresult))
                print("{} 號的身分為 {}".format(k, Surveyresult))
                break
            else:
                # message = TextSendMessage(text="本回合沒有調查任何人~~~傻眼#")
                print("本回合沒有調查任何人~~~傻眼#")
        # line_bot_api.multicast(Innocentidlist, message)

        cell_list = WorkSheet_Game.range("E2:E9")
        for cell in cell_list:
            cell.value = "0"
        WorkSheet_Game.update_cells(cell_list)

        line_bot_api.push_message(WorkSheet_Game.cell(1, 1).value, [TextMessage(text="現在是第1天早上~~~"), TextMessage(text="昨天晚上的死者為 {}".format(str(k)+"號")), TextMessage(text="請開始討論並準備投票~~~")])

        for j in range(90):
            time.sleep(1)
            print(j+1)

        print("第1天公民投票開始囉~~~")


    else:
        pattern = re.compile(r'^(#)([1-8]{1})$')
        match = pattern.search(word)
        if match != None:
            IdentityConfirmList = WorkSheet_Game.col_values(3)
            commandnum = int(match.group(2))
            Murdereridlist = WorkSheet_Game.row_values(21)
            Detectiveidlist = WorkSheet_Game.row_values(22)
            try:
                cell = WorkSheet_Game.find(event.source.user_id)
                player_num = cell.row
                if WorkSheet_Game.cell(1, 3).value == "Night":
                    if event.source.type == "group":
                        message = TextSendMessage(text="現在是晚上閉嘴好嗎？")
                    elif IdentityConfirmList[player_num-1] == "Murderer":
                        WorkSheet_Game.update_cell(player_num, 5, str(commandnum))
                        # line_bot_api.multicast(Murdereridlist, [TextMessge(text="{} 把票投給了 {}號 {}".format(WorkSheet_Game.cell(player_num-1, 2).value, commandnum, WorkSheet_Game.cell(commandnum+1, 2).value))])
                        print(Murdereridlist)
                        print("{} 把票投給了 {}號 {}".format(WorkSheet_Game.cell(player_num, 2).value, commandnum, WorkSheet_Game.cell(commandnum+1, 2).value))
                    elif IdentityConfirmList[player_num-1] == "Detective":
                        WorkSheet_Game.update_cell(player_num, 5, str(commandnum))
                        # line_bot_api.multicast(Detectiveidlist, [TextMessge(text="{} 把票投給了 {}號 {}".format(WorkSheet_Game.cell(player_num-1, 2).value, commandnum, WorkSheet_Game.cell(commandnum+1, 2).value))])
                        print(Detectiveidlist)
                        print("{} 把票投給了 {}號 {}".format(WorkSheet_Game.cell(player_num-1, 2).value, commandnum, WorkSheet_Game.cell(commandnum+1, 2).value))
                elif WorkSheet_Game.cell(1, 3).value == "Day":
                    if event.source.type == "user":
                        message = TextSendMessage(text="白天不要說悄悄話行不行？")
                    else:
                        WorkSheet_Game.update_cell(player_num, 5, str(commandnum))
            except Exception as Error:
                message = TextSendMessage(text="沒有此玩家~~~")
                print(Error)
        else:
            message = TextSendMessage(text="指令操作錯誤~~~")
        
        # line_bot_api.reply_message(event.reply_token, message)


import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)