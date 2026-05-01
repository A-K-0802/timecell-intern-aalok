"""Main entry point for Task4 Portfolio Visualizer."""

import argparse
import sys
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from config import DEFAULT_TONE, DEFAULT_OUTPUT_DIR
from input_loader import load_portfolio
from risk_analysis import compute_risk_metrics, compute_all_scenarios, get_asset_risk_scores
from visualizer import generate_all_plots
from ai_advisor import get_ai_advice
from utils import (
    ensure_output_dir,
    log_info,
    log_success,
    log_warning,
    log_error,
    format_inr,
    format_percentage,
    get_plot_path,
)

console = Console()


def print_portfolio_summary(portfolio: dict) -> None:
    """Print portfolio summary in a formatted table."""
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]PORTFOLIO SUMMARY[/bold cyan]")
    console.print("=" * 70)
    
    total_value = float(portfolio["total_value_inr"])
    monthly_expenses = float(portfolio["monthly_expenses_inr"])
    
    summary_data = [
        ["Total Portfolio Value", format_inr(total_value)],
        ["Monthly Expenses", format_inr(monthly_expenses)],
        ["Number of Assets", str(len(portfolio.get("assets", [])))],
    ]
    
    table = Table(title="Portfolio Details", show_header=False, show_footer=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    for metric, value in summary_data:
        table.add_row(metric, value)
    
    console.print(table)


def print_asset_details(portfolio: dict) -> None:
    """Print asset allocation details."""
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]ASSET ALLOCATION[/bold cyan]")
    console.print("=" * 70)
    
    assets = portfolio.get("assets", [])
    total_value = float(portfolio["total_value_inr"])
    
    table = Table(title="Assets", show_header=True)
    table.add_column("Asset", style="cyan")
    table.add_column("Allocation %", style="yellow")
    table.add_column("Value (INR)", style="green")
    table.add_column("Crash Scenario %", style="red")
    
    for asset in assets:
        name = asset["name"]
        alloc_pct = float(asset["allocation_pct"])
        crash_pct = float(asset["expected_crash_pct"])
        value = total_value * (alloc_pct / 100)
        
        table.add_row(
            name,
            format_percentage(alloc_pct),
            format_inr(value),
            format_percentage(crash_pct),
        )
    
    console.print(table)


def print_risk_metrics(metrics: dict, scenarios: dict) -> None:
    """Print risk metrics in formatted tables."""
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]RISK METRICS[/bold cyan]")
    console.print("=" * 70)
    
    # Current metrics
    table = Table(title="Severe Crash Scenario", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    metrics_data = [
        ["Post-Crash Value", format_inr(metrics.get("post_crash_value", 0))],
        ["Runway (Months)", f"{metrics.get('runway_months', 0):.2f}"],
        ["Ruin Test", metrics.get("ruin_test", "N/A")],
        ["Largest Risk Asset", metrics.get("largest_risk_asset", "N/A")],
        ["Concentration Warning", "YES" if metrics.get("concentration_warning") else "NO"],
    ]
    
    for metric, value in metrics_data:
        table.add_row(metric, value)
    
    console.print(table)
    
    # Scenario comparison
    console.print("\n[bold]Scenario Comparison:[/bold]")
    scenario_table = Table(title="Scenarios", show_header=True)
    scenario_table.add_column("Scenario", style="cyan")
    scenario_table.add_column("Post-Crash Value", style="yellow")
    scenario_table.add_column("Runway (Months)", style="yellow")
    scenario_table.add_column("Status", style="green")
    
    for scenario_name in ["current", "moderate", "severe"]:
        if scenario_name in scenarios:
            scenario = scenarios[scenario_name]
            post_crash = scenario.get("post_crash_value", 0)
            runway = scenario.get("runway_months", 0)
            ruin_test = scenario.get("ruin_test", "N/A")
            
            status_color = "green" if ruin_test == "PASS" else "red"
            status_text = f"[{status_color}]{ruin_test}[/{status_color}]"
            
            scenario_table.add_row(
                scenario_name.capitalize(),
                format_inr(post_crash),
                f"{runway:.2f}",
                status_text,
            )
    
    console.print(scenario_table)


def print_ai_advice(advice: Optional[dict]) -> None:
    """Print AI advisor recommendations."""
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]AI ADVISOR RECOMMENDATIONS[/bold cyan]")
    console.print("=" * 70)
    
    if not advice:
        log_warning("No AI advice available (LLM call failed or skipped)")
        return
    
    # Summary
    if "summary" in advice:
        console.print(Panel(advice["summary"], title="[bold]Summary[/bold]", expand=False))
    
    # Good thing
    if "good_thing" in advice:
        console.print("\n[bold green][+] What's Working:[/bold green]")
        console.print(f"  {advice['good_thing']}")
    
    # Improvement
    if "improvement" in advice:
        console.print("\n[bold yellow][!] Areas to Improve:[/bold yellow]")
        console.print(f"  {advice['improvement']}")
    
    # Verdict
    if "verdict" in advice:
        verdict = advice["verdict"]
        if verdict == "Aggressive":
            verdict_style = "red"
        elif verdict == "Conservative":
            verdict_style = "green"
        else:
            verdict_style = "yellow"
        
        console.print(f"\n[bold {verdict_style}]Portfolio Verdict: {verdict}[/bold {verdict_style}]")


