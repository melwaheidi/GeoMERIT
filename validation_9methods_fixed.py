"""
Validation Module - 9 Methods (Fixed for Long Format Data)
===========================================================

Statistical validation of the geophysical method selection framework
using Spearman ρ, Kendall τ, and Kendall's W.
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple

def calculate_kendalls_w(rankings: np.ndarray) -> Tuple[float, float]:
    """Calculate Kendall's W coefficient of concordance."""
    n_raters, n_items = rankings.shape
    rank_sums = np.sum(rankings, axis=0)
    mean_rank_sum = np.mean(rank_sums)
    S = np.sum((rank_sums - mean_rank_sum) ** 2)
    S_max = (n_raters ** 2) * (n_items ** 3 - n_items) / 12
    W = S / S_max
    chi_square = n_raters * (n_items - 1) * W
    df = n_items - 1
    p_value = 1 - stats.chi2.cdf(chi_square, df)
    return W, p_value

def validate_framework(expert_file: str, framework_file: str) -> pd.DataFrame:
    """Validate framework rankings against expert consensus."""
    
    # Load data (long format)
    expert_df = pd.read_csv(expert_file)
    framework_df = pd.read_csv(framework_file)
    
    scenarios = expert_df['Scenario'].unique()
    results = []
    
    for scenario in scenarios:
        # Get expert rankings for this scenario
        expert_scenario = expert_df[expert_df['Scenario'] == scenario]
        
        # Pivot to wide format: rows = experts, columns = methods
        expert_wide = expert_scenario.pivot(index='Expert', columns='Method', values='Rank')
        expert_rankings = expert_wide.values.astype(float)
        
        n_experts, n_methods = expert_rankings.shape
        
        # Calculate Kendall's W (inter-expert agreement)
        W, W_pvalue = calculate_kendalls_w(expert_rankings)
        
        # Calculate mean expert ranking
        mean_expert_ranks = expert_rankings.mean(axis=0)
        
        # Get framework rankings (wide format)
        framework_scenario = framework_df[framework_df['Scenario'] == scenario]
        
        # Get method names in same order as expert data
        methods = expert_wide.columns.tolist()
        framework_ranks = framework_scenario[methods].values.flatten().astype(float)
        
        # Calculate Spearman correlation
        spearman_rho, spearman_p = stats.spearmanr(mean_expert_ranks, framework_ranks)
        
        # Calculate Kendall tau
        kendall_tau, kendall_p = stats.kendalltau(mean_expert_ranks, framework_ranks)
        
        # Calculate confidence interval for Spearman
        z = np.arctanh(spearman_rho)
        se = 1 / np.sqrt(n_methods - 3)
        ci_lower = np.tanh(z - 1.96 * se)
        ci_upper = np.tanh(z + 1.96 * se)
        
        # Calculate statistical power
        effect_size = abs(spearman_rho)
        power = stats.norm.cdf(effect_size * np.sqrt(n_methods - 3) - 1.96)
        
        # Calculate expert ranking variance
        rank_variance = np.var(expert_rankings, axis=0)
        mean_variance = np.mean(rank_variance)
        
        results.append({
            'Scenario': scenario,
            'Spearman_rho': spearman_rho,
            'Spearman_p': spearman_p,
            'CI_lower': ci_lower,
            'CI_upper': ci_upper,
            'Kendall_tau': kendall_tau,
            'Kendall_p': kendall_p,
            'Kendalls_W': W,
            'W_pvalue': W_pvalue,
            'Power': power,
            'Mean_Variance': mean_variance,
            'N_Experts': n_experts,
            'N_Methods': n_methods
        })
    
    return pd.DataFrame(results)

if __name__ == "__main__":
    print("=" * 70)
    print("VALIDATION RESULTS - 9 METHODS")
    print("=" * 70)
    
    results = validate_framework(
        'actual_expert_rankings_9methods.csv',
        'framework_rankings_9methods.csv'
    )
    
    print(results.to_string(index=False))
    print("=" * 70)
    
    results.to_csv('validation_results_9methods.csv', index=False)
    print("\n✓ Results saved to validation_results_9methods.csv")
