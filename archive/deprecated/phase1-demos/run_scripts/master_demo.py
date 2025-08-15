#!/usr / bin / env python3
"""master_demo.py
--------------
Complete Charlie Reporting System End - to - End Demo

Orchestrates the entire process:
1. Generate CSV data files
2. Send individual emails (1 CSV per email)
3. Fetch emails from Outlook
4. Process CSV attachments
5. Generate Excel reports

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import subprocess
import time
from datetime import datetime

# Import shared utilities
from shared_utils import (
    ensure_directory_exists,
    get_demo_root,
    get_python_executable,
    get_relative_script_path,
    getproject_root,
)


class MasterDemo:
    def __init__(self):
        """Initialize the master demo controller"""
        self.demoroot = get_demo_root()
        self.projectroot = getproject_root()
        self.pythonexe = get_python_executable()
        self.democonfig = self.demo_root / "config.toml"

        print("🚀 Charlie Reporting System - Master Demo")
        print("=" * 60)
        print(f"📁 Demo Root: {self.demo_root}")
        print(f"📁 Project Root: {self.project_root}")
        print(f"🐍 Python: {self.python_exe}")
        print(f"⚙️ Config: {self.demo_config}")
        print()

        # Ensure required directories exist
        ensure_directory_exists(self.demo_root / "data" / "output")
        ensure_directory_exists(self.demo_root / "data" / "archive")
        ensure_directory_exists(self.demo_root / "data" / "raw")

    def run_script(self, script_path, description, wait_for_completion=True):
        """Run a Python script and handle output"""
        print(f"🔄 {description}")
        print(f"📝 Running: {script_path}")

        try:
            if wait_for_completion:
                result = subprocess.run(
                    [self.python_exe, str(script_path)],
                    check=False, cwd=script_path.parent,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    print("✅ Success!")
                    if result.stdout:
                        print("📤 Output:")
                        print(result.stdout[-1000:])  # Last 1000 chars
                else:
                    print("❌ Failed!")
                    if result.stderr:
                        print("🚨 Error:")
                        print(result.stderr)
                    return False
            else:
                # Start process without waiting
                subprocess.Popen([self.python_exe, str(script_path)], cwd=script_path.parent)
                print("🔄 Started in background...")

        except subprocess.TimeoutExpired:
            print("⏰ Script timed out (5 minutes)")
            return False
        except Exception as e:
            print(f"💥 Error running script: {e}")
            return False

        print()
        return True

    def step_1_generate_data(self):
        """Generate CSV data files"""
        print("🔥 STEP 1: Generate Demo Data")
        print("-" * 40)

        datagenerator = get_relative_script_path("data_generator.py", "data_generation")

        if not data_generator.exists():
            print(f"❌ Data generator not found: {data_generator}")
            return False

        return self.run_script(data_generator, "Generating CSV data files...")

    def step_2_send_emails(self):
        """Send focused demo emails (7 emails, 1 CSV each)"""
        print("📧 STEP 2: Send Demo Emails")
        print("-" * 40)

        emailsender = get_relative_script_path("focused_email_sender.py", "email_senders")

        if not email_sender.exists():
            print(f"❌ Email sender not found: {email_sender}")
            return False

        success = self.run_script(email_sender, "Sending 7 demo emails (1 CSV per email)...")

        if success:
            print("⏱️ Waiting 30 seconds for emails to arrive...")
            time.sleep(30)

        return success

    def step_3_process_emails(self):
        """Run Charlie Reporting System to process emails"""
        print("📥 STEP 3: Process Emails with Charlie Reporting System")
        print("-" * 40)

        # Navigate to main source directory and run the system
        mainscript = self.project_root / "src" / "main.py"

        if not main_script.exists():
            print(f"❌ Main script not found: {main_script}")
            return False

        print("🔄 Running Charlie Reporting System...")
        print(f"📁 Config: {self.demo_config}")

        try:
            result = subprocess.run(
                [self.python_exe, str(main_script), "--config", str(self.demo_config)],
                check=False, cwd=main_script.parent,
                capture_output=True,
                text=True,
                timeout=180
            )

            if result.returncode == 0:
                print("✅ Charlie Reporting System completed successfully!")
                if result.stdout:
                    print("📤 Output:")
                    print(result.stdout[-1500:])  # Last 1500 chars
            else:
                print("❌ Charlie Reporting System failed!")
                if result.stderr:
                    print("🚨 Error:")
                    print(result.stderr)
                if result.stdout:
                    print("📤 Output:")
                    print(result.stdout)
                return False

        except subprocess.TimeoutExpired:
            print("⏰ Charlie Reporting System timed out (3 minutes)")
            return False
        except Exception as e:
            print(f"💥 Error running Charlie Reporting System: {e}")
            return False

        print()
        return True

    def step_4_verify_results(self):
        """Verify the demo results"""
        print("🔍 STEP 4: Verify Demo Results")
        print("-" * 40)

        # Check for output files
        outputdir = self.demo_root / "data" / "output"
        archivedir = self.demo_root / "data" / "archive"
        rawdir = self.demo_root / "data" / "raw"

        print("📁 Checking directories:")
        print(f"   Output: {output_dir}")
        print(f"   Archive: {archive_dir}")
        print(f"   Raw: {raw_dir}")
        print()

        # Check output files
        if output_dir.exists():
            excelfiles = list(output_dir.glob("*.xlsx"))
            if excel_files:
                print(f"✅ Found {len(excel_files)} Excel report(s):")
                for file in excel_files:
                    print(f"   📊 {file.name}")
            else:
                print("⚠️ No Excel reports found in output directory")
        else:
            print("❌ Output directory doesn't exist")

        # Check raw files
        if raw_dir.exists():
            csvfiles = list(raw_dir.glob("*.csv"))
            if csv_files:
                print(f"✅ Found {len(csv_files)} processed CSV file(s):")
                for file in csv_files[:5]:  # Show first 5
                    print(f"   📄 {file.name}")
                if len(csv_files) > 5:
                    print(f"   ... and {len(csv_files) - 5} more")
            else:
                print("⚠️ No CSV files found in raw directory")
        else:
            print("❌ Raw directory doesn't exist")

        # Check archive
        if archive_dir.exists():
            archivedfiles = list(archive_dir.glob("*"))
            if archived_files:
                print(f"✅ Found {len(archived_files)} archived file(s)")
            else:
                print("⚠️ No archived files found")
        else:
            print("❌ Archive directory doesn't exist")

        print()
        return True

    def run_complete_demo(self):
        """Run the complete end - to - end demo"""
        starttime = datetime.now()

        print("🎬 Starting Complete End - to - End Demo")
        print(f"⏰ Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()

        # Step 1: Generate Data
        if not self.step_1_generate_data():
            print("💥 Demo failed at Step 1: Data Generation")
            return False

        # Step 2: Send Emails
        if not self.step_2_send_emails():
            print("💥 Demo failed at Step 2: Email Sending")
            return False

        # Step 3: Process Emails
        if not self.step_3_process_emails():
            print("💥 Demo failed at Step 3: Email Processing")
            return False

        # Step 4: Verify Results
        self.step_4_verify_results()

        endtime = datetime.now()
        duration = end_time - start_time

        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"⏰ Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Total Duration: {duration}")
        print()
        print("📋 What was demonstrated:")
        print("   ✅ CSV data generation (7 types, realistic call center data)")
        print("   ✅ Individual email sending (1 CSV per email)")
        print("   ✅ Email fetching from Outlook inbox")
        print("   ✅ CSV processing and transformation")
        print("   ✅ Excel report generation")
        print("   ✅ File archiving and organization")
        print()
        print("🔍 Next steps:")
        print("   📊 Review generated Excel reports in demo / data / output/")
        print("   📁 Check processed CSV files in demo / data / raw/")
        print("   📦 Verify archived emails in demo / data / archive/")
        print()

        return True


def main():
    """Main entry point"""
    try:
        demo = MasterDemo()

        print("🤔 Demo Options:")
        print("1. Run Complete End - to - End Demo")
        print("2. Send Emails Only (Step 2)")
        print("3. Process Emails Only (Step 3)")
        print("4. Exit")
        print()

        choice = input("Select option (1 - 4): ").strip()

        if choice == "1":
            demo.run_complete_demo()
        elif choice == "2":
            demo.step_2_send_emails()
        elif choice == "3":
            demo.step_3_process_emails()
        elif choice == "4":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n💥 Demo failed with error: {e}")


if __name__ == "__main__":
    main()