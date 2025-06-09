#!/bin/bash

VARIANT=$1
FILTER_INLINED=${3:-false}

# SDK 路徑設定，根據你的環境調整
if [ ! -f local.properties ]; then
  echo "sdk.dir=/Users/shiyixiang/Library/Android/sdk" > local.properties
fi

if [ -z "$VARIANT" ]; then
  echo "❌ 用法： ./run_full_coverage.sh <module> <BuildVariant> [<filterInlined>]"
  exit 1
fi

# 自動偵測版本號
echo "🔍 自動從 build.gradle 偵測版本號..."
VERSION=$(grep versionName ./app/build.gradle.kts | head -n1 | cut -d '"' -f2 | sed 's/\.*$//')
if [ -z "$VERSION" ]; then
  echo "❌ 無法偵測版本號，請確認 build.gradle 是否正確"
  exit 1
fi
echo "✅ 偵測到版本號：$VERSION"

TASK="test${VARIANT}UnitTest"
VARIANT_LOWER=$(echo "$VARIANT" | tr '[:upper:]' '[:lower:]')
COVERAGE_SUBDIR="$(echo "${VARIANT:0:1}" | tr '[:upper:]' '[:lower:]')${VARIANT:1}UnitTest"

COVERAGE_EXEC="app/build/outputs/unit_test_code_coverage/$COVERAGE_SUBDIR/${TASK}.exec"
CLASS_DIR="app/build/tmp/kotlin-classes/$VARIANT_LOWER"
SRC_DIR="app/src/main/java"

TIMESTAMP=$(date +%y%m%d_%H%M)
VARIANT_UNDERSCORE=$(echo "$VARIANT" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1_\2/g' | tr '[:upper:]' '[:lower:]')
REPORT_DIR="./code_coverage/coverage-report/${VARIANT_UNDERSCORE}/${TIMESTAMP}"

# 記錄舊 exec 檔案時間（若存在）
OLD_EXEC_TIMESTAMP=0
if [ -f "$COVERAGE_EXEC" ]; then
  OLD_EXEC_TIMESTAMP=$(stat -f "%m" "$COVERAGE_EXEC")
fi

# 1️⃣ 執行測試
echo "🚀 執行測試中..."
./gradlew ":app:$TASK" --continue

# 2️⃣ 檢查 coverage.exec 是否存在
echo "📂 當前目錄：$(pwd)"
echo "📂 檢查 coverage.exec 路徑：$COVERAGE_EXEC"
ls -l "$(dirname "$COVERAGE_EXEC")"  # 列出目錄內容，確認檔案是否存在
if [ ! -f "$COVERAGE_EXEC" ]; then
  echo "❌ 測試結束後找不到 coverage exec，可能測試錯誤未產出"
  exit 1
fi
# 3️⃣ 比對是否為新的 coverage exec
NEW_EXEC_TIMESTAMP=$(stat -f "%m" "$COVERAGE_EXEC")
if [ "$NEW_EXEC_TIMESTAMP" -le "$OLD_EXEC_TIMESTAMP" ]; then
  echo "❌ coverage exec 未更新，仍為舊檔案 ➜ 中止後續報告產出"
  exit 1
fi
echo "✅ 找到最新 coverage exec：$COVERAGE_EXEC"

# 4️⃣ 處理 inline 類別（可選）
if [ "$FILTER_INLINED" == "true" ]; then
  echo "📦 過濾 inline 類別..."
  CLEAN_CLASS_DIR="build/tmp/clean-kotlin-classes/$VARIANT_LOWER"
  mkdir -p "$CLEAN_CLASS_DIR"
  find "$CLASS_DIR" -name "*.class" ! -name "*\$inlined\$*" | while read -r class_file; do
    relative_path="${class_file#$CLASS_DIR/}"
    target_path="$CLEAN_CLASS_DIR/$relative_path"
    mkdir -p "$(dirname "$target_path")"
    cp "$class_file" "$target_path"
  done
else
  CLEAN_CLASS_DIR="$CLASS_DIR"
fi

# 5️⃣ 下載 Jacoco CLI（若尚未存在）
if [ ! -f "jacoco-cli.jar" ]; then
  echo "📥 下載 Jacoco CLI..."
  curl -L -o jacoco-cli.jar https://repo1.maven.org/maven2/org/jacoco/org.jacoco.cli/0.8.11/org.jacoco.cli-0.8.11-nodeps.jar
fi

# 6️⃣ coverage.xml & html
mkdir -p "$REPORT_DIR"
echo "📊 產出 coverage.xml..."
java -jar jacoco-cli.jar report "$COVERAGE_EXEC" \
  --classfiles "$CLEAN_CLASS_DIR" \
  --sourcefiles "$SRC_DIR" \
  --xml "$REPORT_DIR/coverage.xml" \
  --html "$REPORT_DIR/html"

# 7️⃣ 轉成扁平 JSON
echo "🧪 coverage.xml ➜ raw_unit_test_report.json..."
python3 ./code_coverage/coverage_to_json.py \
  --input "$REPORT_DIR/coverage.xml" \
  --src "$SRC_DIR" \
  --version "$VERSION" \
  --output "$REPORT_DIR/raw_unit_test_report.json"

if [ ! -f "$REPORT_DIR/raw_unit_test_report.json" ]; then
  echo "❌ 未產出 raw_unit_test_report.json"
  exit 1
fi

# 8️⃣ 比較差異 ➜ unit_test_report.json
echo "📐 比較差異 coverage..."
python3 ./code_coverage/compare_coverage.py \
  --current "$REPORT_DIR/raw_unit_test_report.json" \
  --archive "coverage-archive/$VARIANT_UNDERSCORE" \
  --version "$VERSION" \
  --output "$REPORT_DIR/unit_test_report.json"

# 9️⃣ 額外分類報告（套件樹）
echo "📂 產出分類報告 structured_tree.json..."
python3 ./code_coverage/coverage_to_package_tree.py \
  --input "$REPORT_DIR/coverage.xml" \
  --output "$REPORT_DIR/structured_tree.json"

# 🔟 歸檔
ARCHIVE_PATH="./code_coverage/coverage-archive/${VARIANT_UNDERSCORE}/${VERSION}.json"
ARCHIVE_WEB_PATH="./code_coverage/coverage-archive-web/${VARIANT_UNDERSCORE}/${VERSION}.json"
mkdir -p "$(dirname "$ARCHIVE_PATH")" "$(dirname "$ARCHIVE_WEB_PATH")"
cp "$REPORT_DIR/unit_test_report.json" "$ARCHIVE_PATH"
cp "$REPORT_DIR/structured_tree.json" "$ARCHIVE_WEB_PATH"

# ✅ 結尾
echo ""
echo "✅ 測試報告完成"
echo "📄 JSON（扁平）：$REPORT_DIR/unit_test_report.json"
echo "📄 JSON（分類）：$REPORT_DIR/structured_tree.json"
echo "🌐 HTML 報告：$REPORT_DIR/html/index.html"
echo "📦 歸檔 JSON：$ARCHIVE_PATH"
echo "📦 歸檔 PACKAGE JSON：$ARCHIVE_WEB_PATH"


# 存入firebase
echo "📂 存入firebase..."
python3 ./code_coverage/upload_to_firestore.py \
  "./code_coverage/coverage-archive-web/${VARIANT_UNDERSCORE}/${VERSION}.json" \
  "app" "android" "version" "${VERSION}"