"""
Extract all metrics by parsing the JSONL task results directly from notebook outputs.
"""
import json
import re
import statistics
from pathlib import Path
from collections import defaultdict

NOTEBOOK_DIR = Path("notebook")
OUTPUT_FILE = Path("docs/extracted_metrics.md")

def extract_jsonl_results(nb_path):
    """Extract all JSON task results from notebook outputs."""
    with open(nb_path, 'r', encoding='utf-8') as f:
        nb = json.load(f)
    
    results = []
    all_text = ""
    
    for cell in nb.get('cells', []):
        for output in cell.get('outputs', []):
            if 'text' in output:
                for line in output['text']:
                    all_text += line
                    # Try to parse JSONL results
                    if line.strip().startswith('{') and 'task_id' in line:
                        try:
                            obj = json.loads(line.strip())
                            if 'task_id' in obj:
                                results.append(obj)
                        except:
                            pass
    
    return results, all_text

def compute_confidence_interval(successes, total, confidence=0.95):
    """Compute Wilson score confidence interval for binomial proportion."""
    import math
    if total == 0:
        return 0, 0
    p = successes / total
    z = 1.96  # 95% CI
    denominator = 1 + z**2 / total
    center = (p + z**2 / (2 * total)) / denominator
    spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * total)) / total) / denominator
    return max(0, center - spread), min(1, center + spread)

def analyze_results(results, all_text, nb_name):
    """Compute comprehensive metrics from task results."""
    m = {'name': nb_name}
    
    if not results:
        # Try to extract basic stats from text
        match = re.search(r"Passed:\s*(\d+)/(\d+)", all_text)
        if match:
            m['passed'] = int(match.group(1))
            m['total'] = int(match.group(2))
            m['pass_rate'] = m['passed'] / m['total'] * 100
        return m
    
    # Basic counts
    total = len(results)
    passed = sum(1 for r in results if r.get('test_passed', False))
    m['total'] = total
    m['passed'] = passed
    m['pass_rate'] = passed / total * 100 if total else 0
    
    # Pass@1 (same as pass_rate for k=1)
    m['pass_at_1'] = m['pass_rate']
    
    # 95% Confidence Interval
    ci_low, ci_high = compute_confidence_interval(passed, total)
    m['ci_95_lower'] = ci_low * 100
    m['ci_95_upper'] = ci_high * 100
    
    # Time metrics
    times = [r.get('elapsed_seconds', r.get('elapsed', 0)) for r in results if r.get('elapsed_seconds', r.get('elapsed', 0)) > 0]
    if times:
        m['total_time_sec'] = sum(times)
        m['avg_time_sec'] = statistics.mean(times)
        m['std_time_sec'] = statistics.stdev(times) if len(times) > 1 else 0
        m['median_time_sec'] = statistics.median(times)
        m['min_time_sec'] = min(times)
        m['max_time_sec'] = max(times)
    
    # API calls
    api_calls = [r.get('api_calls', 0) for r in results if r.get('api_calls', 0) > 0]
    if api_calls:
        m['total_api_calls'] = sum(api_calls)
        m['avg_api_calls'] = statistics.mean(api_calls)
    
    # Escalations
    escalations = [r.get('escalations', 0) for r in results]
    if any(e is not None for e in escalations):
        esc_counts = defaultdict(int)
        for e in escalations:
            if e is not None:
                esc_counts[e] += 1
        for e in [0, 1, 2]:
            m[f'escalation_{e}_count'] = esc_counts.get(e, 0)
        m['total_escalations'] = sum(e for e in escalations if e is not None and e > 0)
        
        # Escalation pass rates
        esc_passed = defaultdict(int)
        esc_total = defaultdict(int)
        for r in results:
            e = r.get('escalations', 0)
            if e is not None:
                esc_total[e] += 1
                if r.get('test_passed', False):
                    esc_passed[e] += 1
        for e in [0, 1, 2]:
            if esc_total[e] > 0:
                m[f'escalation_{e}_pass_rate'] = esc_passed[e] / esc_total[e] * 100
    
    # Developer Tier
    tiers = [r.get('developer_tier', r.get('tier', None)) for r in results]
    if any(t is not None for t in tiers):
        tier_counts = defaultdict(int)
        tier_passed = defaultdict(int)
        for r in results:
            t = r.get('developer_tier', r.get('tier', None))
            if t:
                tier_counts[t] += 1
                if r.get('test_passed', False):
                    tier_passed[t] += 1
        for t in ['S', 'M', 'L']:
            m[f'tier_{t}_count'] = tier_counts.get(t, 0)
            m[f'tier_{t}_pct'] = tier_counts.get(t, 0) / total * 100 if total else 0
            if tier_counts.get(t, 0) > 0:
                m[f'tier_{t}_pass_rate'] = tier_passed.get(t, 0) / tier_counts.get(t, 1) * 100
    
    # Story Points
    sps_initial = [r.get('story_points_initial', r.get('story_points', None)) for r in results]
    sps_final = [r.get('story_points_final', r.get('story_points', None)) for r in results]
    
    valid_initial = [sp for sp in sps_initial if sp is not None]
    valid_final = [sp for sp in sps_final if sp is not None]
    
    if valid_initial:
        m['avg_initial_sp'] = statistics.mean(valid_initial)
        sp_counts = defaultdict(int)
        sp_passed = defaultdict(int)
        for r in results:
            sp = r.get('story_points_initial', r.get('story_points', None))
            if sp:
                sp_counts[sp] += 1
                if r.get('test_passed', False):
                    sp_passed[sp] += 1
        for sp in [1, 2, 3, 5, 8]:
            m[f'sp_{sp}_count'] = sp_counts.get(sp, 0)
            m[f'sp_{sp}_pct'] = sp_counts.get(sp, 0) / total * 100 if total else 0
            if sp_counts.get(sp, 0) > 0:
                m[f'sp_{sp}_pass_rate'] = sp_passed.get(sp, 0) / sp_counts.get(sp, 1) * 100
    
    if valid_final:
        m['avg_final_sp'] = statistics.mean(valid_final)
    
    # Retries
    retries = [r.get('retry_count', r.get('retries', 0)) for r in results]
    if any(r > 0 for r in retries):
        m['total_retries'] = sum(retries)
        m['avg_retries'] = statistics.mean(retries)
    
    return m

def format_value(v, precision=2):
    if isinstance(v, float):
        return f"{v:.{precision}f}"
    return str(v)

def main():
    all_metrics = {}
    
    for nb_file in sorted(NOTEBOOK_DIR.glob("*.ipynb")):
        print(f"Processing {nb_file.name}...")
        results, all_text = extract_jsonl_results(nb_file)
        metrics = analyze_results(results, all_text, nb_file.stem)
        all_metrics[nb_file.stem] = metrics
        
        print(f"  Found {len(results)} results, {metrics.get('passed', 0)}/{metrics.get('total', 0)} passed")
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY OF ALL METRICS")
    print("="*80)
    
    for name, m in all_metrics.items():
        print(f"\n{name}:")
        for k, v in sorted(m.items()):
            if k != 'name':
                print(f"  {k}: {format_value(v)}")

if __name__ == "__main__":
    main()
