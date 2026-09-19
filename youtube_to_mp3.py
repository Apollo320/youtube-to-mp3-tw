import os
import yt_dlp
import opencc

# 建立一個自訂處理器：在轉成 MP3 的瞬間攔截檔案進行處理
class OpenCCTraditionalPP(yt_dlp.postprocessor.PostProcessor):
    def run(self, info):
        filepath = info.get('filepath')
        if filepath and os.path.exists(filepath):
            dir_name = os.path.dirname(filepath)
            file_name = os.path.basename(filepath)
            
            # 防呆機制：如果單曲不小心產生了 "NA - " (yt-dlp的無序號預設值)，把它清掉
            if file_name.startswith("NA - "):
                file_name = file_name[5:]
                
            # 進行簡轉繁
            converter = opencc.OpenCC('s2tw.json')
            new_file_name = converter.convert(file_name)
            
            # 如果有變動 (清理了 NA- 或 有簡轉繁)，就重新命名檔案
            new_filepath = os.path.join(dir_name, new_file_name)
            if filepath != new_filepath:
                os.rename(filepath, new_filepath)
                print(f"\n[檔名處理成功] {os.path.basename(filepath)} -> {new_file_name}")
                info['filepath'] = new_filepath 
                
        return [], info

def download_youtube_mp3(url):
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    
    print("\n[資訊] 正在準備下載與轉檔，請稍候...")
    print(f"[資訊] MP3 將會存檔至：{downloads_folder}")
    
    # 關鍵修改：直接判斷網址有沒有 'list='，如果有就加入序號格式 (%02d 代表 01, 02 兩位數編號)
    if 'list=' in url:
        outtmpl = os.path.join(downloads_folder, '%(playlist_index)02d - %(title)s.%(ext)s')
    else:
        outtmpl = os.path.join(downloads_folder, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': outtmpl,
        'restrictfilenames': False,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 將我們的「攔截式處理器」掛載進去
            ydl.add_post_processor(OpenCCTraditionalPP())
            
            ydl.extract_info(url, download=True)
            print(f"\n[成功] 所有下載與轉檔作業已完成！請到「下載」資料夾查看！")

    except Exception as e:
        print(f"\n[錯誤] 下載失敗：{e}")

if __name__ == "__main__":
    print("=== YouTube 轉 MP3 下載工具 (支援清單序號與簡轉繁) ===")
    while True:
        url = input("\n請輸入 YouTube 影片/播放清單網址 (輸入 q 離開): ").strip()
        if url.lower() == 'q':
            print("感謝使用，再見！")
            break
        if not url:
            print("網址不能為空，請重新輸入。")
            continue
            
        download_youtube_mp3(url)