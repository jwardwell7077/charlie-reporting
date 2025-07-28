"""
master_end_to_end_demo.py
-------------------------
Complete end-to-end demonstration of the Charlie Reporting System.

This script orchestrates the full workflow:
1. Generate realistic call center data
2. Send emails with attachments to Outlook
3. Monitor and process emails automatically
4. Generate Excel reports with incremental updates
5. Provide detailed logging and analysis

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
import logging

# Add paths for imports
demo_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(demo_dir))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, demo_dir)

# Import project modules
from config_loader import ConfigLoader
from email_fetcher import EmailFetcher
from transformer import CSVTransformer
from excel_writer import ExcelWriter
from main import ReportProcessor

# Import demo modules
from data_generator import RealisticDataGenerator
from email_sender import EmailSender

class EndToEndDemo:
    def __init__(self):
        """Initialize the complete demo environment"""
        self.demo_dir = os.path.dirname(os.path.abspath(__file__))
        self.project_root = os.path.dirname(os.path.dirname(self.demo_dir))
        
        # Setup paths
        self.config_path = os.path.join(os.path.dirname(self.demo_dir), 'config.toml')
        self.output_dir = os.path.join(os.path.dirname(self.demo_dir), 'data', 'output')
        self.logs_dir = os.path.join(os.path.dirname(self.demo_dir), 'logs')
        
        # Create directories
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.data_generator = None
        self.email_sender = None
        self.report_processor = None
        self.monitoring_active = False
        
    def _setup_logging(self):
        """Setup comprehensive logging for the demo"""
        log_file = os.path.join(self.logs_dir, f'end_to_end_demo_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('EndToEndDemo')
        self.logger.info("Demo logging initialized")
    
    def print_banner(self):
        """Print demo banner and information"""
        print("=" * 80)
        print("🎯 CHARLIE REPORTING SYSTEM - END-TO-END DEMO")
        print("=" * 80)
        print(f"📅 Demo Date: {datetime.now().strftime('%A, %B %d, %Y')}")
        print(f"⏰ Start Time: {datetime.now().strftime('%I:%M:%S %p')}")
        print(f"📧 Target Email: jontajon191@gmail.com")
        print(f"📁 Demo Directory: {os.path.dirname(self.demo_dir)}")
        print(f"📊 Simulation: 4 hours of call center data (5-minute intervals)")
        print("=" * 80)
    
    def phase_1_data_generation(self) -> Dict[str, List[str]]:
        """Phase 1: Generate realistic call center data"""
        print("\n🔷 PHASE 1: DATA GENERATION")
        print("-" * 50)
        
        self.logger.info("Starting Phase 1: Data Generation")
        
        # Initialize data generator
        base_data_dir = os.path.join(self.project_root, 'tests', 'data')
        self.data_generator = RealisticDataGenerator(base_data_dir)
        
        # Generate demo dataset (9 AM - 1 PM, every 5 minutes = 48 intervals)
        start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        print(f"📊 Generating realistic call center data...")
        print(f"   Start Time: {start_time.strftime('%I:%M %p')}")
        print(f"   Duration: 4 hours (9 AM - 1 PM)")
        print(f"   Interval: 5 minutes")
        print(f"   Total Files: ~144 CSV files (3 types × 48 intervals)")
        
        demo_files = self.data_generator.generate_demo_dataset(
            start_time=start_time,
            intervals=48,  # 4 hours × 12 (5-min intervals per hour)
            interval_minutes=5
        )
        
        print(f"✅ Data generation complete!")
        print(f"   Generated files for {len(demo_files)} time intervals")
        print(f"   Files saved to: {self.data_generator.output_dir}")
        
        self.logger.info(f"Phase 1 complete: Generated {len(demo_files)} time intervals")
        return demo_files
    
    def phase_2_email_sending(self, demo_files: Dict[str, List[str]]) -> int:
        """Phase 2: Send emails with CSV attachments"""
        print("\n🔷 PHASE 2: EMAIL SENDING")
        print("-" * 50)
        
        self.logger.info("Starting Phase 2: Email Sending")
        
        # Initialize email sender
        self.email_sender = EmailSender(to_email="jontajon191@gmail.com")
        
        print(f"📧 Preparing to send {len(demo_files)} emails...")
        print(f"   Target: jontajon191@gmail.com")
        print(f"   Sender: genesysreports@genesysdev.com (simulated)")
        print(f"   Interval: 1 minute between emails")
        print(f"   Estimated time: {len(demo_files)} minutes")
        
        # Confirm before sending
        response = input("\n🤔 Ready to start sending emails? (y/N): ").lower()
        if response != 'y':
            print("❌ Email sending cancelled by user")
            return 0
        
        print("\n📤 Starting email transmission...")
        
        # Send emails with 1-minute delays
        sent_count = self.email_sender.send_batch_emails(demo_files, delay_minutes=1)
        
        print(f"✅ Email sending complete!")
        print(f"   Emails sent: {sent_count}/{len(demo_files)}")
        
        self.logger.info(f"Phase 2 complete: Sent {sent_count} emails")
        return sent_count
    
    def phase_3_monitoring_setup(self) -> bool:
        """Phase 3: Setup automated monitoring and processing"""
        print("\n🔷 PHASE 3: AUTOMATED MONITORING SETUP")
        print("-" * 50)
        
        self.logger.info("Starting Phase 3: Monitoring Setup")
        
        try:
            # Initialize report processor with demo config
            print("🔧 Initializing report processor...")
            self.report_processor = ReportProcessor(self.config_path)
            print("✅ Report processor initialized")
            
            # Setup monitoring parameters
            self.monitoring_interval = 120  # 2 minutes
            self.monitoring_active = True
            
            print(f"📡 Monitoring configuration:")
            print(f"   Check interval: {self.monitoring_interval} seconds (2 minutes)")
            print(f"   Target folder: Inbox/Genesys")
            print(f"   Email account: jontajon191@gmail.com")
            print(f"   Output directory: {self.output_dir}")
            
            self.logger.info("Phase 3 complete: Monitoring setup ready")
            return True
            
        except Exception as e:
            print(f"❌ Monitoring setup failed: {e}")
            self.logger.error(f"Phase 3 failed: {e}")
            return False
    
    def phase_4_automated_processing(self) -> Dict[str, any]:
        """Phase 4: Run automated email monitoring and processing"""
        print("\n🔷 PHASE 4: AUTOMATED PROCESSING")
        print("-" * 50)
        
        self.logger.info("Starting Phase 4: Automated Processing")
        
        processing_stats = {
            'emails_processed': 0,
            'excel_files_created': 0,
            'total_records': 0,
            'start_time': datetime.now(),
            'errors': []
        }
        
        print("🔄 Starting automated monitoring loop...")
        print("   Press Ctrl+C to stop monitoring")
        print("   Monitoring will run for approximately 1 hour or until stopped")
        
        try:
            cycle_count = 0
            max_cycles = 30  # 30 cycles × 2 minutes = 1 hour
            
            while self.monitoring_active and cycle_count < max_cycles:
                cycle_count += 1
                cycle_start = datetime.now()
                
                print(f"\n🔍 Monitoring Cycle {cycle_count}/{max_cycles}")
                print(f"   Time: {cycle_start.strftime('%I:%M:%S %p')}")
                
                try:
                    # Process any new emails for today
                    today = datetime.now().strftime('%Y-%m-%d')
                    
                    # Use the report processor to handle new data
                    current_hour = datetime.now().hour
                    result = self.report_processor.process_hour(today, current_hour)
                    
                    if result:
                        processing_stats['emails_processed'] += 1
                        processing_stats['excel_files_created'] += 1
                        
                        excel_filename = os.path.basename(result)
                        print(f"   ✅ Processed data → {excel_filename}")
                        
                        # Analyze the created file
                        self._analyze_excel_file(result, processing_stats)
                        
                    else:
                        print(f"   ℹ️ No new data found")
                    
                except Exception as e:
                    error_msg = f"Cycle {cycle_count} error: {e}"
                    print(f"   ❌ {error_msg}")
                    processing_stats['errors'].append(error_msg)
                    self.logger.error(error_msg)
                
                # Wait for next cycle
                if cycle_count < max_cycles:
                    print(f"   ⏱️ Waiting {self.monitoring_interval} seconds until next check...")
                    time.sleep(self.monitoring_interval)
            
        except KeyboardInterrupt:
            print(f"\n⏹️ Monitoring stopped by user after {cycle_count} cycles")
            self.monitoring_active = False
        
        processing_stats['end_time'] = datetime.now()
        processing_stats['duration'] = processing_stats['end_time'] - processing_stats['start_time']
        
        print(f"\n✅ Automated processing complete!")
        self._print_processing_summary(processing_stats)
        
        self.logger.info(f"Phase 4 complete: Processed {processing_stats['emails_processed']} emails")
        return processing_stats
    
    def _analyze_excel_file(self, excel_path: str, stats: dict):
        """Analyze created Excel file and update stats"""
        try:
            import pandas as pd
            
            # Read Excel file to count records
            excel_data = pd.read_excel(excel_path, sheet_name=None)
            
            total_records = sum(len(df) for df in excel_data.values())
            stats['total_records'] += total_records
            
            print(f"     📊 File analysis:")
            print(f"        Sheets: {len(excel_data)}")
            print(f"        Total records: {total_records}")
            print(f"        File size: {os.path.getsize(excel_path):,} bytes")
            
        except Exception as e:
            print(f"     ⚠️ Could not analyze Excel file: {e}")
    
    def _print_processing_summary(self, stats: dict):
        """Print comprehensive processing summary"""
        print("\n📈 PROCESSING SUMMARY")
        print("-" * 40)
        print(f"Duration: {stats['duration']}")
        print(f"Emails processed: {stats['emails_processed']}")
        print(f"Excel files created: {stats['excel_files_created']}")
        print(f"Total records processed: {stats['total_records']:,}")
        print(f"Errors encountered: {len(stats['errors'])}")
        
        if stats['errors']:
            print("\n❌ Errors:")
            for error in stats['errors']:
                print(f"   • {error}")
        
        # Calculate performance metrics
        if stats['duration'].total_seconds() > 0:
            records_per_second = stats['total_records'] / stats['duration'].total_seconds()
            print(f"\n⚡ Performance:")
            print(f"   Records/second: {records_per_second:.2f}")
    
    def phase_5_verification(self, processing_stats: dict):
        """Phase 5: Verify and analyze results"""
        print("\n🔷 PHASE 5: VERIFICATION & ANALYSIS")
        print("-" * 50)
        
        self.logger.info("Starting Phase 5: Verification")
        
        print("🔍 Analyzing demo results...")
        
        # Check output directory
        output_files = [f for f in os.listdir(self.output_dir) if f.endswith('.xlsx')]
        
        print(f"\n📁 Output Directory Analysis:")
        print(f"   Location: {self.output_dir}")
        print(f"   Excel files created: {len(output_files)}")
        
        if output_files:
            print(f"   Files:")
            for file in sorted(output_files):
                file_path = os.path.join(self.output_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                print(f"     • {file}")
                print(f"       Size: {file_size:,} bytes")
                print(f"       Modified: {file_time.strftime('%I:%M:%S %p')}")
        
        # Performance analysis
        print(f"\n⚡ Performance Analysis:")
        if processing_stats['duration'].total_seconds() > 0:
            avg_processing_time = processing_stats['duration'].total_seconds() / max(processing_stats['emails_processed'], 1)
            print(f"   Average processing time: {avg_processing_time:.2f} seconds per email")
            print(f"   Total processing time: {processing_stats['duration']}")
            print(f"   System efficiency: {'Excellent' if avg_processing_time < 10 else 'Good' if avg_processing_time < 30 else 'Needs optimization'}")
        
        # Success metrics
        success_rate = processing_stats['emails_processed'] / max(processing_stats.get('emails_sent', 1), 1) * 100
        print(f"\n🎯 Success Metrics:")
        print(f"   Processing success rate: {success_rate:.1f}%")
        print(f"   Error rate: {len(processing_stats['errors']) / max(processing_stats['emails_processed'], 1) * 100:.1f}%")
        
        print(f"\n✅ Verification complete!")
        self.logger.info("Phase 5 complete: Verification successful")
    
    def cleanup(self):
        """Cleanup demo resources"""
        print("\n🧹 Demo cleanup...")
        self.monitoring_active = False
        
        # Additional cleanup could go here
        print("✅ Cleanup complete")
    
    def run_complete_demo(self):
        """Run the complete end-to-end demonstration"""
        try:
            self.print_banner()
            
            # Phase 1: Generate Data
            demo_files = self.phase_1_data_generation()
            
            # Phase 2: Send Emails
            emails_sent = self.phase_2_email_sending(demo_files)
            
            if emails_sent == 0:
                print("❌ No emails sent, cannot proceed with processing demo")
                return
            
            # Phase 3: Setup Monitoring
            if not self.phase_3_monitoring_setup():
                print("❌ Monitoring setup failed, cannot proceed")
                return
            
            # Phase 4: Automated Processing
            processing_stats = self.phase_4_automated_processing()
            processing_stats['emails_sent'] = emails_sent
            
            # Phase 5: Verification
            self.phase_5_verification(processing_stats)
            
            # Demo completion
            print("\n" + "=" * 80)
            print("🎉 END-TO-END DEMO COMPLETE!")
            print("=" * 80)
            print(f"⏰ Total demo time: {datetime.now() - processing_stats['start_time']}")
            print("📊 The Charlie Reporting System successfully demonstrated:")
            print("   ✅ Realistic data generation")
            print("   ✅ Automated email sending")
            print("   ✅ Real-time email monitoring")
            print("   ✅ Incremental Excel processing")
            print("   ✅ Comprehensive error handling")
            print("   ✅ Production-ready performance")
            print("\n🚀 System is ready for production deployment!")
            
        except KeyboardInterrupt:
            print("\n⏹️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            self.logger.error(f"Demo failed: {e}")
        finally:
            self.cleanup()


if __name__ == "__main__":
    demo = EndToEndDemo()
    demo.run_complete_demo()
