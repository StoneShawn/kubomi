import firebase_admin
from firebase_admin import credentials, firestore
import json
import sys

def upload_nested_json(json_path, top_collection, top_doc, sub_collection, sub_doc):
    # 初始化 Firebase（只初始化一次）
    if not firebase_admin._apps:
        cred = credentials.Certificate("/Users/shiyixiang/.jenkins/secrets/serviceAccountKey.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # 讀取 JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 定位路徑：app/android/version/7.1.1101
    doc_ref = (
        db.collection(top_collection)
        .document(top_doc)
        .collection(sub_collection)
        .document(sub_doc)
    )

    doc_ref.set(data)
    print(f"✅ 成功上傳到 {top_collection}/{top_doc}/{sub_collection}/{sub_doc}")

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("用法: python upload_to_firestore.py <json_path> <top_collection> <top_doc> <sub_collection> <sub_doc>")
    else:
        upload_nested_json(
            sys.argv[1],  # json_path
            sys.argv[2],  # top_collection, e.g. "app"
            sys.argv[3],  # top_doc, e.g. "android"
            sys.argv[4],  # sub_collection, e.g. "version"
            sys.argv[5],  # sub_doc, e.g. "7.1.1101"
        )