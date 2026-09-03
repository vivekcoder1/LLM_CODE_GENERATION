#!/usr/bin/env python3
"""
Compute per-timestep L2 errors and overall RMSE between generated and ground-truth .npy trajectories.
Usage examples:
  python compute_l2_errors.py --pairs-file pairs.csv
  python compute_l2_errors.py --pair burgers2d:./test_burgers2d/generated_burgers2d_simulation.npy:./test_burgers2d/burgers2d_velocity_trj.npy

Pairs CSV format (header): label,generated,ground_truth
"""
import argparse
import csv
import math
import os
import sys
from typing import List, Dict
import numpy as np
import subprocess
import time
import runpy


def compute_metrics(gen: np.ndarray, gt: np.ndarray) -> Dict:
    if gen.shape != gt.shape:
        raise ValueError(f"Shape mismatch: generated {gen.shape} vs ground-truth {gt.shape}")

    # If first axis is time-like (T, ...), compute per-timestep L2
    if gen.ndim >= 1 and gen.shape[0] > 1:
        T = gen.shape[0]
        per_t = []
        for t in range(T):
            diff = gen[t].astype(float) - gt[t].astype(float)
            l2 = float(np.linalg.norm(diff.ravel()))
            per_t.append(l2)
        per_t = np.array(per_t)
        mse = float(np.mean(per_t**2))
        rmse = math.sqrt(mse)
        return {
            'per_t': per_t.tolist(),
            'mean_l2': float(per_t.mean()),
            'max_l2': float(per_t.max()),
            'rmse': rmse
        }
    else:
        diff = gen.astype(float) - gt.astype(float)
        l2 = float(np.linalg.norm(diff.ravel()))
        rmse = l2 / math.sqrt(diff.size)
        return {
            'per_t': [l2],
            'mean_l2': l2,
            'max_l2': l2,
            'rmse': rmse
        }


def load_np(path: str) -> np.ndarray:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    try:
        return np.load(path, allow_pickle=False)
    except ValueError as e:
        msg = str(e).lower()
        if 'object arrays cannot be loaded' in msg or 'allow_pickle' in msg:
            # Retry with allow_pickle=True for object arrays saved with pickle
            print(f"Warning: loading object array from {path} with allow_pickle=True")
            # Only do this for trusted files
            return np.load(path, allow_pickle=True)
        raise


def parse_pairs_file(path: str) -> List[Dict[str,str]]:
    pairs = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            pairs.append({'label': row['label'], 'generated': row['generated'], 'ground_truth': row['ground_truth']})
    return pairs


def main(argv=None):
    parser = argparse.ArgumentParser(description='Compute L2 errors between generated and ground-truth .npy trajectories')
    parser.add_argument('--pairs-file', type=str, help='CSV file with columns: label,generated,ground_truth')
    parser.add_argument('--pair', action='append', help='Pair as label:generated_path:ground_truth_path (can pass multiple)')
    parser.add_argument('--out-csv', type=str, default='l2_results.csv', help='CSV output for summary')
    parser.add_argument('--run-and-compare', action='store_true', help='Run built-in generated and ground-truth scripts for the default domains and compare')
    args = parser.parse_args(argv)

    pairs = []
    if args.pairs_file:
        pairs.extend(parse_pairs_file(args.pairs_file))
    if args.pair:
        for p in args.pair:
            try:
                label, gen, gt = p.split(':', 2)
            except ValueError:
                print('Invalid --pair format; expected label:gen:gt', file=sys.stderr)
                sys.exit(2)
            pairs.append({'label': label, 'generated': gen, 'ground_truth': gt})

    if not pairs:
        # If no explicit pairs given, allow running built-in domains
        default_domains = ['burgers2d', 'heat_flow', 'julia_set', 'reaction_diffusion']
        if args.run_and_compare:
            pairs = []
            for d in default_domains:
                gen_npy = os.path.join('test_' + d, f'{d}_velocity_trj.npy')
                gt_script = os.path.join('test_' + d, f'{d}_ground_truth.py')
                pairs.append({'label': d, 'generated': gen_npy, 'ground_truth_script': gt_script})
        else:
            print('No pairs provided. Use --pairs-file or --pair, or enable --run-and-compare', file=sys.stderr)
            sys.exit(2)

    rows = []
    for entry in pairs:
        label = entry['label']
        gt_path = None
        if 'ground_truth_script' in entry:
                # Run the ground-truth script in a subprocess that captures v_trj and saves to a temp file
                gt_script = entry['ground_truth_script']
                gt_out = os.path.join(os.path.dirname(gt_script) or '.', f"{label}_ground_truth_velocity_trj.npy")
                cmd = (
                    "import runpy, numpy as np, sys; ns=runpy.run_path(r'" + gt_script.replace("\\", "\\\\") + "');\n"
                    "v = ns.get('v_trj', None);\n"
                    "if v is None:\n\n"
                    "    sys.exit(2)\n"
                    "np.save(r'" + gt_out.replace("\\", "\\\\") + "', v)"
                )
        print(f"Running ground-truth script for {label} and saving v_trj -> {gt_out}")
        try:
            subprocess.run([sys.executable, '-c', cmd], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
        except subprocess.CalledProcessError as e:
            print(f"Ground-truth execution failed for {label}: exit {e.returncode}")
            print(e.stderr.decode('utf-8', errors='ignore'))
            continue
        except subprocess.TimeoutExpired:
            print(f"Ground-truth execution timed out for {label}")
            continue
        gt_path = gt_out

        gen_path = entry.get('generated')
        if not gen_path or not os.path.exists(gen_path):
            print(f"Generated trajectory not found for {label}: expected {gen_path}")
            continue
        print(f"Processing {label}: generated={gen_path}, ground_truth={gt_path}")
        gen = load_np(gen_path)
        if gt_path:
            gt = load_np(gt_path)
        else:
            print(f"No ground-truth path available for {label}")
            continue

        metrics = compute_metrics(gen, gt)
        mean_l2 = metrics['mean_l2']
        max_l2 = metrics['max_l2']
        rmse = metrics['rmse']
        rows.append({'label': label, 'generated': gen_path, 'ground_truth': gt_path, 'mean_l2': mean_l2, 'max_l2': max_l2, 'rmse': rmse})
        print(f"  mean L2: {mean_l2:.6g}, max L2: {max_l2:.6g}, RMSE: {rmse:.6g}")

    # write summary CSV
    keys = ['label','generated','ground_truth','mean_l2','max_l2','rmse']
    with open(args.out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote summary to {args.out_csv}")

if __name__ == '__main__':
    main()
