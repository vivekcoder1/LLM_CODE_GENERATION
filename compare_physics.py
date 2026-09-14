
import os
import subprocess
import sys
import csv
import numpy as np

from compute_l2_errors import compute_metrics, load_np

DOMAINS = ['burgers2d', 'heat_flow', 'julia_set', 'reaction_diffusion', 'structural_mechanics']
OUT_CSV = 'l2summary.csv'


def trajectory_specs(domain):
    if domain == 'reaction_diffusion':
        return [
            ('u', f'test_{domain}/reaction_diffusion_u_trj.npy', 'u_trj'),
            ('v', f'test_{domain}/reaction_diffusion_v_trj.npy', 'v_trj'),
        ]
    return [('', f'test_{domain}/{domain}_trj.npy', 'v_trj')]

def _to_numpy_state(value):
    """Convert a PhiFlow/PhiML state or ordinary array to a numeric NumPy array."""
    if hasattr(value, 'values'):
        value = value.values

    if isinstance(value, np.ndarray):
        array = value
    elif hasattr(value, 'numpy'):
        try:
            array = value.numpy()
        except TypeError:
            array = value.numpy(value.shape.names)
    else:
        array = np.asarray(value)

    if array.dtype == object:
        raise ValueError('trajectory contains an object or ragged state')
    if not np.issubdtype(array.dtype, np.number):
        raise ValueError(f'trajectory state is not numeric: dtype={array.dtype}')
    if array.size == 0:
        raise ValueError('trajectory state is empty')
    return np.asarray(array)


def normalize_trajectory(value):
    """Convert a ground-truth trajectory into a numeric ndarray."""
    if isinstance(value, (list, tuple)):
        if not value:
            raise ValueError('trajectory is empty')
        states = [_to_numpy_state(state) for state in value]
        try:
            return np.stack(states, axis=0)
        except ValueError as exc:
            raise ValueError(f'trajectory states have incompatible shapes: {exc}') from exc
    return _to_numpy_state(value)


def _nonfinite_summary(array):
    invalid = ~np.isfinite(array)
    indices = np.argwhere(invalid)
    first_index = tuple(int(index) for index in indices[0])
    timestep = first_index[0] if array.ndim > 0 else None
    return int(invalid.sum()), first_index, timestep


def align_trajectories(generated, ground_truth):
    """Align only the known initial-frame difference between generated and reference data."""
    generated = np.asarray(generated)
    ground_truth = np.asarray(ground_truth)
    if not np.all(np.isfinite(generated)):
        count, first_index, timestep = _nonfinite_summary(generated)
        raise ValueError(
            f'generated trajectory contains {count} NaN/infinite values; '
            f'first index={first_index}, timestep={timestep}'
        )
    if not np.all(np.isfinite(ground_truth)):
        count, first_index, timestep = _nonfinite_summary(ground_truth)
        raise ValueError(
            f'ground-truth trajectory contains {count} NaN/infinite values; '
            f'first index={first_index}, timestep={timestep}'
        )
    if generated.ndim == 0 or ground_truth.ndim == 0:
        raise ValueError(f'expected array trajectories, got {generated.shape} and {ground_truth.shape}')
    if generated.shape[1:] != ground_truth.shape[1:]:
        if generated.shape[0] == ground_truth.shape[-1] and generated.shape[1:] == ground_truth.shape[:-1]:
            print('Aligning ground-truth trajectory by moving its final time axis to the front.')
            ground_truth = np.moveaxis(ground_truth, -1, 0)
        else:
            raise ValueError(
                f'spatial shape mismatch: generated {generated.shape} vs ground-truth {ground_truth.shape}'
            )
    if generated.shape[1:] != ground_truth.shape[1:]:
        raise ValueError(
            f'spatial shape mismatch: generated {generated.shape} vs ground-truth {ground_truth.shape}'
        )
    if generated.shape[0] == ground_truth.shape[0] + 1:
        print('Aligning generated trajectory by dropping its initial frame.')
        generated = generated[1:]
    elif generated.shape[0] != ground_truth.shape[0]:
        raise ValueError(
            f'time length mismatch: generated {generated.shape} vs ground-truth {ground_truth.shape}'
        )
    return generated, ground_truth


