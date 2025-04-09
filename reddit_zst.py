import zstandard as zstd
import json
import os

# 修改為你的檔案路徑
zst_path = "dat/reddit/subreddits24/nfl_submissions.zst"

# 設定你要預覽幾筆資料（可自行調整）
PREVIEW_LIMIT = 10

# 逐行讀取與解析 zst 中的 JSON lines
def preview_zst_file(path, limit=10):
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return

    with open(path, 'rb') as f:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(f) as reader:
            buffer = b""
            count = 0

            for chunk in iter(lambda: reader.read(8192), b""):
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        obj = json.loads(line.decode("utf-8"))
                        print(json.dumps(obj, indent=2))  # 印出完整 JSON 結構
                        count += 1
                        if count >= limit:
                            print("\n✅ Preview done.")
                            return
                    except Exception as e:
                        print(f"⚠️ Error parsing line: {e}")

if __name__ == "__main__":
    preview_zst_file(zst_path, PREVIEW_LIMIT)
