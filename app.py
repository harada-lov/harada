import os
import math
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import os

# このPythonファイル自体の場所を取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 同じフォルダ内のファイルパスを作成
DATABASE_FILE = os.path.join(BASE_DIR, "coordinate_database_29bit.txt")

# デバッグ用：起動時に「どこを探しているか」を表示させる
print(f"Searching for database at: {DATABASE_FILE}")
# DATABASE_FILE = "/Users/hayatious/Downloads/選択項目から作成したフォルダ/coordinate_database_29bit.txt"
#DATABASE_FILE = "coordinate_database_29bit.txt"

def calculate_coordinates(binary_str, base=0.8):
    """2進数文字列を29bitに補完してx, y座標を計算する"""
    
    # 入力を29桁の2進数として扱い、足りない分は左側を '0' で埋める
    # 例: "101" -> "00000000000000000000000000101"
    full_binary = binary_str.zfill(29)
    
    # もし29文字を超えて入力された場合は、後ろの29文字だけを使う（念のため）
    if len(full_binary) > 29:
        full_binary = full_binary[-29:]

    directions = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    x, y = 0, 0
    dir_idx = 0
    
    # 初期の1歩目 (常に共通)
    dist0 = 1
    current_x = x + dist0 * directions[dir_idx][0]
    current_y = y + dist0 * directions[dir_idx][1]

    # 29ビット分、すべて計算に含める
    for i, bit in enumerate(full_binary):
        step = i + 2 # 2歩目からスタート
        distance = base ** (step - 1)
        
        if bit == '0':
            dir_idx = (dir_idx + 1) % 4
        elif bit == '1':
            dir_idx = (dir_idx - 1) % 4
            
        current_x += distance * directions[dir_idx][0]
        current_y += distance * directions[dir_idx][1]

    return current_x, current_y

def search_from_database(target_x, target_y, epsilon=1e-5):
    """データベースファイルから最も近い座標を持つ2進数を探す (Decrypt)"""
    if not os.path.exists(DATABASE_FILE):
        return None, "データベースファイルが見つかりません。"

    found_bin = None
    # 巨大ファイルをメモリ節約しながら読み込み
    with open(DATABASE_FILE, 'r', buffering=1024*1024) as f:
        for line in f:
            try:
                parts = line.strip().split(',')
                if len(parts) < 3: continue
                
                bin_str = parts[0]
                x = float(parts[1])
                y = float(parts[2])
                
                # 誤差範囲内か判定
                if math.hypot(x - target_x, y - target_y) < epsilon:
                    found_bin = bin_str
                    break
            except ValueError:
                continue
    return found_bin, None

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    input_str = data.get('binary_str', '').strip()
    
    try:
        # 入力にコンマが含まれている場合は「復号モード」とみなす
        if ',' in input_str:
            parts = input_str.split(',')
            if len(parts) != 2:
                return jsonify({"success": False, "error": "座標は 'x,y' の形式で入力してください"})
            
            tx = float(parts[0])
            ty = float(parts[1])
            
            result_bin, err = search_from_database(tx, ty)
            
            if result_bin:
                return jsonify({
                    "success": True, 
                    "x": f"Plaintext: {result_bin}", # フロントの表示欄を流用
                    "y": "Completed"
                })
            else:
                return jsonify({"success": False, "error": err or "該当データなし"})
        
        # コンマがない場合は通常の「暗号化モード」
        else:
            final_x, final_y = calculate_coordinates(input_str)
            return jsonify({
                "success": True, 
                "x": final_x, 
                "y": final_y
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # ファイルがない場合の警告
    if not os.path.exists(DATABASE_FILE):
        print(f"警告: {DATABASE_FILE} が見つかりません。復号機能は動作しません。")
    app.run(debug=True, port=5000)
