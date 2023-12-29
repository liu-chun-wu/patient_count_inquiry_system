from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    FlexMessage,
    FlexContainer,
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
    QuickReply,
    MessageAction,
    QuickReplyItem,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
import json

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

app = Flask(__name__)

configuration = Configuration(
    access_token="Lz9OkM8NsomlUL9XEO6RJ8BJt73IzUhoPZoQotdfTnA6mOwlFvGCosa7d00CGU92rlSd5w9dBd6Vistp4JmHw1Y1pjkHCHrn7FTxwbePvm7Gob5xamL/i/8707AKgHj3OUxsj+JmL5PwpW8QljusUQdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("b86924085bfea23f189357ea60ed1281")


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info
        (
            "Invalid signature. Please check your channel access token/channel secret."
        )
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        mtext = event.message.text

        # 爬蟲
        def webcrawling(area, subject):
            # 設置Chrome選項
            options = Options()
            # 創建webdriver實例
            chrome = webdriver.Chrome(options=options)
            # 網站的URL
            url = "https://wroom.vision.com.tw/MainPage/SearchResult.aspx"
            # 訪問網站
            chrome.get(url)
            # 選擇城市
            chrome.execute_script(
                "document.getElementsByClassName('qry-city')[0].style.display = 'block'")
            city = chrome.find_element(By.CLASS_NAME, 'qry-city')
            select = Select(city)
            select.select_by_visible_text('臺北市')
            # 選擇區域
            chrome.execute_script(
                "document.getElementsByClassName('qry-area')[0].style.display = 'block'")
            area_list = chrome.find_element(By.CLASS_NAME, 'qry-area')
            select = Select(area_list)
            select.select_by_visible_text(area)
            # 選擇院所類型
            chrome.execute_script(
                "document.getElementsByClassName('qry-type')[0].style.display = 'block'")
            clinic = chrome.find_element(By.CLASS_NAME, 'qry-type')
            select = Select(clinic)
            select.select_by_visible_text('診所')
            # 選擇院所科別
            chrome.execute_script(
                "document.getElementsByClassName('qry-subj')[0].style.display = 'block'")
            subject_list = chrome.find_element(By.CLASS_NAME, 'qry-subj')
            select = Select(subject_list)
            select.select_by_visible_text(subject)
            # 點擊搜索按鈕
            chrome.find_element(By.CLASS_NAME, 'ui-button-text').click()
            # 等待搜索結果加載
            page = 1
            all = []  # 全部
            while True:
                # 11頁要重置
                if page > 10:
                    page = 4

                # 獲取診所元素
                clinics = chrome.find_elements(
                    By.XPATH, "//*[@title='候診訊息']")
                # 沒有候診
                if len(clinics) == 0:
                    break

                # 遍歷診所元素
                for i in clinics:
                    # 創建新的webdriver實例
                    newurl = i.get_attribute('href')
                    newchrome = webdriver.Chrome(options=options)
                    newchrome.get(newurl)

                    information = []  # 一間
                    # 獲取診所信息
                    head = newchrome.find_element(
                        By.ID, 'dnn_ctr655_dnnTITLE_titleLabel')
                    addr = newchrome.find_element(
                        By.ID, 'dnn_ctr655_ViewVWWL_Clinics_mcsModuleCont_ctl00_lblCAddr')
                    phone = newchrome.find_element(
                        By.ID, 'dnn_ctr655_ViewVWWL_Clinics_mcsModuleCont_ctl00_lblCTel')
                    service = newchrome.find_element(
                        By.ID, 'dnn_ctr655_ViewVWWL_Clinics_mcsModuleCont_ctl00_lblServices')
                    try:
                        result = newchrome.find_elements(
                            By.CLASS_NAME, 'winfo-data')
                    except:
                        print("", end="")

                    if len(result):
                        information.append(head.text)
                        information.append(phone.text)
                        information.append(addr.text)
                        information.append(service.text)

                        temp = []
                        for i in result:
                            temp.append(i.text)
                        information.append(temp)

                    if len(information) != 0:
                        all.append(information)
                    newchrome.close()

                page += 1
                # 翻頁
                try:
                    chrome.find_element(
                        By.XPATH, '//*[@id="dnn_ctr1089_ViewVNHI_Clinics_mcsModuleCont_ctl00_visClinicList_gvwClinicList"]/tbody/tr[11]/td/table/tbody/tr/td[' + str(page) + ']/a').click()
                except:
                    chrome.close()
                    return all
            chrome.close()
            return all
        # 建立醫生資訊的json

        def BuildDocInfo(doc_list):
            doc_list_json = []
            for i in range(0, len(doc_list), 4):
                doc_name = doc_list[i]
                doc_time = doc_list[i+1]
                doc_order = doc_list[i+2]
                waiting = doc_list[i+3]

                content = [
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "margin": "none",
                        "contents": [
                            {
                                "type": "text",
                                "text": "候診人數",
                                "size": "md",
                                "color": "#555555",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": waiting,
                                "size": "md",
                                "color": "#555555",
                                "weight": "bold"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "醫師名稱",
                                "size": "md",
                                "color": "#555555",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": doc_name,
                                "size": "md",
                                "color": "#555555",
                                "weight": "bold"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "看診時段",
                                "size": "md",
                                "color": "#555555",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": doc_time,
                                "size": "md",
                                "color": "#555555",
                                "weight": "bold"
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "門診序",
                                "size": "md",
                                "color": "#555555",
                                "weight": "bold"
                            },
                            {
                                "type": "text",
                                "text": doc_order,
                                "size": "md",
                                "color": "#555555",
                                "weight": "bold"
                            }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xxl"
                    },
                ]
                doc_list_json.extend(content)
            return doc_list_json

        # 建立診所資訊的json
        def BuildClinicInfo(info):
            doc_info_list = info[4]
            doc_json_list = BuildDocInfo(doc_info_list)
            contents = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": info[0],
                            "weight": "bold",
                            "size": "xxl",
                            "wrap": True,
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": info[1],
                            "weight": "bold",
                            "size": "xxl",
                            "wrap": True,
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": info[2],
                            "weight": "bold",
                            "size": "xxl",
                            "wrap": True,
                            "margin": "md"
                        },
                        {
                            "type": "separator",
                            "margin": "xxl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "xxl",
                            "contents": doc_json_list
                        },
                    ]
                },
                "styles": {
                    "footer": {
                        "separator": True
                    }
                }
            }
            return contents

        # 所有的區域(台北市內)
        all_area_list = ["中正區", "大同區", "中山區", "松山區", "大安區",
                         "萬華區", "信義區", "士林區", "北投區", "內湖區", "南港區", "文山區"]
        # 所有醫療科別
        all_subject_list = ["不分科", "家醫科", "內科", "外科", "兒科", "婦產科", "骨科", "神經外科",
                            "泌尿科", "耳鼻喉科", "眼科", "皮膚科", "神經科", "精神科", "復健科", "整形外科", "牙科", "中醫科"]
        # 查詢診所
        if mtext == "@查詢診所":
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇要查詢的地區",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyItem(action=MessageAction(
                                    label="中正區", text="中正區")),
                                QuickReplyItem(action=MessageAction(
                                    label="大同區", text="大同區")),
                                QuickReplyItem(action=MessageAction(
                                    label="中山區", text="中山區")),
                                QuickReplyItem(action=MessageAction(
                                    label="松山區", text="松山區")),
                                QuickReplyItem(action=MessageAction(
                                    label="大安區", text="大安區")),
                                QuickReplyItem(action=MessageAction(
                                    label="萬華區", text="萬華區")),
                                QuickReplyItem(action=MessageAction(
                                    label="信義區", text="信義區")),
                                QuickReplyItem(action=MessageAction(
                                    label="士林區", text="士林區")),
                                QuickReplyItem(action=MessageAction(
                                    label="北投區", text="北投區")),
                                QuickReplyItem(action=MessageAction(
                                    label="內湖區", text="內湖區")),
                                QuickReplyItem(action=MessageAction(
                                    label="南港區", text="南港區")),
                                QuickReplyItem(action=MessageAction(
                                    label="文山區", text="文山區")),
                            ]
                        )
                    )
                    ]
                )
            )
        # 因為快速選單的選擇上限是13個，超過醫療科別的18個，所以這邊分兩次提供選項
        # 輸入為區域，回傳前半的醫療科別選項
        elif mtext in all_area_list:

            with open(r'linebot.txt', 'a+',) as f:
                f.write(mtext+" ")

            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇要查詢的醫療科別",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyItem(action=MessageAction(
                                    label="不分科", text="不分科")),
                                QuickReplyItem(action=MessageAction(
                                    label="家醫科", text="家醫科")),
                                QuickReplyItem(action=MessageAction(
                                    label="內科", text="內科")),
                                QuickReplyItem(action=MessageAction(
                                    label="外科", text="外科")),
                                QuickReplyItem(action=MessageAction(
                                    label="兒科", text="兒科")),
                                QuickReplyItem(action=MessageAction(
                                    label="婦產科", text="婦產科")),
                                QuickReplyItem(action=MessageAction(
                                    label="骨科", text="骨科")),
                                QuickReplyItem(action=MessageAction(
                                    label="神經外科", text="神經外科")),
                                QuickReplyItem(action=MessageAction(
                                    label="泌尿科", text="泌尿科")),
                                QuickReplyItem(action=MessageAction(
                                    label="更多醫療科別", text="更多醫療科別")),
                            ]
                        )
                    )
                    ]
                )
            )
        # 回傳後半的醫療科別選項
        elif mtext == "更多醫療科別":
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇要查詢的醫療科別",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyItem(action=MessageAction(
                                    label="耳鼻喉科", text="耳鼻喉科")),
                                QuickReplyItem(action=MessageAction(
                                    label="眼科", text="眼科")),
                                QuickReplyItem(action=MessageAction(
                                    label="皮膚科", text="皮膚科")),
                                QuickReplyItem(action=MessageAction(
                                    label="神經科", text="神經科")),
                                QuickReplyItem(action=MessageAction(
                                    label="精神科", text="精神科")),
                                QuickReplyItem(action=MessageAction(
                                    label="復健科", text="復健科")),
                                QuickReplyItem(action=MessageAction(
                                    label="整形外科", text="整形外科")),
                                QuickReplyItem(action=MessageAction(
                                    label="牙科", text="牙科")),
                                QuickReplyItem(action=MessageAction(
                                    label="中醫科", text="中醫科")),
                                QuickReplyItem(action=MessageAction(
                                    label="回到之前的醫療科別", text="回到之前的醫療科別")),
                            ]
                        )
                    )
                    ]
                )
            )
        # 回傳前半的醫療科別選項
        elif mtext == "回到之前的醫療科別":
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(
                        text="請選擇要查詢的醫療科別",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyItem(action=MessageAction(
                                    label="不分科", text="不分科")),
                                QuickReplyItem(action=MessageAction(
                                    label="家醫科", text="家醫科")),
                                QuickReplyItem(action=MessageAction(
                                    label="內科", text="內科")),
                                QuickReplyItem(action=MessageAction(
                                    label="外科", text="外科")),
                                QuickReplyItem(action=MessageAction(
                                    label="兒科", text="兒科")),
                                QuickReplyItem(action=MessageAction(
                                    label="婦產科", text="婦產科")),
                                QuickReplyItem(action=MessageAction(
                                    label="骨科", text="骨科")),
                                QuickReplyItem(action=MessageAction(
                                    label="神經外科", text="神經外科")),
                                QuickReplyItem(action=MessageAction(
                                    label="泌尿科", text="泌尿科")),
                                QuickReplyItem(action=MessageAction(
                                    label="更多醫療科別", text="更多醫療科別")),
                            ]
                        )
                    )
                    ]
                )
            )
        # 輸入為醫療科別
        elif mtext in all_subject_list:
            subject = mtext

            with open(r'linebot.txt', 'r+',) as f:
                history = f.readlines()
                for i in history:
                    if (len(i) != 9):
                        area = i.split()[0]

                        break
            with open(r'linebot.txt', 'a+',) as f:
                f.write(subject+" \n")
            # 檢查輸入是否符合要求
            if area in all_area_list and subject in all_subject_list:
                all = webcrawling(area, subject)
                for i in all:
                    print(i)
                # 檢查是否有相關資料
                if len(all) == 0:
                    line_bot_api.reply_message_with_http_info(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[TextMessage(text="該地區沒有符合的診所資料")]
                        )
                    )
                else:
                    flex_list = []
                    for i in all:
                        flex_list.append(BuildClinicInfo(i))
                    line_bot_api.reply_message(
                        ReplyMessageRequest(
                            reply_token=event.reply_token,
                            messages=[FlexMessage(
                                alt_text="hello", contents=FlexContainer.from_json(json.dumps(
                                    {"type": "carousel", "contents": flex_list}))
                            )]
                        )
                    )
            # 輸入不合法
            else:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="輸入了無效的地區或是科別")]
                    )
                )


# 啟動程式
if __name__ == "__main__":
    app.run()
