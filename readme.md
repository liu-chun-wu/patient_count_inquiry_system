資訊工程概論project
===
# project名稱 : 台北市區域醫療資源整合平台
# 運作流程:
1. line bot 圖文選單啟動查詢功能 
2. 使用者選取欲查詢地區和科別
3. 發送訊息到伺服器開始進行爬蟲
4. 爬蟲完的資訊整理後傳回line bot介面
# LINE bot: 
- 使用官方提供的Messaging API把爬蟲的伺服器和line bot連結起來
# WebCrawling:
- 環境:Anaconda Spyde
- 使用python編寫程式並使用Seleium套件進行爬蟲
# Ngrok:
- 可以把外界的請求轉發到本機指定的port，這邊做為測試用的暫時伺服器
