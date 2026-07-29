#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def save_bar(series: pd.Series, title: str, ylabel: str, output: Path) -> None:
    fig, ax = plt.subplots()
    series.plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def save_hist(values: pd.Series, title: str, xlabel: str, output: Path) -> None:
    fig, ax = plt.subplots()
    ax.hist(values.dropna(), bins=30)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Số quan sát")
    fig.tight_layout()
    fig.savefig(output, dpi=150)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.evidence_dir / "plots"
    out.mkdir(parents=True, exist_ok=True)

    classes = pd.read_csv(args.evidence_dir / "class-distribution.csv")
    class_series = classes.groupby("canonical_label")["record_count"].sum()
    save_bar(class_series, "Phân bố nhãn canonical", "Số record", out / "class-distribution.png")

    files = pd.read_csv(args.evidence_dir / "file-level-statistics.csv")
    save_hist(files["duration_s"], "Phân bố thời lượng file", "Thời lượng (giây)", out / "file-duration-distribution.png")

    channels = pd.read_csv(args.evidence_dir / "channel-level-statistics.csv")
    save_hist(channels["rms_uV"], "Phân bố RMS theo file/kênh", "RMS (µV)", out / "rms-distribution.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
