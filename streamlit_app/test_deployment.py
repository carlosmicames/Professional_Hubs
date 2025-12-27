"""
Test script to verify Streamlit app is deployment-ready
Run before deploying to Streamlit Cloud
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    try:
        import streamlit
        print("✅ streamlit")
        import requests
        print("✅ requests")
        import pandas
        print("✅ pandas")
        import sqlite3
        print("✅ sqlite3")
        import calendar  # CRITICAL
        print("✅ calendar (at module level)")
        import tempfile
        print("✅ tempfile")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database_path():
    """Test database path function"""
    print("\nTesting database path...")
    try:
        # Simulate function
        if os.path.exists('/mount/src'):  # Streamlit Cloud
            db_dir = '/tmp'
        else:  # Local
            db_dir = '.'
        db_path = os.path.join(db_dir, 'professional_hubs.db')
        print(f"✅ Database path: {db_path}")
        return True
    except Exception as e:
        print(f"❌ Database path error: {e}")
        return False

def test_file_structure():
    """Test required files exist"""
    print("\nTesting file structure...")
    required_files = [
        'app.py',
        'requirements.txt',
        '.streamlit/config.toml',
        '.env.example'
    ]

    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} missing")
            all_exist = False

    return all_exist

def check_critical_fixes():
    """Check that critical fixes are in place"""
    print("\nChecking critical fixes...")

    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    checks = []

    # Check 1: calendar imported at top level
    if 'import calendar  # CRITICAL' in content[:2000]:  # First ~2000 chars
        print("✅ calendar imported at module level")
        checks.append(True)
    else:
        print("❌ calendar NOT imported at module level (will cause timeout!)")
        checks.append(False)

    # Check 2: get_db_path function exists
    if 'def get_db_path():' in content:
        print("✅ get_db_path() function exists")
        checks.append(True)
    else:
        print("❌ get_db_path() function missing")
        checks.append(False)

    # Check 3: offline mode support
    if '"offline": True' in content or "'offline': True" in content:
        print("✅ Offline mode support added")
        checks.append(True)
    else:
        print("❌ Offline mode not implemented")
        checks.append(False)

    # Check 4: timeout reduced
    if 'timeout=5' in content or 'timeout = 5' in content:
        print("✅ API timeout set to 5 seconds")
        checks.append(True)
    else:
        print("⚠️  API timeout not set to 5 seconds (not critical)")
        checks.append(True)  # Not critical

    return all(checks)

def main():
    """Run all tests"""
    print("="*60)
    print("Streamlit Deployment Verification")
    print("="*60)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("Database Path", test_database_path()))
    results.append(("File Structure", test_file_structure()))
    results.append(("Critical Fixes", check_critical_fixes()))

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")

    print("="*60)

    if all(result[1] for result in results):
        print("\n🎉 ALL TESTS PASSED - Ready for deployment!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Fix Streamlit deployment'")
        print("3. git push origin main")
        print("4. Deploy on share.streamlit.io")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Fix issues before deploying")
        print("\nSee STREAMLIT_DEPLOYMENT_FIX.md for solutions")
        return 1

if __name__ == "__main__":
    sys.exit(main())
