import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import seaborn as sns
from collections import Counter
import argparse
import time
import os

class RadiusLogMonitor:
    def __init__(self, log_file_path="./logs/radius.log"):
        self.log_file_path = log_file_path
        self.auth_pattern = re.compile(
            r'(?P<timestamp>\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)\s*:\s*Auth:\s*\(\d+\)\s*(?P<status>.*?):\s*\[(?P<username>[^\]]+)\]'
        )
        
    def parse_log_line(self, line):
        """Parse a single log line and extract relevant information."""
        match = self.auth_pattern.search(line)
        if match:
            timestamp_str = match.group('timestamp')
            status = match.group('status').strip()
            username = match.group('username')
            
            # Parse timestamp
            try:
                timestamp = datetime.strptime(timestamp_str, '%a %b %d %H:%M:%S %Y')
            except ValueError:
                print(f"Failed to parse timestamp: {timestamp_str}")
                return None
                
            # Determine if login was successful or failed
            auth_result = 'Success' if ('Login OK' in status or 'Access-Accept' in status) else 'Failed'
            
            return {
                'timestamp': timestamp,
                'username': username,
                'status': status,
                'auth_result': auth_result,
                'request_type': 'Auth'
            }
        else:
            print(f"No match for line: {line.strip()}")
        return None
    
    def read_logs(self, since_hours=24):
        """Read and parse log file for authentication entries."""
        auth_logs = []
        if not os.path.exists(self.log_file_path):
            print(f"Log file not found: {self.log_file_path}")
            return pd.DataFrame()
        
        try:
            with open(self.log_file_path, 'r') as file:
                for line in file:
                    if 'Auth:' in line:
                        parsed = self.parse_log_line(line)
                        print(f'{parsed} --------')
                        if parsed:
                            auth_logs.append(parsed)
        except Exception as e:
            print(f"Error reading log file: {e}")
            return pd.DataFrame()
            
        df = pd.DataFrame(auth_logs)
        
        if not df.empty:
            # Filter by time if specified
            if since_hours:
                cutoff_time = datetime.now() - pd.Timedelta(hours=since_hours)
                df = df[df['timestamp'] >= cutoff_time]
                
        return df
    
    def create_timeline_plot(self, df):
        """Create a timeline plot of authentication attempts."""
        if df.empty:
            print("No data to plot")
            return
            
        plt.figure(figsize=(15, 8))
        
        # Separate successful and failed attempts
        success_df = df[df['auth_result'] == 'Success']
        failed_df = df[df['auth_result'] == 'Failed']
        
        plt.subplot(2, 1, 1)
        if not success_df.empty:
            plt.scatter(success_df['timestamp'], success_df['username'], 
                       color='green', alpha=0.7, label='Successful', s=50)
        if not failed_df.empty:
            plt.scatter(failed_df['timestamp'], failed_df['username'], 
                       color='red', alpha=0.7, label='Failed', s=50)
        
        plt.title('FreeRADIUS Authentication Timeline')
        plt.xlabel('Time')
        plt.ylabel('Username')
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        # Authentication attempts over time
        plt.subplot(2, 1, 2)
        df_hourly = df.set_index('timestamp').resample('H').size()
        plt.plot(df_hourly.index, df_hourly.values, marker='o', linewidth=2)
        plt.title('Authentication Attempts per Hour')
        plt.xlabel('Time')
        plt.ylabel('Number of Attempts')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def create_user_analysis(self, df):
        """Create user-based analysis plots."""
        if df.empty:
            print("No data to analyze")
            return
            
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Most active users
        user_counts = df['username'].value_counts().head(10)
        axes[0, 0].bar(user_counts.index, user_counts.values)
        axes[0, 0].set_title('Top 10 Most Active Users')
        axes[0, 0].set_xlabel('Username')
        axes[0, 0].set_ylabel('Authentication Attempts')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Success vs Failed ratio
        auth_results = df['auth_result'].value_counts()
        colors = ['green' if x == 'Success' else 'red' for x in auth_results.index]
        axes[0, 1].pie(auth_results.values, labels=auth_results.index, 
                       autopct='%1.1f%%', colors=colors)
        axes[0, 1].set_title('Authentication Success Rate')
        
        # Failed attempts by user
        failed_users = df[df['auth_result'] == 'Failed']['username'].value_counts().head(10)
        if not failed_users.empty:
            axes[1, 0].bar(failed_users.index, failed_users.values, color='red', alpha=0.7)
            axes[1, 0].set_title('Top 10 Users with Failed Attempts')
            axes[1, 0].set_xlabel('Username')
            axes[1, 0].set_ylabel('Failed Attempts')
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Authentication attempts by hour of day
        df['hour'] = df['timestamp'].dt.hour
        hourly_attempts = df['hour'].value_counts().sort_index()
        axes[1, 1].plot(hourly_attempts.index, hourly_attempts.values, marker='o')
        axes[1, 1].set_title('Authentication Attempts by Hour of Day')
        axes[1, 1].set_xlabel('Hour')
        axes[1, 1].set_ylabel('Number of Attempts')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def create_heatmap(self, df):
        """Create a heatmap of authentication attempts."""
        if df.empty:
            print("No data for heatmap")
            return
            
        # Create hour and day columns
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.day_name()
        
        # Create pivot table for heatmap
        heatmap_data = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
        
        # Reorder days
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex([day for day in day_order if day in heatmap_data.index])
        
        plt.figure(figsize=(15, 6))
        sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='d', cbar_kws={'label': 'Authentication Attempts'})
        plt.title('Authentication Attempts Heatmap (Day vs Hour)')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        plt.tight_layout()
        plt.show()
    
    def print_summary(self, df):
        """Print a summary of the authentication logs."""
        if df.empty:
            print("No authentication data found")
            return
            
        print("=" * 50)
        print("FREERADIUS AUTHENTICATION LOG SUMMARY")
        print("=" * 50)
        print(f"Total authentication attempts: {len(df)}")
        print(f"Successful authentications: {len(df[df['auth_result'] == 'Success'])}")
        print(f"Failed authentications: {len(df[df['auth_result'] == 'Failed'])}")
        print(f"Success rate: {len(df[df['auth_result'] == 'Success']) / len(df) * 100:.1f}%")
        print(f"Unique users: {df['username'].nunique()}")
        print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print()
        
        print("Top 5 most active users:")
        print(df['username'].value_counts().head().to_string())
        print()
        
        print("Top 5 users with failed attempts:")
        failed_users = df[df['auth_result'] == 'Failed']['username'].value_counts()
        if not failed_users.empty:
            print(failed_users.head().to_string())
        else:
            print("No failed attempts found")
    
    def monitor_live(self, interval=60):
        """Monitor logs in real-time and update visualizations."""
        print(f"Starting live monitoring of {self.log_file_path}")
        print(f"Updating every {interval} seconds. Press Ctrl+C to stop.")
        
        try:
            while True:
                df = self.read_logs(since_hours=1)  # Last hour
                if not df.empty:
                    plt.clf()
                    self.create_timeline_plot(df)
                    plt.pause(1)
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping live monitoring...")

def main():
    parser = argparse.ArgumentParser(description='FreeRADIUS Log Monitor and Visualizer')
    parser.add_argument('--log-file', default='./logs/radius.log', 
                       help='Path to FreeRADIUS log file')
    parser.add_argument('--hours', type=int, default=24, 
                       help='Number of hours to analyze (default: 24)')
    parser.add_argument('--live', action='store_true', 
                       help='Enable live monitoring mode')
    parser.add_argument('--interval', type=int, default=60, 
                       help='Update interval for live monitoring in seconds (default: 60)')
    
    args = parser.parse_args()
    
    monitor = RadiusLogMonitor(args.log_file)
    
    if args.live:
        monitor.monitor_live(args.interval)
    else:
        # Read and analyze logs
        df = monitor.read_logs(since_hours=args.hours)
        
        # Print summary
        monitor.print_summary(df)
        
        if not df.empty:
            # Create visualizations
            monitor.create_timeline_plot(df)
            monitor.create_user_analysis(df)
            monitor.create_heatmap(df)
        else:
            print("No authentication data found in the specified time range.")

if __name__ == "__main__":
    main() 