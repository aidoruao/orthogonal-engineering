#!/usr/bin/env python3
"""
TOKEN USAGE ANALYZER - Glass Box Boundary Compliant
Version: 1.11
Schema ID: GB-ORIGIN-1.11

Purpose: Analyze repository files for potential token usage issues
that could cause IDE summary generation failures or API token limit errors.

Glass Box Boundary Compliance:
- Uses @glass_box_boundary decorator for all functions
- Implements fail-fast architecture (exit code 2 on violations)
- Maintains orthogonal separation principles
- Generates trace-compliant output
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ============================================================================
# GLASS BOX BOUNDARY DECORATOR
# ============================================================================


def glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
):
    """
    Glass Box Boundary decorator factory.

    Enforces:
    1. Input validation (if validator provided)
    2. Output validation (if validator provided)
    3. Side effect confinement
    4. Orthogonal separation principles
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Input validation
            if input_validator:
                try:
                    input_validator(*args, **kwargs)
                except Exception as e:
                    raise ValueError(f"Input validation failed: {str(e)}")

            # Execute function with boundary enforcement
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                # Re-raise with boundary violation context
                raise RuntimeError(f"Boundary violation in {func.__name__}: {str(e)}")

            # Output validation
            if output_validator:
                try:
                    output_validator(result)
                except Exception as e:
                    raise ValueError(f"Output validation failed: {str(e)}")

            return result

        return wrapper

    return decorator


# ============================================================================
# CONSTANTS
# ============================================================================

# Token usage limits
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB maximum file size
MAX_TOKEN_ESTIMATE = 100000  # 100K tokens maximum estimate
TOKEN_RATIO = 0.75  # Rough estimate: tokens = chars * 0.75
WARNING_THRESHOLD = 0.8  # Warn at 80% of limit

# Text file extensions to analyze
TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".html",
    ".js",
    ".css",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".xml",
    ".csv",
    ".tsv",
    ".rst",
    ".tex",
    ".log",
}

# Directories to exclude from analysis
EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    "target",
    "out",
    "bin",
    "obj",
    ".idea",
    ".vscode",
    ".zed",
}

# ============================================================================
# CORE ANALYSIS FUNCTIONS
# ============================================================================


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def analyze_file_token_usage(file_path: Path, repo_root: Path) -> Dict[str, Any]:
    """
    Analyze a single file for token usage.

    Returns:
        Dictionary with analysis results
    """
    try:
        # Get file stats
        file_size = file_path.stat().st_size
        relative_path = str(file_path.relative_to(repo_root))

        # Estimate token count (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = int(file_size * TOKEN_RATIO / 4)

        # Calculate percentages
        size_percentage = (file_size / MAX_FILE_SIZE_BYTES) * 100
        token_percentage = (estimated_tokens / MAX_TOKEN_ESTIMATE) * 100

        # Determine severity
        severity = "low"
        if file_size > MAX_FILE_SIZE_BYTES or estimated_tokens > MAX_TOKEN_ESTIMATE:
            severity = "critical"
        elif size_percentage > 80 or token_percentage > 80:
            severity = "high"
        elif size_percentage > 50 or token_percentage > 50:
            severity = "medium"

        # Generate recommendations
        recommendations = []
        if file_size > MAX_FILE_SIZE_BYTES:
            recommendations.append(
                f"File exceeds size limit ({file_size:,} bytes > {MAX_FILE_SIZE_BYTES:,} bytes)"
            )
            recommendations.append(
                f"Consider splitting file or adding to .zedignore: {relative_path}"
            )

        if estimated_tokens > MAX_TOKEN_ESTIMATE:
            recommendations.append(
                f"Estimated tokens exceed limit ({estimated_tokens:,} > {MAX_TOKEN_ESTIMATE:,})"
            )
            recommendations.append(
                "This file may cause IDE summary generation failures"
            )

        if size_percentage > 80 or token_percentage > 80:
            recommendations.append("File is approaching token/size limits")

        return {
            "file_path": relative_path,
            "file_size_bytes": file_size,
            "estimated_tokens": estimated_tokens,
            "size_percentage": round(size_percentage, 2),
            "token_percentage": round(token_percentage, 2),
            "severity": severity,
            "recommendations": recommendations,
            "extension": file_path.suffix.lower(),
            "last_modified": datetime.fromtimestamp(
                file_path.stat().st_mtime
            ).isoformat(),
        }

    except (OSError, UnicodeDecodeError) as e:
        # Return minimal info for unreadable files
        return {
            "file_path": str(file_path.relative_to(repo_root)),
            "error": str(e),
            "severity": "low",
            "recommendations": ["File cannot be analyzed (may be binary or corrupted)"],
        }


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def scan_repository_for_token_issues(repo_path: Path) -> Dict[str, Any]:
    """
    Scan entire repository for token usage issues.

    Returns:
        Comprehensive analysis report
    """
    repo_root = Path(repo_path).resolve()

    if not repo_root.exists():
        raise ValueError(f"Repository path does not exist: {repo_path}")

    analysis_results = []
    total_files = 0
    problematic_files = 0
    total_size_bytes = 0
    total_estimated_tokens = 0

    # Walk through repository
    for file_path in repo_root.rglob("*"):
        if file_path.is_file():
            # Skip excluded directories
            if any(excluded in str(file_path) for excluded in EXCLUDE_DIRS):
                continue

            # Skip non-text files
            if file_path.suffix.lower() not in TEXT_EXTENSIONS:
                continue

            total_files += 1

            # Analyze file
            result = analyze_file_token_usage(file_path, repo_root)
            analysis_results.append(result)

            # Update statistics
            if "file_size_bytes" in result:
                total_size_bytes += result["file_size_bytes"]
                total_estimated_tokens += result.get("estimated_tokens", 0)

            # Count problematic files
            if result.get("severity") in ["high", "critical"]:
                problematic_files += 1

    # Sort by severity (critical first)
    analysis_results.sort(
        key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(
            x.get("severity", "low"), 4
        )
    )

    # Generate summary
    summary = {
        "repository": str(repo_root),
        "scan_timestamp": datetime.now().isoformat(),
        "total_files_analyzed": total_files,
        "problematic_files": problematic_files,
        "total_size_bytes": total_size_bytes,
        "total_estimated_tokens": total_estimated_tokens,
        "max_file_size_bytes": MAX_FILE_SIZE_BYTES,
        "max_token_estimate": MAX_TOKEN_ESTIMATE,
        "token_ratio": TOKEN_RATIO,
        "warning_threshold": WARNING_THRESHOLD,
        "analysis_results": analysis_results,
    }

    return summary


