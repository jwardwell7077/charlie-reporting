"""
test_integration_complete.py
---------------------------
Complete integration test suite for charlie-reporting system.
Tests real email sending/receiving, SMTP authentication, data generation, and attachment workflows.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import unittest
import time
import logging
from pathlib import Path

from utils.integration_base import IntegrationTestBase

class TestCompleteIntegration(IntegrationTestBase):
    """
    Complete integration test suite covering all major workflows.
    """
    
    def test_01_smtp_connection_and_basic_email(self):
        """Test 1: Verify SMTP connection and basic email sending/receiving."""
        self.logger.info("=== TEST 1: SMTP Connection and Basic Email ===")
        
        # Create test email subject
        subject = self.create_test_email_subject("SMTP Basic Test")
        
        # Send basic test email
        success = self.email_manager.send_simple_email(
            to_address=self.get_config_value('email.test_receiver_address'),
            subject=subject,
            body="This is a basic SMTP integration test email."
        )
        
        self.assertTrue(success, "Failed to send basic email")
        self.logger.info("✓ Basic email sent successfully")
        
        # Verify email was received
        email_details = self.assert_email_sent_and_received(subject, timeout_seconds=60)
        self.logger.info(f"✓ Email received: {email_details.get('subject', 'N/A')}")
        
        # Verify email content
        self.assertIn("SMTP integration test", email_details.get('body', ''))
        self.logger.info("✓ Email content verified")
    
    def test_02_csv_data_generation(self):
        """Test 2: Generate test CSV data and verify structure."""
        self.logger.info("=== TEST 2: CSV Data Generation ===")
        
        # Generate test CSV files
        csv_files = self.data_generator.generate_multiple_csvs(
            output_dir=self.temp_manager.get_temp_dir('generated'),
            file_count=3
        )
        
        self.assertEqual(len(csv_files), 3, "Expected 3 CSV files to be generated")
        self.logger.info(f"✓ Generated {len(csv_files)} CSV files")
        
        # Verify each CSV file
        for csv_file in csv_files:
            self.assertTrue(os.path.exists(csv_file), f"CSV file missing: {csv_file}")
            
            # Verify CSV structure
            is_valid = self.data_generator.verify_csv_structure(csv_file)
            self.assertTrue(is_valid, f"Invalid CSV structure: {csv_file}")
            
            self.logger.info(f"✓ Verified CSV structure: {os.path.basename(csv_file)}")
        
        # Track files for cleanup
        for csv_file in csv_files:
            self.temp_manager.track_file(csv_file)
    
    def test_03_email_with_csv_attachments(self):
        """Test 3: Send email with CSV attachments and verify receipt."""
        self.logger.info("=== TEST 3: Email with CSV Attachments ===")
        
        # Generate test CSV file
        csv_file = self.data_generator.generate_test_csv(
            filename="test_attachment.csv",
            output_dir=self.temp_manager.get_temp_dir('generated'),
            row_count=10
        )
        
        self.assertTrue(os.path.exists(csv_file), "Test CSV file was not created")
        self.logger.info(f"✓ Generated test CSV: {os.path.basename(csv_file)}")
        
        # Create test email subject
        subject = self.create_test_email_subject("CSV Attachment Test")
        
        # Send email with CSV attachment
        success = self.email_manager.send_email_with_csv_attachment(
            to_address=self.get_config_value('email.test_receiver_address'),
            subject=subject,
            body="This email contains a test CSV attachment for integration testing.",
            csv_file_path=csv_file
        )
        
        self.assertTrue(success, "Failed to send email with CSV attachment")
        self.logger.info("✓ Email with CSV attachment sent successfully")
        
        # Verify email was received
        email_details = self.assert_email_sent_and_received(subject, timeout_seconds=90)
        self.logger.info("✓ Email with attachment received")
        
        # Verify attachment presence
        attachments = email_details.get('attachments', [])
        self.assertGreater(len(attachments), 0, "No attachments found in received email")
        self.logger.info(f"✓ Found {len(attachments)} attachment(s)")
        
        # Verify attachment filename
        attachment_names = [att.get('filename', '') for att in attachments]
        self.assertIn("test_attachment.csv", attachment_names, "Expected CSV attachment not found")
        self.logger.info("✓ CSV attachment filename verified")
    
    def test_04_multiple_csv_email_workflow(self):
        """Test 4: Generate multiple CSVs and send them via email."""
        self.logger.info("=== TEST 4: Multiple CSV Email Workflow ===")
        
        # Generate multiple test CSV files
        csv_files = self.data_generator.generate_multiple_csvs(
            output_dir=self.temp_manager.get_temp_dir('generated'),
            file_count=2
        )
        
        self.assertEqual(len(csv_files), 2, "Expected 2 CSV files")
        self.logger.info(f"✓ Generated {len(csv_files)} CSV files for email workflow")
        
        # Send separate emails for each CSV
        sent_subjects = []
        
        for i, csv_file in enumerate(csv_files, 1):
            subject = self.create_test_email_subject(f"Multiple CSV Test {i}")
            sent_subjects.append(subject)
            
            success = self.email_manager.send_email_with_csv_attachment(
                to_address=self.get_config_value('email.test_receiver_address'),
                subject=subject,
                body=f"This is CSV file {i} of {len(csv_files)} in the multiple CSV workflow test.",
                csv_file_path=csv_file
            )
            
            self.assertTrue(success, f"Failed to send email {i}")
            self.logger.info(f"✓ Sent email {i}/{len(csv_files)}")
            
            # Small delay between sends
            time.sleep(2)
        
        # Verify all emails were received
        for i, subject in enumerate(sent_subjects, 1):
            email_details = self.assert_email_sent_and_received(subject, timeout_seconds=90)
            self.logger.info(f"✓ Received email {i}/{len(sent_subjects)}")
            
            # Verify attachment
            attachments = email_details.get('attachments', [])
            self.assertGreater(len(attachments), 0, f"No attachments in email {i}")
    
    def test_05_directory_scanning_simulation(self):
        """Test 5: Simulate directory scanning and processing workflow."""
        self.logger.info("=== TEST 5: Directory Scanning Simulation ===")
        
        # Set up scan directory with test files
        scan_dir = self.temp_manager.get_temp_dir('scan')
        
        # Generate CSV files in scan directory
        csv_files = []
        for i in range(3):
            csv_file = self.data_generator.generate_test_csv(
                filename=f"scan_test_{i+1}.csv",
                output_dir=scan_dir,
                row_count=5
            )
            csv_files.append(csv_file)
        
        self.logger.info(f"✓ Created {len(csv_files)} files in scan directory")
        
        # Verify directory contents
        self.assertTrue(self.verify_file_count(scan_dir, 3, timeout_seconds=10))
        self.logger.info("✓ Directory file count verified")
        
        # Simulate processing each file
        processed_files = []
        
        for csv_file in csv_files:
            # Verify file structure
            is_valid = self.data_generator.verify_csv_structure(csv_file)
            self.assertTrue(is_valid, f"Invalid CSV structure: {csv_file}")
            
            # Move to processed directory (simulate archiving)
            archive_dir = self.temp_manager.get_temp_dir('archive')
            processed_path = self.temp_manager.copy_file_to_dir(
                csv_file, 'archive', new_name=f"processed_{os.path.basename(csv_file)}"
            )
            processed_files.append(processed_path)
            
            self.logger.info(f"✓ Processed and archived: {os.path.basename(csv_file)}")
        
        # Verify all files were processed
        self.assertEqual(len(processed_files), 3, "Not all files were processed")
        self.assertTrue(self.verify_file_count(archive_dir, 3, timeout_seconds=10))
        self.logger.info("✓ All files processed and archived")
    
    def test_06_error_handling_and_recovery(self):
        """Test 6: Error handling and recovery scenarios."""
        self.logger.info("=== TEST 6: Error Handling and Recovery ===")
        
        # Test invalid email address handling
        invalid_subject = self.create_test_email_subject("Invalid Email Test")
        
        success = self.email_manager.send_simple_email(
            to_address="invalid_email_address",
            subject=invalid_subject,
            body="This should fail gracefully."
        )
        
        self.assertFalse(success, "Expected failure for invalid email address")
        self.logger.info("✓ Invalid email address handled gracefully")
        
        # Test missing file attachment
        non_existent_file = os.path.join(self.temp_manager.get_temp_dir('generated'), "nonexistent.csv")
        
        missing_file_subject = self.create_test_email_subject("Missing File Test")
        
        success = self.email_manager.send_email_with_csv_attachment(
            to_address=self.get_config_value('email.test_receiver_address'),
            subject=missing_file_subject,
            body="This should fail gracefully due to missing attachment.",
            csv_file_path=non_existent_file
        )
        
        self.assertFalse(success, "Expected failure for missing attachment file")
        self.logger.info("✓ Missing attachment file handled gracefully")
        
        # Test CSV generation with invalid parameters
        try:
            invalid_csv = self.data_generator.generate_test_csv(
                filename="",  # Invalid empty filename
                output_dir="/invalid/path",  # Invalid directory
                row_count=-1  # Invalid row count
            )
            self.fail("Expected exception for invalid CSV generation parameters")
        except (ValueError, OSError) as e:
            self.logger.info(f"✓ Invalid CSV parameters handled gracefully: {e}")
    
    def test_07_performance_and_timeout_handling(self):
        """Test 7: Performance characteristics and timeout handling."""
        self.logger.info("=== TEST 7: Performance and Timeout Handling ===")
        
        # Test email timeout handling
        start_time = time.time()
        
        # Send email and measure time
        subject = self.create_test_email_subject("Performance Test")
        
        success = self.email_manager.send_simple_email(
            to_address=self.get_config_value('email.test_receiver_address'),
            subject=subject,
            body="Performance test email to measure sending time."
        )
        
        send_time = time.time() - start_time
        
        self.assertTrue(success, "Performance test email failed to send")
        self.assertLess(send_time, 30, f"Email sending took too long: {send_time}s")
        self.logger.info(f"✓ Email sent in {send_time:.2f} seconds")
        
        # Test email receipt timeout
        start_time = time.time()
        
        email_details = self.assert_email_sent_and_received(subject, timeout_seconds=60)
        
        receive_time = time.time() - start_time
        self.assertLess(receive_time, 60, f"Email receiving took too long: {receive_time}s")
        self.logger.info(f"✓ Email received in {receive_time:.2f} seconds")
        
        # Test bulk CSV generation performance
        start_time = time.time()
        
        bulk_csv_files = self.data_generator.generate_multiple_csvs(
            output_dir=self.temp_manager.get_temp_dir('generated'),
            file_count=5
        )
        
        generation_time = time.time() - start_time
        
        self.assertEqual(len(bulk_csv_files), 5, "Not all bulk CSV files generated")
        self.assertLess(generation_time, 30, f"Bulk CSV generation took too long: {generation_time}s")
        self.logger.info(f"✓ Generated 5 CSV files in {generation_time:.2f} seconds")
    
    def test_08_end_to_end_complete_workflow(self):
        """Test 8: Complete end-to-end workflow simulation."""
        self.logger.info("=== TEST 8: Complete End-to-End Workflow ===")
        
        # Step 1: Generate source data
        source_files = self.data_generator.generate_multiple_csvs(
            output_dir=self.temp_manager.get_temp_dir('raw'),
            file_count=2
        )
        
        self.assertEqual(len(source_files), 2, "Source data generation failed")
        self.logger.info("✓ Step 1: Source data generated")
        
        # Step 2: Process files (simulate main processing)
        processed_files = []
        output_dir = self.temp_manager.get_temp_dir('output')
        
        for i, source_file in enumerate(source_files, 1):
            # Simulate processing by copying with new name
            processed_name = f"processed_report_{i}.csv"
            processed_file = self.temp_manager.copy_file_to_dir(
                source_file, 'output', new_name=processed_name
            )
            processed_files.append(processed_file)
        
        self.assertEqual(len(processed_files), 2, "File processing failed")
        self.logger.info("✓ Step 2: Files processed")
        
        # Step 3: Send processed files via email
        email_subjects = []
        
        for i, processed_file in enumerate(processed_files, 1):
            subject = self.create_test_email_subject(f"End-to-End Report {i}")
            email_subjects.append(subject)
            
            success = self.email_manager.send_email_with_csv_attachment(
                to_address=self.get_config_value('email.test_receiver_address'),
                subject=subject,
                body=f"End-to-end integration test report {i} of {len(processed_files)}.",
                csv_file_path=processed_file
            )
            
            self.assertTrue(success, f"Failed to send report {i}")
            time.sleep(3)  # Delay between sends
        
        self.logger.info("✓ Step 3: Reports sent via email")
        
        # Step 4: Verify all emails received
        for i, subject in enumerate(email_subjects, 1):
            email_details = self.assert_email_sent_and_received(subject, timeout_seconds=120)
            
            # Verify attachment
            attachments = email_details.get('attachments', [])
            self.assertGreater(len(attachments), 0, f"No attachment in report {i}")
            
            self.logger.info(f"✓ Report {i} received and verified")
        
        # Step 5: Archive source files
        archive_dir = self.temp_manager.get_temp_dir('archive')
        archived_files = []
        
        for source_file in source_files:
            archived_file = self.temp_manager.copy_file_to_dir(
                source_file, 'archive', new_name=f"archived_{os.path.basename(source_file)}"
            )
            archived_files.append(archived_file)
        
        self.assertEqual(len(archived_files), 2, "Archiving failed")
        self.logger.info("✓ Step 5: Source files archived")
        
        # Step 6: Verify complete workflow
        self.assertTrue(self.verify_file_count(self.temp_manager.get_temp_dir('raw'), 2))
        self.assertTrue(self.verify_file_count(self.temp_manager.get_temp_dir('output'), 2))
        self.assertTrue(self.verify_file_count(self.temp_manager.get_temp_dir('archive'), 2))
        
        self.logger.info("✓ Complete end-to-end workflow verified successfully")

if __name__ == '__main__':
    # Configure logging for test run
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('integration_test_run.log')
        ]
    )
    
    # Run tests
    unittest.main(verbosity=2)
