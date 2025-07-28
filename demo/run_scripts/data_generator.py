"""
data_generator.py
----------------
Generates realistic call center data for end-to-end demo testing.

This script creates CSV files with realistic metrics based on actual data patterns
from the test files, simulating business hours operations with proper time intervals.

Author: Jonathan Wardwell, Copilot, GPT-4o
License: MIT
"""

import os
import sys
import pandas as pd
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Add src to path for access to utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from utils import sanitize_filename

class RealisticDataGenerator:
    def __init__(self, base_data_dir: str = "tests/data"):
        """Initialize with source data templates"""
        self.base_data_dir = base_data_dir
        self.output_dir = "demo/data/generated"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load template data to get agent names and realistic ranges
        self._load_agent_data()
        self._calculate_realistic_ranges()
    
    def _load_agent_data(self):
        """Load agent names and IDs from template data"""
        try:
            ib_calls_df = pd.read_csv(os.path.join(self.base_data_dir, "IB_Calls.csv"))
            dials_df = pd.read_csv(os.path.join(self.base_data_dir, "Dials.csv"))
            productivity_df = pd.read_csv(os.path.join(self.base_data_dir, "Productivity.csv"))
            
            # Extract unique agents from all sources
            self.agents = []
            agent_data = {}
            
            # From IB_Calls
            for _, row in ib_calls_df.iterrows():
                agent_id = row['Agent Id']
                agent_name = row['Agent Name']
                if agent_id not in agent_data:
                    agent_data[agent_id] = agent_name
            
            # Convert to list of tuples
            self.agents = [(agent_id, name) for agent_id, name in agent_data.items()]
            print(f"Loaded {len(self.agents)} agents from template data")
            
        except Exception as e:
            print(f"Error loading agent data: {e}")
            # Fallback to hardcoded agents
            self.agents = [
                ('6c7bba2a-d8ec-4b53-9934-cf52606b282a', 'Alice Smith'),
                ('24bb913e-5636-4db3-aab7-1213b0928274', 'Bob Johnson'),
                ('08f54f08-058a-4e0b-9ec4-a738a595da3c', 'Charlie Brown'),
                ('5cce8f28-359c-4531-9d91-93f103f4edc1', 'Dana White'),
                ('a16bfe90-f4bd-4b7c-af6e-881454647f5f', 'Eve Adams')
            ]
    
    def _calculate_realistic_ranges(self):
        """Calculate realistic ranges from template data"""
        try:
            # IB Calls ranges
            ib_df = pd.read_csv(os.path.join(self.base_data_dir, "IB_Calls.csv"))
            self.ib_handle_range = (int(ib_df['Handle'].min()), int(ib_df['Handle'].max()))
            self.ib_avg_handle_range = (300000, 2000000)  # milliseconds (5min - 33min)
            
            # Dials ranges
            dials_df = pd.read_csv(os.path.join(self.base_data_dir, "Dials.csv"))
            self.dials_handle_range = (int(dials_df['Handle'].min()), int(dials_df['Handle'].max()))
            self.dials_avg_handle_range = (20000, 250000)  # milliseconds
            self.dials_avg_talk_range = (10000, 80000)    # milliseconds
            
            # Productivity ranges (in milliseconds)
            prod_df = pd.read_csv(os.path.join(self.base_data_dir, "Productivity.csv"))
            self.prod_logged_range = (3600000, 28800000)    # 1-8 hours
            self.prod_queue_range = (3000000, 25200000)     # 50min - 7 hours
            self.prod_idle_range = (600000, 7200000)        # 10min - 2 hours
            
            print("Calculated realistic ranges from template data")
            
        except Exception as e:
            print(f"Error calculating ranges: {e}")
            # Use fallback ranges
            self.ib_handle_range = (1, 50)
            self.ib_avg_handle_range = (300000, 1800000)
            self.dials_handle_range = (10, 300)
            self.dials_avg_handle_range = (20000, 200000)
    
    def generate_ib_calls_data(self, timestamp: datetime, num_agents: int = None) -> pd.DataFrame:
        """Generate realistic IB_Calls data for a specific timestamp"""
        if num_agents is None:
            num_agents = min(random.randint(3, 8), len(self.agents))
        
        selected_agents = random.sample(self.agents, num_agents)
        
        data = []
        interval_start = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        interval_end = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        for agent_id, agent_name in selected_agents:
            # Generate realistic metrics
            handle_count = random.randint(*self.ib_handle_range)
            avg_handle_ms = random.randint(*self.ib_avg_handle_range)
            
            # Convert to readable format (MM:SS)
            avg_handle_formatted = self._ms_to_mmss(avg_handle_ms)
            
            data.append({
                'Interval Start': interval_start,
                'Interval End': interval_end,
                'Interval Complete': 0.0,
                'Filters': 'Initial Direction: Inbound; Queue: Demo Queue',
                'Media Type': 'voice',
                'Agent Id': agent_id,
                'Agent Name': agent_name,
                'Handle': handle_count,
                'Avg Handle': avg_handle_formatted
            })
        
        return pd.DataFrame(data)
    
    def generate_dials_data(self, timestamp: datetime, num_agents: int = None) -> pd.DataFrame:
        """Generate realistic Dials data for a specific timestamp"""
        if num_agents is None:
            num_agents = min(random.randint(3, 8), len(self.agents))
        
        selected_agents = random.sample(self.agents, num_agents)
        
        data = []
        interval_start = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        interval_end = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        for agent_id, agent_name in selected_agents:
            # Generate realistic metrics
            handle_count = random.randint(*self.dials_handle_range)
            avg_handle_ms = random.randint(*self.dials_avg_handle_range)
            avg_talk_ms = random.randint(*self.dials_avg_talk_range)
            avg_hold_ms = random.randint(0, 30000)  # 0-30 seconds
            
            # Calculate totals
            total_handle = handle_count * avg_handle_ms
            total_talk = handle_count * avg_talk_ms
            total_hold = handle_count * avg_hold_ms if avg_hold_ms > 0 else ""
            
            data.append({
                'Interval Start': interval_start,
                'Interval End': interval_end,
                'Interval Complete': 0.0,
                'Filters': 'Initial Direction: Outbound; Queue: Demo Outbound',
                'Media Type': 'voice',
                'Agent Id': agent_id,
                'Agent Name': agent_name,
                'Handle': handle_count,
                'Avg Handle': avg_handle_ms,
                'Avg Talk': avg_talk_ms,
                'Avg Hold': avg_hold_ms if avg_hold_ms > 0 else "",
                'Avg ACW': random.randint(5000, 30000),  # After call work
                'Total Handle': total_handle,
                'Total Talk': total_talk,
                'Total Hold': total_hold,
                'Total ACW': handle_count * random.randint(5000, 30000)
            })
        
        return pd.DataFrame(data)
    
    def generate_productivity_data(self, timestamp: datetime, num_agents: int = None) -> pd.DataFrame:
        """Generate realistic Productivity data for a specific timestamp"""
        if num_agents is None:
            num_agents = min(random.randint(3, 8), len(self.agents))
        
        selected_agents = random.sample(self.agents, num_agents)
        
        data = []
        interval_start = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        interval_end = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        
        for agent_id, agent_name in selected_agents:
            # Generate realistic productivity metrics
            logged_in = random.randint(*self.prod_logged_range)
            on_queue = random.randint(int(logged_in * 0.7), int(logged_in * 0.95))
            idle = random.randint(*self.prod_idle_range)
            off_queue = logged_in - on_queue
            interacting = on_queue - idle
            
            data.append({
                'Interval Start': interval_start,
                'Interval End': interval_end,
                'Interval Complete': 0.0,
                'Filters': '',
                'Agent Id': agent_id,
                'Agent Name': agent_name,
                'Logged In': logged_in,
                'On Queue': on_queue if on_queue > 0 else "",
                'Idle': idle if idle > 0 else "",
                'Off Queue': off_queue if off_queue > 0 else "",
                'Interacting': interacting if interacting > 0 else ""
            })
        
        return pd.DataFrame(data)
    
    def _ms_to_mmss(self, milliseconds: int) -> str:
        """Convert milliseconds to MM:SS format"""
        total_seconds = milliseconds // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def generate_csv_files_for_time(self, timestamp: datetime) -> List[str]:
        """Generate all CSV files for a specific timestamp"""
        generated_files = []
        
        # Format timestamp for filename
        time_str = timestamp.strftime('%Y-%m-%d_%H%M')
        
        # Generate IB_Calls
        ib_data = self.generate_ib_calls_data(timestamp)
        ib_filename = f"IB_Calls__{time_str}.csv"
        ib_path = os.path.join(self.output_dir, ib_filename)
        ib_data.to_csv(ib_path, index=False)
        generated_files.append(ib_path)
        
        # Generate Dials
        dials_data = self.generate_dials_data(timestamp)
        dials_filename = f"Dials__{time_str}.csv"
        dials_path = os.path.join(self.output_dir, dials_filename)
        dials_data.to_csv(dials_path, index=False)
        generated_files.append(dials_path)
        
        # Generate Productivity (every other interval to simulate less frequent updates)
        if timestamp.minute % 10 == 0:  # Every 10 minutes
            prod_data = self.generate_productivity_data(timestamp)
            prod_filename = f"Productivity__{time_str}.csv"
            prod_path = os.path.join(self.output_dir, prod_filename)
            prod_data.to_csv(prod_path, index=False)
            generated_files.append(prod_path)
        
        return generated_files
    
    def generate_demo_dataset(self, start_time: datetime, intervals: int, interval_minutes: int = 5) -> Dict[str, List[str]]:
        """Generate complete dataset for demo"""
        print(f"🎯 Generating demo dataset:")
        print(f"   Start time: {start_time}")
        print(f"   Intervals: {intervals}")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Total duration: {intervals * interval_minutes} minutes")
        
        all_files = {}
        
        for i in range(intervals):
            current_time = start_time + timedelta(minutes=i * interval_minutes)
            print(f"\n📊 Generating data for {current_time.strftime('%H:%M')}...")
            
            files = self.generate_csv_files_for_time(current_time)
            time_key = current_time.strftime('%H:%M')
            all_files[time_key] = files
            
            for file_path in files:
                filename = os.path.basename(file_path)
                print(f"   ✓ {filename}")
        
        print(f"\n✅ Generated {sum(len(files) for files in all_files.values())} CSV files")
        return all_files


if __name__ == "__main__":
    print("Realistic Data Generator Demo")
    print("=" * 50)
    
    # Generate data for demo (9 AM - 12 PM, every 5 minutes)
    generator = RealisticDataGenerator()
    
    # Start at 9 AM today
    start_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Generate 4 hours of data (48 intervals of 5 minutes each)
    demo_files = generator.generate_demo_dataset(
        start_time=start_time,
        intervals=48,  # 4 hours * 12 intervals per hour
        interval_minutes=5
    )
    
    print(f"\n📁 Files saved to: {generator.output_dir}")
    print("Ready for email sending and processing demo!")
