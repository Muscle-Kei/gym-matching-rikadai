# -*- coding: utf-8 -*-
"""
Created on Mon Jan 26 09:02:23 2026

@author: keiji
"""

import streamlit as st
import datetime
import logic  # 先ほど作成したlogic.pyを読み込み

# --- ページ設定 ---
st.set_page_config(page_title="合トレマッチング", layout="wide")

# --- 定数読み込み ---
# logic.pyで定義した定数を使うことでズレを防ぐ
GYM_OPTIONS = logic.GYM_OPTIONS
LEVEL_OPTIONS = logic.LEVEL_OPTIONS
DAYS = logic.DAYS
TIMES = logic.TIMES

def main():
    st.title("💪 合トレ マッチングシステム")

    # --- 1. ユーザー認証（簡易版） ---
    st.sidebar.header("ログイン")
    # 実運用ではパスワード等が必要ですが、プロトタイプなので名前だけで識別します
    user_name = st.sidebar.text_input("名前を入力してください", key="user_name")
    password = st.sidebar.text_input("パスワード", type="password", key="user_pass")
    
    if not user_name or not password:
        st.warning("名前とパスワードを入力してください")
        return

    # 既存データの読み込み
    all_users = logic.load_data()
    # 自分のデータを探す
    current_user_data = next((u for u in all_users if u["name"] == user_name), None)

    # --- 認証ロジック ---
    if current_user_data:
        # 既存ユーザーの場合：パスワードチェック
        # （データにパスワードがない古いデータの場合は、今回入力したものを設定する救済措置）
        saved_pass = current_user_data.get("password")
        
        if saved_pass and saved_pass != password:
            st.error("パスワードが違います")
            return
        elif not saved_pass:
            # パスワードがまだ登録されていないデータ用（移行措置）
            st.info("初回パスワードを設定します。")
    else:
        # 新規ユーザーの場合：入力されたパスワードで登録予定
        st.info(f"「{user_name}」さんは新規登録になります。このパスワードを記憶してください。")
    
    # 新規ユーザーの場合の初期値設定
    default_level = current_user_data["level"] if current_user_data else LEVEL_OPTIONS[0]
    default_gyms = current_user_data["gyms"] if current_user_data else []
    default_schedule = current_user_data["schedule"] if current_user_data else []
    default_comment = current_user_data.get("comment", "") if current_user_data else ""

    # --- 2. プロフィール入力フォーム ---
    st.subheader(f"👤 {user_name}さんの設定")
    
    with st.expander("プロフィール・スケジュールの編集", expanded=True):
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # レベルとジムの選択
            level = st.radio("レベル", LEVEL_OPTIONS, index=LEVEL_OPTIONS.index(default_level))
            gyms = st.multiselect("利用ジム（複数選択可）", GYM_OPTIONS, default=default_gyms)
            comment = st.text_area("ひとこと", default_comment)

        with col2:
            st.write("**希望スケジュールを選択（平日 8:00-22:00）**")
            # --- 詳細型グリッドレイアウト ---
            # 曜日ごとに列を作る（5列）
            cols = st.columns(len(DAYS))
            selected_schedule = []

            for i, day in enumerate(DAYS):
                with cols[i]:
                    st.markdown(f"**{day}**") # 曜日のヘッダー
                    for time_slot in TIMES:
                        # データ保存用のキー作成（例: "月_08:00-10:00"）
                        schedule_key = f"{day}_{time_slot}"
                        
                        # チェックボックス（保存データにあればチェックを入れる）
                        is_checked = schedule_key in default_schedule
                        
                        if st.checkbox(time_slot, key=schedule_key, value=is_checked):
                            selected_schedule.append(schedule_key)

        # 保存ボタン
        if st.button("設定を保存する", type="primary"):
            new_user_data = {
                "name": user_name,
                "password": password,
                "level": level,
                "gyms": gyms,
                "schedule": selected_schedule,
                "comment": comment
            }
            
            # リストから既存の自分を消して、新しい自分を追加（更新）
            # ※同じ名前があれば上書き、なければ追加
            updated_users = [u for u in all_users if u["name"] != user_name]
            updated_users.append(new_user_data)
            
            logic.save_data(updated_users)
            st.success("プロフィールを保存しました！土日のマッチング公開をお待ちください。")
            # 画面をリロードして反映
            st.rerun()

    # --- 3. マッチング機能（曜日による制限） ---
    st.markdown("---")
    st.subheader("🔍 マッチング結果")

    # 今日の曜日を取得（0:月, 1:火, ... 5:土, 6:日）
    today_weekday = datetime.datetime.now().weekday()
    
    # --- 開発用デバッグモード（ここをTrueにすると平日でも結果が見れます） ---
    # 運用時は False にしてください
    DEV_MODE = True 

    if today_weekday >= 5 or DEV_MODE:
        # 土日（5, 6）の場合
        if not current_user_data:
            st.info("まずはプロフィールを保存してください。")
        else:
            st.write("条件の合うパートナーを表示します（スコア順）")
            
            # ロジックファイルを使ってマッチング計算
            matches = logic.find_matches(current_user_data, all_users)
            
            if matches:
                for m in matches:
                    # カード形式で表示
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1])
                        with c1:
                            st.markdown(f"### {m['name']} <span style='font-size:0.8em; color:gray'>({m['level']})</span>", unsafe_allow_html=True)
                            st.write(f"💬 {m.get('comment', 'コメントなし')}")
                            
                            # 共通項目の表示
                            common_days_display = [s.replace("_", " ") for s in m['common_schedule']]
                            st.write(f"📍 **共通ジム:** {', '.join(m['common_gyms'])}")
                            st.write(f"⏰ **合う時間:** {', '.join(common_days_display)}")
                        
                        with c2:
                            st.metric("マッチ度", f"{m['score']}点")
            else:
                st.warning("現在、条件が一致する相手は見つかりませんでした。")
    else:
        # 平日の場合
        st.info("🚧 **現在は「登録期間」です** 🚧")
        st.write("マッチング結果は **土曜日・日曜日** に公開されます。")
        st.write("今のうちにスケジュールを登録・更新しておきましょう！")

if __name__ == "__main__":
    main()