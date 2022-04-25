# meeter
Google Meet 自動化  
*開發中，仍不穩定*  


## 使用方法
1.  下載 chromedriver，預設放置於 `drivers` 資料夾，**目前僅支援 chrome 瀏覽器**
    1.  在 [chrome://settings/help](chrome://settings/help) 檢查 Google Chrome 版本，
    2.  下載相同版本的 Chromedirver，連結: [https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)
2.  調整設定檔
    *   `config.yml`主要設定檔，包含帳號密碼、瀏覽器參數
    *   `data/meets.json` 編輯 Google Meet 代碼，參數:
        *   code: 會議代碼，**必填**
        *   join_msg: 加入時發送的訊息，可選
        *   start_time: 開始時間(年-月-日_時:分:秒)，**必填**
        *   end_time: 結束時間，**必填**
        *   repeat: 重複間隔，可選
        *   時間格式: `YYYY-mm-dd_HH:MM:SS`
3.  開始執行
    *   Python 原始碼(建議使用 python 3.10.2 以上版本)
    1.  執行 `start.bat` 或輸入以下指令
    2.  開啟 cmd 執行指令，安裝所需的 module
        ```bash
        pip install -r requirements.txt
        ```
    3.  輸入指令開始執行程式，或執行 `start.bat`
        ```bash
        python main.py
        ```
    *   執行檔
    1.  執行 `meeter.exe`，不須安裝 python，**注意: 僅支援 Windows 系統**

## 注意事項
*   目前正在開發中，不太穩定，可能發生未知錯誤，且功能不完善
*   目前僅測試可於 Windows 10 運行，不確定其他作業系統是否能正常運行。
