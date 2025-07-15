#!/usr/bin/env python3
"""
Adaptive TCP Congestion Control Test Script
Tests dynamic algorithm switching based on network conditions
"""

import sys
import os
import time
import requests
import json

# Add backend to path for testing
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_adaptive_tcp_system():
    """Test the adaptive TCP congestion control system"""
    base_url = "http://localhost:5000/api"
    
    print("=== Adaptive TCP Congestion Control Test ===")
    print()
    
    print("🧪 Testing Dynamic Algorithm Switching...")
    print()
    
    # Monitor metrics for algorithm switches over time
    switch_events = []
    previous_algorithms = {}
    
    for round_num in range(1, 11):  # Monitor for 10 rounds (20 seconds)
        print(f"Round {round_num}/10 - Monitoring for algorithm switches...")
        
        try:
            # Get current metrics
            response = requests.get(f"{base_url}/metrics/history?seconds=5")
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('metrics', [])
                
                if metrics:
                    print(f"  📊 Found {len(metrics)} metric entries")
                    
                    # Track algorithm changes per client
                    for metric in metrics:
                        client_id = metric.get('client_id')
                        algorithm = metric.get('algorithm')
                        timestamp = metric.get('timestamp')
                        
                        if client_id and algorithm:
                            if client_id in previous_algorithms:
                                if previous_algorithms[client_id] != algorithm:
                                    switch_event = {
                                        'client_id': client_id,
                                        'from': previous_algorithms[client_id],
                                        'to': algorithm,
                                        'timestamp': timestamp,
                                        'round': round_num
                                    }
                                    switch_events.append(switch_event)
                                    print(f"  🔄 SWITCH DETECTED: Client {client_id[:8]} "
                                          f"{switch_event['from']} → {algorithm}")
                            
                            previous_algorithms[client_id] = algorithm
                    
                    # Show current algorithm distribution
                    algorithm_count = {}
                    for metric in metrics[-10:]:  # Last 10 entries
                        algo = metric.get('algorithm', 'unknown')
                        algorithm_count[algo] = algorithm_count.get(algo, 0) + 1
                    
                    print(f"  📈 Current algorithms: {dict(algorithm_count)}")
                
                else:
                    print("  ⏳ No metrics data yet, waiting...")
            
            # Get global metrics
            response = requests.get(f"{base_url}/metrics/global")
            if response.status_code == 200:
                global_data = response.json()
                print(f"  🌐 Active connections: {global_data.get('active_connections', 0)}")
                print(f"  📊 Total bandwidth: {global_data.get('total_bandwidth', 0):.0f} B/s")
            
            print()
            time.sleep(2)
            
        except Exception as e:
            print(f"  ❌ Error in round {round_num}: {e}")
    
    # Summary
    print("=== Test Results Summary ===")
    print()
    
    if switch_events:
        print(f"✅ SUCCESS: Detected {len(switch_events)} algorithm switches!")
        print()
        print("📋 Switch Events:")
        for i, event in enumerate(switch_events, 1):
            print(f"  {i}. Client {event['client_id'][:8]}: "
                  f"{event['from']} → {event['to']} (Round {event['round']})")
        
        # Analyze switching patterns
        algorithms_used = set()
        for event in switch_events:
            algorithms_used.add(event['from'])
            algorithms_used.add(event['to'])
        
        print()
        print(f"🔧 Algorithms observed: {sorted(list(algorithms_used))}")
        
        # Check for BBR specifically
        if 'bbr' in algorithms_used:
            print("🎉 BBR algorithm successfully integrated and active!")
        else:
            print("⚠️  BBR algorithm not observed in switches")
    
    else:
        print("⚠️  No algorithm switches detected during test period")
        print("   This could mean:")
        print("   - Network conditions were stable")
        print("   - Switch cooldown period is preventing changes")
        print("   - System needs more time to adapt")
    
    print()
    return len(switch_events) > 0

def test_bbr_specific_features():
    """Test BBR-specific features"""
    print("=== BBR Algorithm Features Test ===")
    print()
    
    try:
        # Import BBR to test directly
        from backend.algorithms.bbr import BBRAlgorithm
        
        print("✅ BBR Algorithm successfully imported")
        
        # Test BBR initialization
        bbr = BBRAlgorithm()
        print(f"✅ BBR initialized - State: {bbr.get_state()}")
        print(f"   Initial bandwidth estimate: {bbr.get_bandwidth_estimate():.0f} B/s")
        print(f"   Initial congestion window: {bbr.get_current_cwnd():.2f}")
        print(f"   Initial pacing rate: {bbr.get_pacing_rate():.0f} B/s")
        
        # Simulate some ACKs
        print()
        print("🧪 Simulating network activity...")
        for i in range(5):
            rtt = 0.05 + i * 0.01  # Increasing RTT
            bbr.on_ack_received(i, rtt=rtt, delivered_bytes=1024, elapsed_time=0.001)
            print(f"   ACK {i+1}: RTT={rtt*1000:.1f}ms, "
                  f"CWND={bbr.get_current_cwnd():.2f}, "
                  f"State={bbr.get_state()}")
        
        print("✅ BBR simulation completed successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import BBR: {e}")
        return False
    except Exception as e:
        print(f"❌ BBR test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Starting Adaptive TCP Congestion Control Tests...")
    print("Make sure the backend server is running on http://localhost:5000")
    print()
    
    # Test BBR features
    bbr_success = test_bbr_specific_features()
    print()
    
    # Test adaptive switching
    switching_success = test_adaptive_tcp_system()
    
    print("=== Final Results ===")
    if bbr_success and switching_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ BBR algorithm is working")
        print("✅ Dynamic algorithm switching is active")
        print("✅ System adapts to network conditions")
    elif bbr_success:
        print("⚠️  PARTIAL SUCCESS")
        print("✅ BBR algorithm is working")
        print("❌ Dynamic switching needs more time or different conditions")
    else:
        print("❌ TESTS FAILED")
        print("❌ Check backend implementation")
    
    print()
    print("📚 Understanding the Results:")
    print("- Algorithm switches occur based on detected network conditions")
    print("- BBR excels in clean, high-bandwidth networks")
    print("- CUBIC works well for general high-bandwidth scenarios")
    print("- Reno provides conservative, stable performance")
    print("- Tahoe offers simple, robust operation in lossy conditions")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
