"""Visualization module - generates plots and saves to outputs folder."""

from typing import Any, Dict, Mapping
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from config import (
    FIGURE_WIDTH, FIGURE_HEIGHT, FIGURE_DPI, PLOT_STYLE,
    PLOT_ALLOCATION, PLOT_RUNWAY, PLOT_RISK_SCORES, PLOT_POST_CRASH, PLOT_CONCENTRATION,
)
from utils import ensure_output_dir, log_success, format_inr


def plot_asset_allocation(
    portfolio: Mapping[str, Any],
    output_dir: str,
) -> str:
    """
    Create pie chart of asset allocation.
    
    Returns path to saved plot.
    """
    output_path = ensure_output_dir(output_dir)
    
    assets = portfolio.get("assets", [])
    names = [asset["name"] for asset in assets]
    allocations = [float(asset["allocation_pct"]) for asset in assets]
    total_value = float(portfolio["total_value_inr"])
    
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=FIGURE_DPI)
    colors = plt.cm.Set3(range(len(names)))
    
    wedges, texts, autotexts = ax.pie(
        allocations,
        labels=names,
        autopct='%1.1f%%',
        colors=colors,
        startangle=90,
        textprops={'fontsize': 11, 'weight': 'bold'},
    )
    
    # Add values in INR as legend
    legend_labels = [
        f"{name}: {format_inr(total_value * pct / 100)}"
        for name, pct in zip(names, allocations)
    ]
    ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
    
    ax.set_title(f"Portfolio Asset Allocation\nTotal Value: {format_inr(total_value)}", 
                 fontsize=14, weight='bold', pad=20)
    
    plt.tight_layout()
    plot_file = output_path / PLOT_ALLOCATION
    plt.savefig(plot_file, dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    
    log_success(f"Asset allocation plot saved: {plot_file}")
    return str(plot_file)


def plot_runway_comparison(
    scenarios: Dict[str, Dict[str, Any]],
    output_dir: str,
) -> str:
    """
    Create bar chart comparing runway across current/moderate/severe scenarios.
    
    Returns path to saved plot.
    """
    output_path = ensure_output_dir(output_dir)
    
    scenario_names = []
    runway_values = []
    colors_list = []
    
    for scenario_name in ["current", "moderate", "severe"]:
        if scenario_name in scenarios:
            scenario = scenarios[scenario_name]
            runway = scenario.get("runway_months", 0)
            ruin_test = scenario.get("ruin_test", "FAIL")
            
            scenario_names.append(scenario_name.capitalize())
            runway_values.append(min(runway, 60))  # Cap at 60 for visibility
            
            # Color based on PASS/FAIL
            if ruin_test == "PASS":
                colors_list.append("#2ecc71")  # Green
            else:
                colors_list.append("#e74c3c")  # Red
    
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=FIGURE_DPI)
    
    bars = ax.bar(scenario_names, runway_values, color=colors_list, edgecolor='black', linewidth=1.5)
    
    # Add threshold line
    ax.axhline(y=12, color='orange', linestyle='--', linewidth=2, label='Safety Threshold (12 months)')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}mo',
                ha='center', va='bottom', fontsize=11, weight='bold')
    
    ax.set_ylabel('Runway (Months)', fontsize=12, weight='bold')
    ax.set_title('Portfolio Runway Across Scenarios', fontsize=14, weight='bold', pad=20)
    ax.set_ylim(0, max(runway_values + [12]) * 1.15)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plot_file = output_path / PLOT_RUNWAY
    plt.savefig(plot_file, dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    
    log_success(f"Runway comparison plot saved: {plot_file}")
    return str(plot_file)


def plot_risk_scores(
    risk_scores: list,
    output_dir: str,
) -> str:
    """
    Create scatter plot of asset risk scores (allocation vs crash severity).
    
    Returns path to saved plot.
    """
    output_path = ensure_output_dir(output_dir)
    
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=FIGURE_DPI)
    
    names = [rs["name"] for rs in risk_scores]
    allocations = [rs["allocation_pct"] for rs in risk_scores]
    crashes = [rs["crash_pct"] for rs in risk_scores]
    risk_scores_values = [rs["risk_score"] for rs in risk_scores]
    
    # Normalize risk scores for bubble size
    max_risk = max(risk_scores_values) if risk_scores_values else 1
    sizes = [100 + (rs / max_risk * 500) for rs in risk_scores_values]
    
    colors = plt.cm.RdYlGn_r([(s - min(sizes)) / (max(sizes) - min(sizes)) for s in sizes])
    
    scatter = ax.scatter(allocations, crashes, s=sizes, c=colors, alpha=0.6, edgecolors='black', linewidth=1.5)
    
    # Annotate each point with asset name
    for i, name in enumerate(names):
        ax.annotate(name, (allocations[i], crashes[i]), 
                   fontsize=10, weight='bold', ha='center', va='center')
    
    ax.set_xlabel('Allocation (%)', fontsize=12, weight='bold')
    ax.set_ylabel('Expected Crash Severity (%)', fontsize=12, weight='bold')
    ax.set_title('Asset Risk Scores\n(Bubble size = Risk Score)', fontsize=14, weight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_file = output_path / PLOT_RISK_SCORES
    plt.savefig(plot_file, dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    
    log_success(f"Risk scores plot saved: {plot_file}")
    return str(plot_file)


def plot_post_crash_value(
    portfolio: Mapping[str, Any],
    scenarios: Dict[str, Dict[str, Any]],
    output_dir: str,
) -> str:
    """
    Create bar chart comparing post-crash values across scenarios.
    
    Returns path to saved plot.
    """
    output_path = ensure_output_dir(output_dir)
    
    scenario_names = []
    values = []
    colors_list = []
    
    total_value = float(portfolio["total_value_inr"])
    
    for scenario_name in ["current", "moderate", "severe"]:
        if scenario_name in scenarios:
            scenario = scenarios[scenario_name]
            post_crash_val = scenario.get("post_crash_value", 0)
            
            scenario_names.append(scenario_name.capitalize())
            values.append(post_crash_val)
            
            # Color based on value preservation
            if post_crash_val / total_value >= 0.8:
                colors_list.append("#2ecc71")  # Green
            elif post_crash_val / total_value >= 0.5:
                colors_list.append("#f39c12")  # Orange
            else:
                colors_list.append("#e74c3c")  # Red
    
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=FIGURE_DPI)
    
    bars = ax.bar(scenario_names, values, color=colors_list, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        pct = (height / total_value) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{format_inr(height)}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=10, weight='bold')
    
    ax.set_ylabel('Portfolio Value (INR)', fontsize=12, weight='bold')
    ax.set_title('Post-Crash Portfolio Value by Scenario', fontsize=14, weight='bold', pad=20)
    ax.set_ylim(0, max(values) * 1.2)
    ax.grid(axis='y', alpha=0.3)
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_inr(x)))
    
    plt.tight_layout()
    plot_file = output_path / PLOT_POST_CRASH
    plt.savefig(plot_file, dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    
    log_success(f"Post-crash value plot saved: {plot_file}")
    return str(plot_file)


def plot_concentration_risk(
    portfolio: Mapping[str, Any],
    concentration_warning: bool,
    output_dir: str,
) -> str:
    """
    Create bar chart showing concentration risk for each asset.
    
    Returns path to saved plot.
    """
    output_path = ensure_output_dir(output_dir)
    
    assets = portfolio.get("assets", [])
    names = [asset["name"] for asset in assets]
    allocations = [float(asset["allocation_pct"]) for asset in assets]
    
    # Color code: warn if >40%
    colors_list = ['#e74c3c' if alloc > 40 else '#3498db' for alloc in allocations]
    
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH, FIGURE_HEIGHT), dpi=FIGURE_DPI)
    
    bars = ax.barh(names, allocations, color=colors_list, edgecolor='black', linewidth=1.5)
    
    # Add threshold line
    ax.axvline(x=40, color='red', linestyle='--', linewidth=2, label='Concentration Threshold (40%)')
    
    # Add value labels
    for i, (bar, alloc) in enumerate(zip(bars, allocations)):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2.,
                f'{alloc:.1f}%',
                ha='left', va='center', fontsize=11, weight='bold')
    
    ax.set_xlabel('Allocation (%)', fontsize=12, weight='bold')
    ax.set_title('Asset Concentration Risk Analysis', fontsize=14, weight='bold', pad=20)
    ax.set_xlim(0, max(allocations) * 1.15)
    ax.legend(fontsize=10, loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    
    # Add warning if needed
    if concentration_warning:
        fig.text(0.5, 0.02, '⚠ WARNING: Concentration detected (>40% in single asset)', 
                ha='center', fontsize=11, weight='bold', color='red',
                bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    
    plt.tight_layout()
    plot_file = output_path / PLOT_CONCENTRATION
    plt.savefig(plot_file, dpi=FIGURE_DPI, bbox_inches='tight')
    plt.close()
    
    log_success(f"Concentration risk plot saved: {plot_file}")
    return str(plot_file)


def generate_all_plots(
    portfolio: Mapping[str, Any],
    scenarios: Dict[str, Dict[str, Any]],
    risk_scores: list,
    concentration_warning: bool,
    output_dir: str,
) -> Dict[str, str]:
    """
    Generate all 5 plots and return paths.
    
    Returns dict mapping plot names to file paths.
    """
    plots = {}
    
    plots["allocation"] = plot_asset_allocation(portfolio, output_dir)
    plots["runway"] = plot_runway_comparison(scenarios, output_dir)
    plots["risk_scores"] = plot_risk_scores(risk_scores, output_dir)
    plots["post_crash"] = plot_post_crash_value(portfolio, scenarios, output_dir)
    plots["concentration"] = plot_concentration_risk(portfolio, concentration_warning, output_dir)
    
    return plots
