"""
Script to run Pylint and Coverage.
"""
import subprocess
import sys
import re

def run_command(command, description, capture_output=False):
    print(f"--- Running {description} ---")
    print(f"Command: {command}")
    try:
        # Run command
        if capture_output:
            process = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
            print(process.stdout)
            print(process.stderr)
        else:
            process = subprocess.run(command, shell=True, check=False)

        if process.returncode != 0:
            print(f"!!! {description} failed or found issues (Exit code: {process.returncode}) !!!")
            return False if not capture_output else (False, process.stdout)
        
        print(f"+++ {description} passed +++")
        return True if not capture_output else (True, process.stdout)
    except Exception as e:
        print(f"Error running {description}: {e}")
        return False if not capture_output else (False, "")

def main():
    # 1. Run Pylint
    print("\n=== 1. Linting (Pylint) ===")
    _, lint_output = run_command("pylint src tests", "Pylint", capture_output=True)
    
    # Parse Pylint score
    lint_score = 0.0
    if lint_output:
        # Match: Your code has been rated at 10.00/10
        score_match = re.search(r'rated at (\d+\.\d+)/10', lint_output)
        if score_match:
            lint_score = float(score_match.group(1))

    # 2. Run Coverage with Pytest
    print("\n=== 2. Testing & Coverage ===")
    # Create coverage html report in tests/htmlcov
    cov_cmd = "coverage run -m pytest && coverage report && coverage html -d tests/htmlcov"
    test_success, output = run_command(cov_cmd, "Pytest with Coverage", capture_output=True)
    
    # Extract percentage
    cov_percentage_val = 0
    if output:
        # Look for TOTAL ... 95%
        match = re.search(r'TOTAL\s+\d+\s+\d+\s+(\d+)%', output)
        if match:
            cov_percentage_val = int(match.group(1))

    # Strict Criteria Check
    lint_passed = lint_score >= 10.0
    cov_passed = cov_percentage_val == 100
    all_tests_passed = test_success # valid because pytest exit code 0 means passed

    # Summary
    print("\n=== Summary ===")
    
    # Linting
    if lint_passed:
        print(f"Linting:  PASSED ({lint_score}/10)")
    else:
        print(f"Linting:  FAIL   ({lint_score}/10)")

    # Tests
    if all_tests_passed:
        print("Tests:    PASSED")
    else:
        print("Tests:    FAIL")

    # Coverage
    if cov_passed:
        print(f"Coverage: PASSED ({cov_percentage_val}%)")
    else:
        print(f"Coverage: FAIL   ({cov_percentage_val}%)")
        
    # Final Exit Code
    if not (lint_passed and all_tests_passed and cov_passed):
        sys.exit(1)

if __name__ == "__main__":
    main()
