"""ChronosGraph command line entry point.

chronos doctor      environment + phase-gate readiness report
chronos migrate     apply database migrations
chronos check       run research invariant checks
chronos sources     show the source registry approval state
"""

from __future__ import annotations

import typer

from chronosgraph.config import get_settings

app = typer.Typer(add_completion=False, help="ChronosGraph research CLI")


@app.command()
def doctor() -> None:
    """Report environment readiness without changing anything."""
    from chronosgraph.utils.doctor import report

    ok = report()
    raise typer.Exit(code=0 if ok else 1)


@app.command()
def migrate() -> None:
    """Apply pending database migrations."""
    from chronosgraph.db.migrate import migrate as run

    run()


@app.command()
def check() -> None:
    """Run the research invariant checks. Non-zero exit means a violation."""
    from chronosgraph.db.check import main

    raise typer.Exit(code=main())


@app.command()
def sources() -> None:
    """Show registered sources and their human-owned approval status."""
    from chronosgraph.sources import load_registry

    reg = load_registry()
    typer.echo(f"study window: {reg.study_window.start} .. {reg.study_window.end}")
    typer.echo(f"corpus frozen: {reg.frozen}")
    for s in reg.sources:
        typer.echo(f"  [{s.approval_status:>16}] {s.id:<16} {s.language}  {s.name}")
    approved = reg.approved()
    typer.echo(f"approved sources: {len(approved)}")


@app.command()
def config() -> None:
    """Print effective configuration with secrets redacted."""
    for k, v in get_settings().redacted().items():
        typer.echo(f"{k} = {v}")


if __name__ == "__main__":
    app()
