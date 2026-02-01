# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 08:50:16 2026

@author: keiji
"""

import json
import os

# ==========================================
# 【重要】ファイルの場所を絶対パスで固定する
# ==========================================
# 1. この logic.py ファイルがあるフォルダの場所を取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. そのフォルダの中にある data.json を指定
DATA_PATH = os.path.join(BASE_DIR, "data.json")

# --- 定数設定 ---
GYM_OPTIONS = ["エニタイム", "ゴールドジム", "トレーニングルーム"]
LEVEL_OPTIONS = ["初心者", "上級者"]
DAYS = ["月", "火", "水", "木", "金"]
TIMES = [
    "08:00-10:00", "10:00-12:00", "12:00-14:00", 
    "14:00-16:00", "16:00-18:00", "18:00-20:00", "20:00-22:00"
]

# --- 1. データの読み込み ---
def load_data():
    """固定したパス(DATA_PATH)から読み込む"""
    # ファイルがない場合は空のリストを返す
    if not os.path.exists(DATA_PATH):
        return []

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"読み込みエラー: {e}")
        return []

# --- 2. データの保存 ---
def save_data(data_list):
    """固定したパス(DATA_PATH)に保存する"""
    try:
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)
        print(f"保存成功: {DATA_PATH}")  # どこに保存したかログに出す
    except Exception as e:
        print(f"保存エラー: {e}")

# --- 3. マッチング計算ロジック ---
def find_matches(current_user, all_users):
    results = []
    
    my_gyms = set(current_user["gyms"])
    my_schedule = set(current_user["schedule"])
    my_level = current_user["level"]

    for other in all_users:
        if other["name"] == current_user["name"]:
            continue
            
        other_gyms = set(other["gyms"])
        other_schedule = set(other["schedule"])
        other_level = other["level"]
        
        common_gyms = my_gyms & other_gyms
        common_schedule = my_schedule & other_schedule
        is_same_level = (my_level == other_level)

        if len(common_gyms) > 0 and len(common_schedule) > 0:
            score = (len(common_schedule) * 10) + (20 if is_same_level else 0)
            
            results.append({
                "name": other["name"],
                "level": other["level"],
                "common_gyms": list(common_gyms),
                "common_schedule": list(common_schedule),
                "score": score,
                "comment": other.get("comment", "")
            })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results