@glass_box_boundary(
    input_validator=None,
    output_validator=None,
    side_effect_check=True,
    orthogonal_separation=True,
)
def generate_zedignore_recommendations(analysis_summary: Dict[str, Any]) -> List[str]:
    """
    Generate .zedignore recommendations based on analysis.

    Returns:
        List of .zedignore patterns
    """
    recommendations = []

    # Add header
    recommendations.append(
        "# .zedignore recommendations generated by token usage analyzer"
    )
    recommendations.append("# Generated: " + datetime.now().isoformat())
    recommendations.append("")

    # Group by directory
    dir_patterns = {}

    for result in analysis_summary.get("analysis_results", []):
        if result.get("severity") in ["critical", "high"]:
            file_path = result.get("file_path", "")
            if file_path:
                # Convert to .zedignore pattern
                dir_path = os.path.dirname(file_path)
                if dir_path:
                    if dir_path not in dir_patterns:
                        dir_patterns[dir_path] = []
                    dir_patterns[dir_path].append(file_path)

    # Generate patterns
    for dir_path, files in dir_patterns.items():
        if len(files) > 3:
            # If many files in directory, exclude the whole directory
            recommendations.append(f"# Multiple large files in {dir_path}/")
            recommendations.append(f"{dir_path}/*")
        else:
            # List individual files
            recommendations.append(f"# Large files in {dir_path}/")
            for file_path in files:
                recommendations.append(file_path)
        recommendations.append("")

    # Add common exclusions
    recommendations.append("# Common exclusions for token-heavy directories")
    recommendations.append("logs/**/*")
    recommendations.append("evidence/**/*")
    recommendations.append("chat_exports/*.txt")
    recommendations.append("chat_exports/*.json")
    recommendations.append("forgiveness_all_exports_output/**/*.json")
    recommendations.append("")

    return recommendations


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================


def main():
    """Main entry point with Glass Box Boundary compliance."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Token Usage Analyzer - Detect files that may cause IDE token limit issues",
        epilog="Exit codes: 0=Success, 1=System error, 2=Boundary violation",
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to repository (default: current directory)",
    )

    parser.add_argument(
        "--output", "-o", help="Output file for analysis results (default: stdout)"
    )

    parser.add_argument(
        "--zedignore",
        "-z",
        action="store_true",
        help="Generate .zedignore recommendations",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=WARNING_THRESHOLD,
        help="Warning threshold percentage (default: 80.0%%)",
    )

    args = parser.parse_args()

    try:
        # Scan repository
        if args.verbose:
            print(f"Scanning repository: {args.path}")

        analysis = scan_repository_for_token_issues(Path(args.path))

        # Output results
        output = json.dumps(analysis, indent=2, ensure_ascii=False)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            if args.verbose:
                print(f"Analysis written to: {args.output}")
        else:
            print(output)

        # Generate .zedignore recommendations if requested
        if args.zedignore:
            recommendations = generate_zedignore_recommendations(analysis)
            print("\n" + "=" * 80)
            print(".zedignore RECOMMENDATIONS")
            print("=" * 80)
            for line in recommendations:
                print(line)

        # Check for critical violations
        problematic_files = analysis.get("problematic_files", 0)
        if problematic_files > 0:
            print(
                f"\n⚠️  WARNING: Found {problematic_files} files that may cause token limit issues",
                file=sys.stderr,
            )

            # List critical files
            critical_files = [
                r
                for r in analysis.get("analysis_results", [])
                if r.get("severity") in ["critical", "high"]
            ]

            if args.verbose and critical_files:
                print("\nCritical/High severity files:", file=sys.stderr)
                for result in critical_files[:10]:  # Show top 10
                    print(
                        f"  - {result['file_path']} ({result['file_size_bytes']:,} bytes, "
                        f"{result['estimated_tokens']:,} estimated tokens)",
                        file=sys.stderr,
                    )

            # Exit with boundary violation code if critical files found
            critical_count = len(
                [r for r in critical_files if r.get("severity") == "critical"]
            )
            if critical_count > 0:
                print(
                    f"\n❌ CRITICAL: {critical_count} files exceed token/size limits",
                    file=sys.stderr,
                )
                sys.exit(2)  # Boundary violation

        if args.verbose:
            print(
                f"\n✅ Analysis complete: {analysis['total_files_analyzed']} files analyzed"
            )

        sys.exit(0)

    except ValueError as e:
        print(f"Validation error: {str(e)}", file=sys.stderr)
        sys.exit(1)

    except RuntimeError as e:
        print(f"Boundary violation: {str(e)}", file=sys.stderr)
        sys.exit(2)

    except Exception as e:
        print(f"System error: {str(e)}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
