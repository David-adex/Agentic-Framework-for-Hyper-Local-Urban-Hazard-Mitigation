import subprocess
import sys
import os
from pathlib import Path

def run_script(script_name, description):
    script_path = Path(__file__).parent / script_name
    
    print()
    print("=" * 80)
    print(f"Step: {description}")
    print("=" * 80)
    print(f"Running: {script_name}")
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=Path(__file__).parent,
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


def main():
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  AGENTIC FRAMEWORK - COMPLETE UTILITY SEQUENCE".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    scripts = [
        ("create_geospatial_index.py", "1️⃣  Create MongoDB Geospatial Index"),
        ("ingest_sensor_data.py", "2️⃣  Ingest Realistic Sensor Data"),
        ("test_agent_query.py", "3️⃣  Test Agent Framework"),
    ]
    
    results = []
    
    for script_name, description in scripts:
        success = run_script(script_name, description)
        results.append((description, success))
        
        if not success:
            print()
            print(f"⚠️  Script {script_name} encountered an issue.")
            print("   Continuing with next step...")
    
    # Summary
    print()
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  EXECUTION SUMMARY".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    for description, success in results:
        status = "✅ PASS" if success else "⚠️  PARTIAL"
        print(f"{status} - {description}")
    
    all_passed = all(success for _, success in results)
    
    print()
    if all_passed:
        print("✅ ALL SCRIPTS COMPLETED SUCCESSFULLY!")
        print()
        print("Next steps:")
        print("  1. Open http://localhost:3000 in your browser")
        print("  2. View sensor markers on the interactive map")
        print("  3. Check detected anomalies in the dashboard")
        print("  4. Review agent mitigation recommendations")
    else:
        print("⚠️  Some scripts had issues, but this may not be critical.")
        print()
        print("Verify:")
        print("  1. Backend is running on 127.0.0.1:8001")
        print("  2. MongoDB credentials in .env are correct")
        print("  3. Check detailed output above for error messages")
    
    print()
    print("📖 For detailed information:")
    print("   - See backend/scripts/README.md for full documentation")
    print("   - Check QUICKSTART_SCRIPTS.md for quick reference")
    print()


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    main()
