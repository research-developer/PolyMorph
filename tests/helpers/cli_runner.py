"""
Test helper for running CLI commands

This module provides utilities for testing CLI behavior in TDD mode.
"""
import subprocess
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


class CLIRunner:
    """Helper class to run CLI commands and capture output"""

    def __init__(self, cli_path: Optional[Path] = None):
        """
        Initialize CLI runner

        Args:
            cli_path: Path to CLI executable (defaults to plugin's cli.py)
        """
        if cli_path is None:
            # Default to the CLI we're about to create
            plugin_dir = Path(__file__).parent.parent.parent
            cli_path = plugin_dir / "cli.py"

        self.cli_path = cli_path

    def run(
        self,
        args: List[str],
        input_text: Optional[str] = None,
        check: bool = False
    ) -> 'CLIResult':
        """
        Run CLI command with arguments

        Args:
            args: Command-line arguments
            input_text: Optional stdin input
            check: If True, raise exception on non-zero exit code

        Returns:
            CLIResult with stdout, stderr, exit_code
        """
        cmd = ["python3", str(self.cli_path)] + args

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                input=input_text,
                timeout=10
            )

            return CLIResult(
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )
        except subprocess.TimeoutExpired:
            return CLIResult(
                stdout="",
                stderr="Command timed out",
                exit_code=124
            )
        except FileNotFoundError as e:
            return CLIResult(
                stdout="",
                stderr=f"CLI not found: {e}",
                exit_code=127
            )

    def run_json(self, args: List[str]) -> Dict[str, Any]:
        """
        Run CLI command expecting JSON output

        Args:
            args: Command-line arguments

        Returns:
            Parsed JSON output

        Raises:
            json.JSONDecodeError: If output is not valid JSON
        """
        result = self.run(args)
        return json.loads(result.stdout)


class CLIResult:
    """Container for CLI execution results"""

    def __init__(self, stdout: str, stderr: str, exit_code: int):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.success = exit_code == 0

    def __repr__(self):
        return f"CLIResult(exit_code={self.exit_code}, success={self.success})"

    @property
    def json(self) -> Dict[str, Any]:
        """Parse stdout as JSON"""
        return json.loads(self.stdout)
