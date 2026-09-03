
import os
import subprocess
import sys
import csv
import time
import runpy
import numpy as np

from compute_l2_errors import compute_metrics, load_np

DOMAINS = ['burgers2d', 'heat_flow', 'julia_set']
OUT_CSV = 'l2_three_summary.csv'

rows = []
for d in DOMAINS:
    gen_npy = os.path.join(f'test_{d}', f'{d}_velocity_trj.npy')
    gt_script = os.path.join(f'test_{d}', f'{d}_ground_truth.py')
    gt_out = os.path.join(f'test_{d}', f'{d}_ground_truth_velocity_trj.npy')

    if not os.path.exists(gen_npy):
        print(f"[SKIP] generated trajectory missing for {d}: {gen_npy}")
        continue
    if not os.path.exists(gt_script):
        print(f"[SKIP] ground-truth script missing for {d}: {gt_script}")
        continue

    cmd = (
        "import runpy, numpy as np, sys; ns=runpy.run_path(r'" + gt_script.replace('\\', '\\\\') + "');\n"
        "v = ns.get('v_trj', None);\n"
        "if v is None:\n"
        "    sys.exit(2)\n"
        "np.save(r'" + gt_out.replace('\\', '\\\\') + "', v)"
    )
    print(f"Running ground-truth for {d} -> {gt_out}")
    try:
        subprocess.run([sys.executable, '-c', cmd], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    except subprocess.CalledProcessError as e:
        print(f"Ground-truth execution failed for {d}: exit {e.returncode}")
        print(e.stderr.decode('utf-8', errors='ignore'))
        continue
    except subprocess.TimeoutExpired:
        print(f"Ground-truth execution timed out for {d}")
        continue

    try:
        gen = load_np(gen_npy)
        gt = load_np(gt_out)
    except Exception as e:
        print(f"Failed loading arrays for {d}: {e}")
        continue

    try:
        metrics = compute_metrics(gen, gt)
    except Exception as e:
        print(f"Metric computation failed for {d}: {e}")
        continue

    mean_l2 = metrics['mean_l2']
    max_l2 = metrics['max_l2']
    rmse = metrics['rmse']
    print(f"{d}: mean L2={mean_l2:.6g}, max L2={max_l2:.6g}, RMSE={rmse:.6g}")
    rows.append({'label': d, 'generated': gen_npy, 'ground_truth': gt_out, 'mean_l2': mean_l2, 'max_l2': max_l2, 'rmse': rmse})

# write summary
keys = ['label','generated','ground_truth','mean_l2','max_l2','rmse']
with open(OUT_CSV, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=keys)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Wrote summary to {OUT_CSV}")
