#!/usr/bin/env python3
"""Recalculate the report's scenarios; no network access or paid inference.

All benefit, labor, workload and loss values are assumptions, not measurements.
Run from any directory with Python 3.10+; output files sit beside this script.
"""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent
PRICE_PER_MILLION = 0.042
ENGINEER_HOURLY = 100
REVIEWER_HOURLY = 50
VOLUMES = (100, 1000, 10000)
FOUNDATION_COST = 44 * ENGINEER_HOURLY + 24 * REVIEWER_HOURLY
FOUNDATION_MONTHLY = 2 * ENGINEER_HOURLY

# id, name, input tokens/model, requests/model, engineering h low/high,
# labeling h low/high, maintenance h/month, gross avoided cost/model,
# introduced-error allowance/model, extra generation cost/model,
# other setup dollars, other monthly dollars, fixed monthly input tokens.
ROWS = [
    ("U1", "Part selection", 240000, 12, (24, 48), (8, 16), 1, .10, .01, 0, 0, 0, 0),
    ("U2", "Assembly selection", 150000, 4, (48, 96), (16, 32), 2, .40, .01, 0, 0, 0, 0),
    ("U3", "Brief and handler selection", 6000, 1, (24, 48), (4, 8), .5, .06, .01, 0, 0, 0, 0),
    ("U4", "Brief coverage verification", 18000, 2, (24, 48), (8, 16), 1, .20, .01, 0, 0, 0, 0),
    ("U5", "Context selection", 36000, 4, (16, 32), (4, 8), .5, .02, .01, 0, 0, 0, 0),
    ("U6", "Generator escalation", 18000, 3, (64, 120), (16, 32), 3, .60, .05, 0, 0, 0, 0),
    ("U7", "Repair routing", 600, .1, (24, 48), (8, 16), 1, .08, .01, 0, 0, 0, 0),
    ("U8", "Alternative design selection", 30000, 3, (32, 64), (16, 32), 2, .50, .01, 1, 0, 0, 0),
    ("U9", "Offline semantic annotations", 0, 0, (32, 64), (16, 32), 1, .03, .01, 0, .84, 0, 2000000),
    ("U10", "Learned preference model", 6000, 1, (80, 160), (40, 100), 4, .15, .025, 0, 52.52, 10, 0),
    ("U11", "Delivery claim verification", 5000, 1, (16, 32), (4, 8), .5, .01, .005, 0, 0, 0, 0),
]


def calculate():
    results = []
    for (key, name, tokens, requests, eng, labels, maint, benefit, loss,
         extra, setup_other, monthly_other, fixed_tokens) in ROWS:
        api = tokens / 1e6 * PRICE_PER_MILLION
        fixed_api = fixed_tokens / 1e6 * PRICE_PER_MILLION
        upfront = sum(eng) / 2 * ENGINEER_HOURLY + sum(labels) / 2 * REVIEWER_HOURLY + setup_other
        monthly = maint * ENGINEER_HOURLY + monthly_other + fixed_api
        margin = benefit - loss - extra - api
        all_upfront = upfront + FOUNDATION_COST
        all_monthly = monthly + FOUNDATION_MONTHLY
        threshold = (all_upfront / 12 + all_monthly) / margin if margin > 0 else None
        result = dict(id=key, name=name, tokens_per_model=tokens,
                      requests_per_model=requests, engineering_hours=eng,
                      labeling_hours=labels, maintenance_hours_monthly=maint,
                      gross_avoided_cost_per_model=benefit,
                      introduced_error_allowance_per_model=loss,
                      extra_generation_cost_per_model=extra,
                      other_setup_cost=setup_other, other_monthly_cost=monthly_other,
                      fixed_monthly_input_tokens=fixed_tokens,
                      api_per_model=api, fixed_api_monthly=fixed_api,
                      incremental_setup_cost=upfront,
                      incremental_monthly_cost=monthly,
                      marginal_benefit_per_model=margin,
                      standalone_break_even_models_monthly_12mo=threshold,
                      volumes={})
        for volume in VOLUMES:
            net = volume * margin - all_monthly
            result['volumes'][volume] = dict(
                api_monthly=volume * api + fixed_api,
                standalone_net_monthly_before_setup=net,
                standalone_net_year_one=12 * net - all_upfront,
                standalone_payback_months=all_upfront / net if net > 0 else None,
            )
        results.append(result)
    return results


if __name__ == '__main__':
    results = calculate()
    data = dict(scenario='illustrative, unmeasured benefits; cold cache; no retry allowance',
                price_per_million_input=PRICE_PER_MILLION,
                engineer_hourly=ENGINEER_HOURLY, reviewer_hourly=REVIEWER_HOURLY,
                foundation_cost=FOUNDATION_COST,
                foundation_monthly=FOUNDATION_MONTHLY, use_cases=results)
    (ROOT / 'typesafe-jev-costs.json').write_text(json.dumps(data, indent=2) + '\n')
    with (ROOT / 'typesafe-jev-costs.csv').open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['id', 'name', 'models_monthly', 'api_monthly_usd',
                         'standalone_net_monthly_before_setup_usd',
                         'standalone_net_year_one_usd', 'payback_months'])
        for row in results:
            for volume, values in row['volumes'].items():
                writer.writerow([row['id'], row['name'], volume,
                                 *[round(values[key], 6) if values[key] is not None else ''
                                   for key in ('api_monthly', 'standalone_net_monthly_before_setup',
                                               'standalone_net_year_one', 'standalone_payback_months')]])
    for row in results:
        monthly = ' / '.join(f"${row['volumes'][n]['api_monthly']:.3f}" for n in VOLUMES)
        threshold = row['standalone_break_even_models_monthly_12mo']
        threshold_text = f'{threshold:,.0f}' if threshold is not None else 'never in this scenario'
        print(f"{row['id']} | {monthly} | setup ${row['incremental_setup_cost']:,.0f} | "
              f"margin ${row['marginal_benefit_per_model']:.5f} | break even {threshold_text}")
