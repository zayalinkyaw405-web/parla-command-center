import argparse
import io
import json
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from parla.domains.void_engine import VoidEngine


def load_scenario(file_path: str) -> dict:
    """Load a JSON scenario file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Unable to read scenario file: {e}")
        sys.exit(1)


def parse_entities(entities_str: str) -> dict:
    """Parse a comma-separated list of entities into a scenario dict."""
    entities = [e.strip() for e in entities_str.split(",") if e.strip()]
    return {"entities": entities}


def display_roster(engine: VoidEngine) -> None:
    """Prints a clean, human-readable breakdown of everyone in the user's accord."""
    roster = engine.get_accord_roster()
    print("=" * 72)
    print(f"  {roster.get('accord_name', 'The Void Coexistence Accord').upper()}")
    print(f"  Motto: \"{roster.get('motto', 'Part of all, helping all.')}\"")
    print(f"  Established: {roster.get('founded_date', '2026-10-02')}")
    print("=" * 72)
    print()

    members = roster.get("members", [])
    print(f"Total Signatories & Protected Parties: {len(members)}\n")

    current_category = None
    for m in members:
        cat = m.get("category", "General Member")
        if cat != current_category:
            current_category = cat
            print(f"\n--- [ {current_category.upper()} ] ---")
        
        print(f"  * ID: {m.get('id')} | Name: {m.get('name')}")
        print(f"    Role: {m.get('role')} | Status: {m.get('status')}")
        print("    Protections & Benefits:")
        for p in m.get("protections_and_benefits", []):
            print(f"      - {p}")
        print()

    print("=" * 72)
    print("Status: ALL PARTIES HARMONIZED UNDER THE MUTUAL COEXISTENCE ACCORD.")
    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(
        description="Assess paranormal nullification risk, view roster, and generate collaboration accords via the VOID pillar.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--roster",
        action="store_true",
        help="Display the active Accord Signatory Registry & Census Roster (Who is in my Accord).")
    group.add_argument(
        "--entities",
        type=str,
        help="Comma-separated list of paranormal entities (e.g. 'alien,god,mutation').")
    group.add_argument(
        "--scenario-file",
        type=str,
        help="Path to a JSON file containing a scenario with an 'entities' array.")
    args = parser.parse_args()

    engine = VoidEngine()

    if args.roster:
        display_roster(engine)
        return

    if args.entities:
        scenario = parse_entities(args.entities)
    else:
        scenario = load_scenario(args.scenario_file)

    result = engine.assess_paranormal_nullification(scenario)

    # Attach accords for each entity if the method exists
    if hasattr(engine, "generate_accord"):
        accords = []
        for entity in scenario.get("entities", []):
            accords.append(engine.generate_accord(entity))
        result["accords"] = accords

    # Pretty-print the final report
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
