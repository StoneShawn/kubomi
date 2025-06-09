import os
import xml.etree.ElementTree as ET
import json
import argparse

def get_real_file_line_count(source_root, file_name):
    for root, dirs, files in os.walk(source_root):
        if file_name in files:
            try:
                with open(os.path.join(root, file_name), "r", encoding="utf-8") as f:
                    return sum(1 for _ in f)
            except Exception:
                return None
    return None

def generate_file_based_report(xml_path, src_root, version):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    report_data = {}
    total_logic = 0
    total_covered = 0

    for pkg in root.findall("package"):
        for source in pkg.findall("sourcefile"):
            file_name = source.get("name")
            counters = {c.get("type"): (int(c.get("missed")), int(c.get("covered")))
                        for c in source.findall("counter")}
            missed, covered = counters.get("LINE", (0, 0))
            logic_total = missed + covered
            real_line = get_real_file_line_count(src_root, file_name)

            report_data[file_name] = {
                "fileLine": real_line if real_line else logic_total,
                # "logicLine": logic_total,
                "unitTestCoverLine": logic_total,
                "unitTestPassLine": covered,
                "coverage": round((covered / logic_total) * 100, 2) if logic_total else 0.0,
                # "logicCoverage": round((covered / logic_total) * 100, 2) if logic_total else 0.0,
                "isChangeFromPreviousVersion": False
            }

            total_logic += logic_total
            total_covered += covered

    avg_coverage = round((total_covered / total_logic) * 100, 2) if total_logic > 0 else 0.0

    return {
        "UnitTestReport": {
            "Android": {
                "version": [
                    {
                        version: {
                            "versionInfo": {
                                "avgCoverage": avg_coverage,
                                "allCoveredLine": total_covered,
                                "diffLineChange": 0,
                                "displayDiffAvgCoverage": 0
                            },
                            "fileCodeCoverage": report_data
                        }
                    }
                ]
            }
        }
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate file-based Jacoco coverage report")
    parser.add_argument("--input", required=True, help="Path to coverage.xml")
    parser.add_argument("--src", required=True, help="Path to source root for .kt files")
    parser.add_argument("--output", required=True, help="Output JSON path")
    parser.add_argument("--version", required=True, help="Version label")
    args = parser.parse_args()

    report = generate_file_based_report(args.input, args.src, args.version)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ File-based coverage report saved to {args.output}")