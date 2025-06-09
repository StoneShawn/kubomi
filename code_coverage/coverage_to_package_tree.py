import xml.etree.ElementTree as ET
import json
import argparse
from collections import defaultdict
from pathlib import Path

def generate_structured_report(xml_path, output_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    package_data = defaultdict(lambda: {
        "summary": {
            "coverage": 0.0,
            "fileLine": 0,
            "unitTestCoverLine": 0,
            "unitTestPassLine": 0
        },
        "classes": []
    })

    total_file_lines = 0
    total_covered = 0

    for pkg in root.findall("package"):
        pkg_name = pkg.get("name")

        for source in pkg.findall("sourcefile"):
            file_name = source.get("name")
            counters = {
                c.get("type"): (int(c.get("missed")), int(c.get("covered")))
                for c in source.findall("counter")
            }

            missed, covered = counters.get("LINE", (0, 0))
            logic_total = missed + covered

            if logic_total == 0:
                continue

            coverage = round((covered / logic_total) * 100, 2)

            file_entry = {
                "name": file_name,
                "coverage": coverage,
                "fileLine": logic_total,
                "unitTestCoverLine": logic_total,
                "unitTestPassLine": covered
            }

            package_data[pkg_name]["classes"].append(file_entry)
            package_data[pkg_name]["summary"]["fileLine"] += logic_total
            package_data[pkg_name]["summary"]["unitTestCoverLine"] += logic_total
            package_data[pkg_name]["summary"]["unitTestPassLine"] += covered

    # 計算每個 package 的 summary.coverage 與全域 summary
    for pkg_summary in package_data.values():
        s = pkg_summary["summary"]
        s["coverage"] = round((s["unitTestPassLine"] / s["fileLine"]) * 100, 2) if s["fileLine"] > 0 else 0.0
        total_file_lines += s["fileLine"]
        total_covered += s["unitTestPassLine"]

    overall = {
        "coverage": round((total_covered / total_file_lines) * 100, 2) if total_file_lines > 0 else 0.0,
        "fileLine": total_file_lines,
        "unitTestCoverLine": total_file_lines,
        "unitTestPassLine": total_covered
    }

    output = {
        "summary": overall,
        "packages": []
    }

    for pkg_name, pkg_data in sorted(package_data.items()):
        output["packages"].append({
            "package": pkg_name,
            "summary": pkg_data["summary"],
            "classes": pkg_data["classes"]
        })

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Structured package report saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Jacoco coverage.xml to structured package report")
    parser.add_argument("--input", required=True, help="Path to coverage.xml")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    args = parser.parse_args()

    generate_structured_report(args.input, args.output)