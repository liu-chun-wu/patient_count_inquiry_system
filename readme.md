# 🏥 門診人數查詢系統｜LINE Bot + Web Crawling + Ngrok

一個互動式的 LINE Bot 系統，讓使用者能透過 LINE 介面查詢指定診所的門診資訊。後端自動爬取官方網站的即時資料並回傳給使用者。本專案以 Ngrok 作為測試環境的暫時伺服器。

---

## 📌 功能簡介

- 使用者透過 LINE Bot 與系統互動
- 點選診所選單後，自動爬取門診人數資訊
- 將即時資料回傳給使用者

---

## 🛠️ 技術架構

| 模組        | 技術 / 工具 |
|-------------|--------------|
| 📱 前端介面   | LINE Messaging API |
| 🕷️ 爬蟲工具   | Python + Selenium |
| 🧪 開發環境   | Anaconda (Spyder IDE) |
| 🌐 測試部署   | Ngrok 轉發至本機 Flask 伺服器 |
| 🔗 串接方式   | LINE Bot ↔ Flask API ↔ 爬蟲結果 |

---

## 🔍 專案流程

1. 使用者發送訊息或點選 LINE Bot 的診所查詢按鈕  
2. 系統透過 Flask 接收請求並啟動爬蟲模組（Selenium）
3. 從官方網站即時抓取診所門診人數資訊
4. 回傳整理後的資訊至 LINE Bot 回應使用者
