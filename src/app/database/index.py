#!/usr/bin/env python3
"""
Database Seeding CLI for Rental Management System
Usage:
    python src/app/database/index.py                    # Full seed with defaults
    python src/app/database/index.py --rooms 15         # Custom room count
    python src/app/database/index.py --no-clear         # Skip clearing existing data
    python src/app/database/index.py --help             # Show help
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.app.config.session import local_session
from src.app.database.seed.seeder import DatabaseSeeder
from src.app.utils.color import Colors


def parse_args():
    parser = argparse.ArgumentParser(description="Seed rental management database")
    parser.add_argument("--rooms", type=int, default=20, help="Number of rooms to seed")
    parser.add_argument("--tenants", type=int, default=20, help="Number of tenants to seed")
    parser.add_argument("--no-clear", action="store_true", help="Skip clearing existing data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be seeded without executing")
    return parser.parse_args()


def main():
    args = parse_args()
    
    Colors.print("🚀 Rental Management System - Database Seeder", Colors.HEADER)
    print(f"   Rooms: {args.rooms} | Tenants: {args.tenants} | Clear: {not args.no_clear}")
    
    if args.dry_run:
        Colors.info("Dry run mode - no changes will be made")
        return
    
    db = local_session()
    try:
        seeder = DatabaseSeeder(db)
        results = seeder.run(
            num_tenants=args.tenants,
            num_rooms=args.rooms,
            clear_first=not args.no_clear
        )
        Colors.success("\n✨ Ready for testing! 🎉")
        return 0
    except Exception as e:
        Colors.error(f"\nSeeding failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())