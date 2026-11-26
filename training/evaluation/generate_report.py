"""
Training Report Generator
==========================
Generates a comprehensive evaluation report from training results.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime


def generate_report(results_dir: str, output_file: str = None):
    """Generate a markdown report from training results."""
    results = Path(results_dir)
    
    # Collect available data
    report_lines = [
        "# Campus Signs Detection — Training & Evaluation Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## 1. Training Configuration",
        "",
    ]
    
    # Check for training args
    args_file = results / "args.yaml"
    if args_file.exists():
        report_lines.append("```yaml")
        with open(args_file, "r") as f:
            report_lines.append(f.read().strip())
        report_lines.append("```")
    else:
        report_lines.append("*Training arguments file not found.*")
    
    report_lines.extend(["", "## 2. Training Results", ""])
    
    # Check for results CSV
    results_csv = results / "results.csv"
    if results_csv.exists():
        import csv
        with open(results_csv, "r") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        if rows:
            last_row = rows[-1]
            report_lines.append("### Final Epoch Metrics")
            report_lines.append("")
            report_lines.append("| Metric | Value |")
            report_lines.append("|--------|-------|")
            
            for key, value in last_row.items():
                key = key.strip()
                try:
                    value = f"{float(value.strip()):.4f}"
                except (ValueError, AttributeError):
                    value = str(value).strip()
                report_lines.append(f"| {key} | {value} |")
    else:
        report_lines.append("*Results CSV not found.*")
    
    report_lines.extend(["", "## 3. Model Weights", ""])
    
    weights_dir = results / "weights"
    if weights_dir.exists():
        for weight_file in sorted(weights_dir.glob("*.pt")):
            size_mb = weight_file.stat().st_size / (1024 * 1024)
            report_lines.append(f"- **{weight_file.name}**: {size_mb:.1f} MB")
    else:
        report_lines.append("*No weights directory found.*")
    
    report_lines.extend(["", "## 4. Training Plots", ""])
    
    plot_files = [
        ("results.png", "Training curves (loss, mAP, precision, recall)"),
        ("confusion_matrix.png", "Confusion matrix"),
        ("confusion_matrix_normalized.png", "Normalized confusion matrix"),
        ("P_curve.png", "Precision curve"),
        ("R_curve.png", "Recall curve"),
        ("PR_curve.png", "Precision-Recall curve"),
        ("F1_curve.png", "F1 curve"),
    ]
    
    for plot_name, description in plot_files:
        plot_path = results / plot_name
        if plot_path.exists():
            report_lines.append(f"### {description}")
            report_lines.append(f"![{description}]({plot_path})")
            report_lines.append("")
    
    report_lines.extend([
        "## 5. Usage",
        "",
        "```python",
        "from ultralytics import YOLO",
        "",
        "# Load trained model",
        "model = YOLO('models/custom/best.pt')",
        "",
        "# Run inference",
        "results = model.predict('path/to/image.jpg', conf=0.25)",
        "",
        "# Process results",
        "for result in results:",
        "    for box in result.boxes:",
        "        class_id = int(box.cls[0])",
        "        confidence = float(box.conf[0])",
        "        bbox = box.xyxy[0].tolist()",
        "        print(f'Class: {class_id}, Confidence: {confidence:.2f}')",
        "```",
        "",
        "## 6. Classes",
        "",
        "| ID | Class | Description |",
        "|----|-------|-------------|",
        "| 0 | directional_sign | Signs with arrows indicating directions |",
        "| 1 | department_sign | Department, room, office labels |",
        "| 2 | safety_sign | Warning and hazard symbols |",
        "| 3 | exit_sign | Emergency exit signs |",
        "| 4 | information_sign | Information boards, notice boards |",
        "",
    ])
    
    # Write report
    report_text = "\n".join(report_lines)
    
    if output_file:
        output = Path(output_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w") as f:
            f.write(report_text)
        print(f"Report saved to: {output}")
    else:
        print(report_text)
    
    return report_text


def main():
    parser = argparse.ArgumentParser(description="Generate training evaluation report")
    parser.add_argument("--results", required=True, help="Path to training results directory")
    parser.add_argument("--output", default=None, help="Output markdown file path")
    
    args = parser.parse_args()
    generate_report(args.results, args.output)


if __name__ == "__main__":
    main()

