import subprocess
import sys
from pathlib import Path
from typing import List, Tuple

BASE_DIR = Path("D:/Vivek/research")
TEST_DIRS = [
    "burgers2d", "heat_flow", "julia_set", "lid_driven_cavity",
    "reaction_diffusion", "smoke_plume", "structural_mechanics", "wake_flow"
]


def run_generated_script(script_path: Path, timeout: int = 60) -> Tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            timeout=timeout,
            text=True,
            cwd=script_path.parent
        )

        if result.returncode == 0:
            return True, f" Executed successfully. Output: {result.stdout}"
        else:
            error_msg = result.stderr or result.stdout
            return False, f"✗ Exit code {result.returncode}. Error: {error_msg}"

    except subprocess.TimeoutExpired:
        return False, f"✗ Timeout after {timeout} seconds"
    except Exception as e:
        return False, f"✗ Exception: {str(e)[:300]}"


def main():
    print("\n" + "=" * 80)
    print(" GENERATED SIMULATION SCRIPT VALIDATION")
    print("=" * 80 + "\n")

    results = []

    for folder_name in TEST_DIRS:
        test_dir = BASE_DIR / f"test_{folder_name}"
        script_path = test_dir / f"generated_{folder_name}_simulation.py"

        if not script_path.exists():
            print(f"[{folder_name.upper():20}] ✗ MISSING: {script_path}")
            results.append((folder_name, False, "Script file not found"))
            continue

        print(f"[{folder_name.upper():20}] Running...", end=" ", flush=True)
        success, message = run_generated_script(script_path, timeout=60)
        print(message)
        results.append((folder_name, success, message))

    print("\n" + "=" * 80)
    print(" SUMMARY")
    print("=" * 80 + "\n")

    passed = sum(1 for _, success, _ in results if success)
    total = len(results)

    for folder_name, success, message in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status:8} | {folder_name:25}")

    print(f"\n  Passed: {passed}/{total}")

    if passed == total:
        print("\n All generated scripts are executable!\n")
        return 0
    else:
        print(f"\n{total - passed} script(s) failed or are missing.\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
