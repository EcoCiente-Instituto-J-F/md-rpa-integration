"""Migração pela linha de comando. Use --simular para rodar sem gravar."""

import sys

from rpa.orchestrator import MigrationOrchestrator


def main():
    success = MigrationOrchestrator(dry_run="--simular" in sys.argv).execute()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
