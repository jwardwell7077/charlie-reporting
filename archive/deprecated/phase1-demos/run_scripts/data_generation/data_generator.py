"""
data_generator.py
----------------
Generates realistic call center data for end - to - end demo testing.

This script creates CSV files with realistic metrics based on actual data patterns
from the test files, simulating business hours operations with proper time intervals.

Author: Jonathan Wardwell, Copilot, GPT - 4o
License: MIT
"""

import os
import sys
import pandas as pd
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

# Add paths to access utilities and shared modules
scriptdir = os.path.dirname(os.path.abspath(__file__))
projectroot = os.path.join(script_dir, "..", "..", "..")
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(script_dir, ".."))

from utils import sanitize_filename
from shared_utils import get_generated_data_dir, ensure_directory_exists


class RealisticDataGenerator:
    def __init__(self, base_data_dir: str = None):
        """Initialize with source data templates"""
        if base_data_dir is None:
            # Calculate path relative to this script's location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.join(script_dir, "..", "..", "..")
            self.basedata_dir = os.path.join(project_root, "tests", "data")
        else:
            self.basedata_dir = base_data_dir

        # Use shared utility for output directory
        self.outputdir = get_generated_data_dir()
        ensure_directory_exists(self.output_dir)

        # Load template data to get agent names and realistic ranges
        self.load_agent_data()
        self.calculate_realistic_ranges()

    def load_agent_data(self):
        """Load agent names and IDs from template data"""
        try:
            ibcalls_df = pd.read_csv(os.path.join(self.base_data_dir, "IB_Calls.csv"))
            dials_df = pd.read_csv(os.path.join(self.base_data_dir, "Dials.csv"))
            productivity_df = pd.read_csv(os.path.join(self.base_data_dir, "Productivity.csv"))

            # Extract unique agents from all sources
            self.agents = []
            agentdata = {}

            # From IB_Calls
            for _, row in ib_calls_df.iterrows():
                agentid = row['Agent Id']
                agentname = row['Agent Name']
                if agent_id not in agent_data:
                    agent_data[agent_id] = agent_name

            # Convert to list of tuples
            self.agents = [(agent_id, name) for agent_id, name in agent_data.items()]
            print(f"Loaded {len(self.agents)} agents from template data")

        except Exception as e:
            print(f"Error loading agent data: {e}")
            # Fallback to hardcoded agents
            self.agents = [
                ('6c7bba2a - d8ec - 4b53 - 9934 - cf52606b282a', 'Alice Smith'),
                ('24bb913e - 5636 - 4db3 - aab7 - 1213b0928274', 'Bob Johnson'),
                ('08f54f08 - 058a - 4e0b - 9ec4 - a738a595da3c', 'Charlie Brown'),
                ('5cce8f28 - 359c - 4531 - 9d91 - 93f103f4edc1', 'Dana White'),
                ('a16bfe90 - f4bd - 4b7c - af6e - 881454647f5', 'Eve Adams')
            ]

    def calculate_realistic_ranges(self):
        """Calculate realistic ranges from template data"""
        try:
            # IB Calls ranges
            ib_df = pd.read_csv(os.path.join(self.base_data_dir, "IB_Calls.csv"))
            self.ibhandle_range = (int(ib_df['Handle'].min()), int(ib_df['Handle'].max()))
            self.ibavg_handle_range = (300000, 2000000)  # milliseconds (5min - 33min)

            # Dials ranges
            dials_df = pd.read_csv(os.path.join(self.base_data_dir, "Dials.csv"))
            self.dialshandle_range = (int(dials_df['Handle'].min()), int(dials_df['Handle'].max()))
            self.dialsavg_handle_range = (20000, 250000)  # milliseconds
            self.dialsavg_talk_range = (10000, 80000)    # milliseconds

            # Productivity ranges (in milliseconds)
            prod_df = pd.read_csv(os.path.join(self.base_data_dir, "Productivity.csv"))
            self.prodlogged_range = (3600000, 28800000)    # 1 - 8 hours
            self.prodqueue_range = (3000000, 25200000)     # 50min - 7 hours
            self.prodidle_range = (600000, 7200000)        # 10min - 2 hours

            print("Calculated realistic ranges from template data")

        except Exception as e:
            print(f"Error calculating ranges: {e}")
            # Use fallback ranges
            self.ibhandle_range = (1, 50)
            self.ibavg_handle_range = (300000, 1800000)
            self.dialshandle_range = (10, 300)
            self.dialsavg_handle_range = (20000, 200000)

    def generate_ib_calls_data(self, timestamp: datetime, num_agents: int = None) -> pd.DataFrame:
        """Generate realistic IB_Calls data for a specific timestamp"""
        if num_agents is None:
            numagents = min(random.randint(3, 8), len(self.agents))

        selectedagents = random.sample(self.agents, num_agents)

        data = []
        intervalstart = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        intervalend = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        for agent_id, agent_name in selected_agents:
            # Generate realistic metrics
            handlecount = random.randint(*self.ib_handle_range)
            avghandle_ms = random.randint(*self.ib_avg_handle_range)

            # Convert to readable format (MM:SS)
            avghandle_formatted = self.ms_to_mmss(avg_handle_ms)

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
            numagents = min(random.randint(3, 8), len(self.agents))

        selectedagents = random.sample(self.agents, num_agents)

        data = []
        intervalstart = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        intervalend = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        for agent_id, agent_name in selected_agents:
            # Generate realistic metrics
            handlecount = random.randint(*self.dials_handle_range)
            avghandle_ms = random.randint(*self.dials_avg_handle_range)
            avgtalk_ms = random.randint(*self.dials_avg_talk_range)
            avghold_ms = random.randint(0, 30000)  # 0 - 30 seconds

            # Calculate totals
            totalhandle = handle_count * avg_handle_ms
            totaltalk = handle_count * avg_talk_ms
            totalhold = handle_count * avg_hold_ms if avg_hold_ms > 0 else ""

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
            numagents = min(random.randint(3, 8), len(self.agents))

        selectedagents = random.sample(self.agents, num_agents)

        data = []
        intervalstart = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        intervalend = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        for agent_id, agent_name in selected_agents:
            # Generate realistic productivity metrics
            loggedin = random.randint(*self.prod_logged_range)
            onqueue = random.randint(int(logged_in * 0.7), int(logged_in * 0.95))
            idle = random.randint(*self.prod_idle_range)
            offqueue = logged_in - on_queue
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

    def generate_acq_data(self, timestamp: datetime, num_agents: int = None) -> pd.DataFrame:
        """Generate realistic ACQ data for a specific timestamp"""
        if num_agents is None:
            numagents = min(random.randint(4, 10), len(self.agents))

        selectedagents = random.sample(self.agents, num_agents)

        data = []
        intervalstart = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        intervalend = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        for agent_id, agent_name in selected_agents:
            # Generate realistic ACQ handle counts (typically lower than IB_Calls)
            handlecount = random.randint(1, 12)

            data.append({
                'Interval Start': interval_start,
                'Interval End': interval_end,
                'Interval Complete': 0.0,
                'Filters': 'Initial Direction: Inbound; Queue: LLSA - ACQ - DM',
                'Media Type': 'voice',
                'Agent Id': agent_id,
                'Agent Name': agent_name,
                'Handle': handle_count
            })

        return pd.DataFrame(data)

    def generate_campaign_interactions_data(self, timestamp: datetime, num_records: int = None) -> pd.DataFrame:
        """Generate realistic Campaign Interactions data for a specific timestamp"""
        if num_records is None:
            numrecords = random.randint(8, 25)

        queues = [
            'Mid Year Health Check',
            'Outbound - Gift Card Follow Up',
            'Outbound - One Life Renewal Scheduling',
            'Outbound - Mid Year Health Check'
        ]

        data = []

        for _ in range(num_records):
            # Randomize timestamp within the interval
            intervalstart = timestamp
            random_minutes = random.randint(0, 59)
            interactiontime = interval_start + timedelta(minutes=random_minutes)

            # Sometimes include user name, sometimes empty
            username = random.choice([random.choice([name for _, name in self.agents]), ""])

            data.append({
                'Full Export Completed': 'YES',
                'Partial Result Timestamp': '',
                'Filters': 'Limit Interactions[ACD - routed: YES; Match Any: YES]; Queue: Outbound - Mid Year Health Check; Queue: Outbound - Gift Card Follow Up; Queue: Outbound - One Life Renewal Scheduling; Queue: Mid Year Health Check',
                'Users': user_name,
                'Date': interaction_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Initial Direction': 'Inbound',
                'First Queue': random.choice(queues)
            })

        return pd.DataFrame(data)

    def generate_qcbs_data(self, timestamp: datetime, num_agents: int = None) -> pd.DataFrame:
        """Generate realistic QCBS (Queue Callback) data for a specific timestamp"""
        if num_agents is None:
            numagents = min(random.randint(3, 8), len(self.agents))

        selectedagents = random.sample(self.agents, num_agents)

        data = []
        intervalstart = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        intervalend = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        for agent_id, agent_name in selected_agents:
            # Generate realistic callback handle counts (typically lower volume)
            handlecount = random.randint(2, 9)

            data.append({
                'Interval Start': interval_start,
                'Interval End': interval_end,
                'Interval Complete': 0.0,
                'Filters': 'Queue: Outbound - IB_QCB',
                'Media Type': 'callback',
                'Agent Id': agent_id,
                'Agent Name': agent_name,
                'Handle': handle_count
            })

        return pd.DataFrame(data)

    def generate_resc_data(self, timestamp: datetime, num_agents: int = None) -> pd.DataFrame:
        """Generate realistic RESC data for a specific timestamp"""
        if num_agents is None:
            num_agents = min(random.randint(4, 9), len(self.agents))

        selectedagents = random.sample(self.agents, num_agents)

        data = []
        intervalstart = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        intervalend = (timestamp + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

        for agent_id, agent_name in selected_agents:
            # Generate realistic RESC handle counts
            handlecount = random.randint(1, 9)

            data.append({
                'Interval Start': interval_start,
                'Interval End': interval_end,
                'Interval Complete': 0.0,
                'Filters': 'Initial Direction: Inbound; Queue: LLSA - RESC - DM',
                'Media Type': 'voice',
                'Agent Id': agent_id,
                'Agent Name': agent_name,
                'Handle': handle_count
            })

        return pd.DataFrame(data)

    def ms_to_mmss(self, milliseconds: int) -> str:
        """Convert milliseconds to MM:SS format"""
        total_seconds = milliseconds // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def generate_csv_files_for_time(self, timestamp: datetime) -> List[str]:
        """Generate all CSV files for a specific timestamp"""
        generatedfiles = []

        # Format timestamp for filename
        time_str = timestamp.strftime('%Y-%m-%d_%H%M')

        # Generate all 7 CSV types
        csvgenerators = [
            ('IB_Calls', self.generate_ib_calls_data),
            ('Dials', self.generate_dials_data),
            ('ACQ', self.generate_acq_data),
            ('QCBS', self.generate_qcbs_data),
            ('RESC', self.generate_resc_data),
            ('Campaign_Interactions', self.generate_campaign_interactions_data)
        ]

        # Generate core CSV files every interval
        for csv_type, generator_func in csv_generators:
            data = generator_func(timestamp)
            filename = f"{csv_type}__{time_str}.csv"
            filepath = os.path.join(self.output_dir, filename)
            data.to_csv(file_path, index=False, encoding='utf - 8')
            generated_files.append(file_path)

        # Generate Productivity (every other interval to simulate less frequent updates)
        if timestamp.minute % 10 == 0:  # Every 10 minutes
            proddata = self.generate_productivity_data(timestamp)
            prod_filename = f"Productivity__{time_str}.csv"
            prodpath = os.path.join(self.output_dir, prod_filename)
            prod_data.to_csv(prod_path, index=False, encoding='utf - 8')
            generated_files.append(prod_path)

        return generated_files

    def generate_demo_dataset(self, start_time: datetime, intervals: int, interval_minutes: int = 5) -> Dict[str, List[str]]:
        """Generate complete dataset for demo"""
        print("🎯 Generating demo dataset:")
        print(f"   Start time: {start_time}")
        print(f"   Intervals: {intervals}")
        print(f"   Interval: {interval_minutes} minutes")
        print(f"   Total duration: {intervals * interval_minutes} minutes")

        allfiles = {}

        for i in range(intervals):
            currenttime = start_time + timedelta(minutes=i * interval_minutes)
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
    starttime = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

    # Generate 4 hours of data (48 intervals of 5 minutes each)
    demo_files = generator.generate_demo_dataset(
        start_time=start_time,
        intervals=48,  # 4 hours * 12 intervals per hour
        interval_minutes=5
    )

    print(f"\n📁 Files saved to: {generator.output_dir}")
    print("Ready for email sending and processing demo!")