import argparse
import json
from pathlib import Path

def parse_version(version_str):
    return tuple(map(int, version_str.strip().split(".")))

def find_previous_version(current_version, archive_dir):
    current_parsed = parse_version(current_version)
    candidates = []

    for path in Path(archive_dir).glob("*.json"):
        try:
            ver = path.stem
            parsed = parse_version(ver)
            if parsed < current_parsed:
                candidates.append((parsed, path))
        except Exception:
            continue

    if not candidates:
        return None

    return sorted(candidates, reverse=True)[0][1]

def compare_custom_format(current_path, previous_path, current_version, output_path):
    current_data = json.loads(Path(current_path).read_text(encoding='utf-8'))
    previous_data = json.loads(Path(previous_path).read_text(encoding='utf-8'))

    current_entry = current_data["UnitTestReport"]["Android"]["version"][0]
    previous_entry = previous_data["UnitTestReport"]["Android"]["version"][0]
    previous_version = list(previous_entry.keys())[0]

    current_info = current_entry[current_version]["versionInfo"]
    previous_info = previous_entry[previous_version]["versionInfo"]
    current_files = current_entry[current_version]["fileCodeCoverage"]
    previous_files = previous_entry[previous_version]["fileCodeCoverage"]

    diffLineChange = current_info["allCoveredLine"] - previous_info["allCoveredLine"]

    changed_coverages = []
    for filename, cur in current_files.items():
        prev = previous_files.get(filename)
        is_changed = False
        if prev:
            if abs(cur["coverage"] - prev["coverage"]) > 0.01:
                is_changed = True
        else:
            is_changed = True

        cur["isChangeFromPreviousVersion"] = is_changed

        if is_changed and cur["coverage"] > 0:
            changed_coverages.append(cur["coverage"])

    displayDiffAvgCoverage = round(
        sum(changed_coverages) / len(changed_coverages), 2
    ) if changed_coverages else 0.0

    current_info["diffLineChange"] = diffLineChange
    current_info["displayDiffAvgCoverage"] = displayDiffAvgCoverage

    result = {
        "UnitTestReport": {
            "Android": {
                "version": [
                    {
                        current_version: {
                            "versionInfo": current_info,
                            "fileCodeCoverage": current_files
                        }
                    }
                ]
            }
        }
    }

    Path(output_path).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare coverage reports with version archive")
    parser.add_argument("--current", required=True, help="Path to current unit_test_report.json")
    parser.add_argument("--archive", required=True, help="Path to coverage-archive/<variant>/")
    parser.add_argument("--version", required=True, help="Current version, e.g. 7.7.1801")
    parser.add_argument("--output", required=True, help="Path to output updated JSON")

    args = parser.parse_args()

    previous_path = find_previous_version(args.version, args.archive)
    if not previous_path:
        print("⚠️ 找不到前一版本，跳過比對")
        Path(args.output).write_text(Path(args.current).read_text(encoding='utf-8'))
    else:
        compare_custom_format(args.current, previous_path, args.version, args.output)
        print(f"✅ 已完成與前一版比對：{previous_path.name} ➜ {args.output}")