def print_plot_summary(plots: dict, output_dir: str) -> None:
    """Print summary of generated plots."""
    console.print("\n" + "=" * 70)
    console.print("[bold cyan]GENERATED VISUALIZATIONS[/bold cyan]")
    console.print("=" * 70)
    
    plot_descriptions = {
        "allocation": "Asset Allocation Pie Chart",
        "runway": "Runway Comparison Across Scenarios",
        "risk_scores": "Asset Risk Scores Scatter Plot",
        "post_crash": "Post-Crash Value Comparison",
        "concentration": "Concentration Risk Analysis",
    }
    
    for plot_key, description in plot_descriptions.items():
        if plot_key in plots:
            plot_path = plots[plot_key]
            console.print(f"[green][OK][/green] {description}")
            console.print(f"  -> {plot_path}")


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Task4 - Portfolio Visualizer & AI Advisor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--input-mode",
        choices=["python", "json", "string"],
        default="python",
        help="Input source (default: python)",
    )
    parser.add_argument(
        "--input-file",
        help="Path to JSON or Python portfolio file",
    )
    parser.add_argument(
        "--tone",
        choices=["beginner", "experienced", "expert"],
        default=DEFAULT_TONE,
        help="Tone for AI advice",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save plots (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip LLM call, show metrics & plots only",
    )
    parser.add_argument(
        "--compare-scenarios",
        action="store_true",
        help="Show detailed scenario comparison",
    )
    
    args = parser.parse_args(argv)
    
    try:
        # Load portfolio
        log_info("Loading portfolio...")
        portfolio = load_portfolio(
            input_mode=args.input_mode,
            file_path=args.input_file,
        )
        log_success("Portfolio loaded successfully")
        
        # Print portfolio summary
        print_portfolio_summary(portfolio)
        print_asset_details(portfolio)
        
        # Compute risk metrics
        log_info("Computing risk metrics...")
        metrics = compute_risk_metrics(portfolio)
        scenarios = compute_all_scenarios(portfolio)
        risk_scores = get_asset_risk_scores(portfolio)
        log_success("Risk metrics computed")
        
        # Print risk metrics
        print_risk_metrics(metrics, scenarios)
        
        # Generate plots
        log_info("Generating visualizations...")
        ensure_output_dir(args.output_dir)
        plots = generate_all_plots(
            portfolio=portfolio,
            scenarios=scenarios,
            risk_scores=risk_scores,
            concentration_warning=metrics.get("concentration_warning", False),
            output_dir=args.output_dir,
        )
        log_success("Visualizations generated")
        print_plot_summary(plots, args.output_dir)
        
        # Get AI advice (if not skipped)
        advice = None
        if not args.no_ai:
            log_info("Getting AI advisor recommendations...")
            advice = get_ai_advice(portfolio, metrics, tone=args.tone)
            if advice:
                log_success("AI advice received")
            else:
                log_warning("AI advice unavailable")
        else:
            log_info("Skipping AI advisor (--no-ai flag)")
        
        print_ai_advice(advice)
        
        # Final summary
        console.print("\n" + "=" * 70)
        console.print("[bold green][OK] ANALYSIS COMPLETE[/bold green]")
        console.print("=" * 70)
        console.print(f"\n[cyan]Plots saved to:[/cyan] {args.output_dir}")
        console.print("\nYou can now review the generated PNG files for detailed visualizations.\n")
        
        return 0
    
    except FileNotFoundError as e:
        log_error(f"File not found: {e}")
        return 1
    except ValueError as e:
        log_error(f"Invalid input: {e}")
        return 1
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
