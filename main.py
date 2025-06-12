#!/usr/bin/env python3
"""
FreeRADIUS Log Monitor - Main Usage Examples
"""

from radius_log_monitor import RadiusLogMonitor
import os

def main():
    """
    Example usage of the FreeRADIUS Log Monitor
    """
    
    # Initialize the monitor
    # Default log path: /var/log/freeradius/radius.log
    monitor = RadiusLogMonitor()
    
    # For Docker environment, logs might be in different location
    # You can specify custom path:
    # monitor = RadiusLogMonitor("/var/log/radius/radius.log")
    
    print("FreeRADIUS Authentication Log Monitor")
    print("====================================")
    
    # Example 1: Analyze last 24 hours
    print("\n1. Analyzing last 24 hours...")
    df = monitor.read_logs(since_hours=24)
    
    if not df.empty:
        # Print summary statistics
        monitor.print_summary(df)
        
        # Create visualizations
        print("\nGenerating timeline plot...")
        monitor.create_timeline_plot(df)
        
        print("Generating user analysis...")
        monitor.create_user_analysis(df)
        
        print("Generating heatmap...")
        monitor.create_heatmap(df)
    else:
        print("No authentication data found in the last 24 hours.")
        print("\nTo test with sample data, you can create some authentication attempts:")
        print("radtest alice password123 localhost 1812 testing123")
        print("radtest bob wrongpass localhost 1812 testing123")
    
    # Example 2: Quick analysis of last hour
    print("\n2. Quick analysis of last hour...")
    recent_df = monitor.read_logs(since_hours=1)
    if not recent_df.empty:
        print(f"Found {len(recent_df)} authentication attempts in the last hour")
        print("\nUser breakdown:")
        print(recent_df['username'].value_counts().to_string())
        print("\nSuccess/Failure breakdown:")
        print(recent_df['auth_result'].value_counts().to_string())
    else:
        print("No recent authentication attempts found.")

def example_live_monitoring():
    """
    Example of how to start live monitoring
    (Uncomment to use)
    """
    # monitor = RadiusLogMonitor()
    # monitor.monitor_live(interval=30)  # Update every 30 seconds

def example_custom_analysis():
    """
    Example of custom analysis
    """
    monitor = RadiusLogMonitor()
    df = monitor.read_logs(since_hours=48)  # Last 2 days
    
    if not df.empty:
        # Custom analysis
        print("Custom Analysis:")
        print(f"Peak hour: {df['timestamp'].dt.hour.mode().iloc[0]}:00")
        
        # Find users with most failed attempts
        failed_attempts = df[df['auth_result'] == 'Failed']
        if not failed_attempts.empty:
            print(f"User with most failed attempts: {failed_attempts['username'].mode().iloc[0]}")
        
        # Authentication pattern analysis
        weekend_attempts = df[df['timestamp'].dt.weekday >= 5]
        weekday_attempts = df[df['timestamp'].dt.weekday < 5]
        
        print(f"Weekend authentication attempts: {len(weekend_attempts)}")
        print(f"Weekday authentication attempts: {len(weekday_attempts)}")

if __name__ == "__main__":
    main()
    
    # Uncomment these for additional examples:
    # example_custom_analysis()
    # example_live_monitoring()  # This will start continuous monitoring 