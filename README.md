# meeter
Google Meet 自動化  
*開發中，尚不穩定*

## 使用方法
1.  安裝 python，建議使用 `3.10.2` 以上版本，  
    下載連結:[https://www.python.org/downloads/](https://www.python.org/downloads/)
2.  下載 chromedriver，預設放置於 `drivers` 資料夾，  
    **目前僅支援 chrome 瀏覽器**，下載連結: [https://chromedriver.chromium.org/](https://chromedriver.chromium.org/)
3.  在 `.env` 設定登入帳號密碼
4.  在 `data/meets.json` 編輯 Google Meet 代碼
5.  開啟 cmd 執行指令，安裝所需的 module
```bash
pip install -r requirements.txt
```
6.  輸入指令開始執行程式，或執行 `start.bat`
```bash
python main.py
```

## 注意事項
* 目前正在開發中，不太穩定，可能發生未知錯誤，且功能不完善
* 目前僅測試可於 Windows 10 及 Windows 11 執行，不確定其他作業系統是否能正常運行。