def _is_missing_jax(error_text):
    lowered = error_text.lower()
    return 'modulenotfounderror' in lowered and ('jax' in lowered or 'jaxlib' in lowered)


def run_ground_truth(domains: list[str]):
    rows = []
    for d in domains:
        gt_script = os.path.join(f'test_{d}', f'{d}_ground_truth.py')
        if not os.path.exists(gt_script):
            print(f"[SKIP] ground-truth script missing for {d}: {gt_script}")
            continue

        for component, generated_name, variable_name in trajectory_specs(d):
            gen_npy = generated_name
            suffix = f'_{component}' if component else ''
            gt_out = os.path.join(f'test_{d}', f'{d}_ground_truth{suffix}_trj.npy')

            if not os.path.exists(gen_npy):
                print(f"[SKIP] generated trajectory missing for {d}{suffix}: {gen_npy}")
                continue

            cmd = """
import runpy
import sys
import numpy as np

namespace = runpy.run_path(sys.argv[1])
trajectory = namespace.get(sys.argv[3])
if trajectory is None:
    sys.exit(2)
trajectory = getattr(trajectory, 'values', trajectory)
if hasattr(trajectory, 'numpy'):
    dimension_names = getattr(getattr(trajectory, 'shape', None), 'names', None)
    trajectory = trajectory.numpy(tuple(dimension_names)) if dimension_names else trajectory.numpy()
else:
    trajectory = np.asarray(trajectory)
if trajectory.dtype == object:
    sys.exit(3)
np.save(sys.argv[2], trajectory)
"""
            print(f"Running ground-truth for {d}{suffix} -> {gt_out}")
            try:
                script_path = os.path.abspath(gt_script)
                output_path = os.path.abspath(gt_out)
                domain_dir = os.path.dirname(script_path)
                subprocess.run(
                    [sys.executable, '-c', cmd, script_path, output_path, variable_name],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=300,
                    cwd=domain_dir,
                )
            except subprocess.CalledProcessError as e:
                error_text = e.stderr.decode('utf-8', errors='ignore')
                if _is_missing_jax(error_text):
                    print(f"[SKIP] {d}{suffix}: JAX is not installed; install jax and jaxlib to compare this domain.")
                    continue
                print(f"Ground-truth execution failed for {d}{suffix}: exit {e.returncode}")
                print(error_text)
                continue
            except subprocess.TimeoutExpired:
                print(f"Ground-truth execution timed out for {d}{suffix}")
                continue

            try:
                gen = load_np(gen_npy)
                gt = normalize_trajectory(load_np(gt_out))
                np.save(gt_out, gt)
                gen, gt = align_trajectories(gen, gt)
            except Exception as e:
                print(f"[SKIP] {d}{suffix}: cannot compare trajectories: {e}")
                continue

            try:
                metrics = compute_metrics(gen, gt)
            except Exception as e:
                print(f"Metric computation failed for {d}{suffix}: {e}")
                continue

            mean_l2 = metrics['mean_l2']
            max_l2 = metrics['max_l2']
            rmse = metrics['rmse']
            label = f'{d}{suffix}'
            print(f"{label}: mean L2={mean_l2:.6g}, max L2={max_l2:.6g}, RMSE={rmse:.6g}")
            rows.append({'label': label, 'generated': gen_npy, 'ground_truth': gt_out, 'mean_l2': mean_l2, 'max_l2': max_l2, 'rmse': rmse})
    return rows


if __name__ == '__main__':
    rows = run_ground_truth(DOMAINS)
    keys = ['label','generated','ground_truth','mean_l2','max_l2','rmse']
    with open(OUT_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote summary to {OUT_CSV}")
