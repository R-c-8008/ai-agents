import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.security_monitor_agent import SecurityMonitorAgent
from datetime import datetime
import time

def main():
    print("=" * 60)
    print("Security Monitor Agent - CCTV Monitoring Demo")
    print("=" * 60)
    
    # Initialize the security agent
    agent = SecurityMonitorAgent()
    
    # Configure emergency contacts
    print("\n[1] Configuring Emergency Contacts...")
    agent.configure_emergency_contacts({
        "owner": {"number": "+91-9876543210", "enabled": True},
        "police": {"number": "100", "enabled": True},
        "ambulance": {"number": "102", "enabled": True}
    })
    print("✓ Emergency contacts configured")
    
    # Add monitoring zones
    print("\n[2] Setting Up Monitoring Zones...")
    zones = [
        ("entrance", "cam_01"),
        ("parking", "cam_02"),
        ("shop_floor", "cam_03"),
        ("cash_counter", "cam_04")
    ]
    
    for zone_name, camera_id in zones:
        agent.add_monitoring_zone(zone_name, camera_id)
        print(f"✓ Zone added: {zone_name} (Camera: {camera_id})")
    
    # Start monitoring
    print("\n[3] Starting Active Monitoring...")
    for zone_name, camera_id in zones:
        result = agent.execute(
            "Start monitoring",
            zone=zone_name,
            camera_id=camera_id
        )
        if result["status"] == "success":
            print(f"✓ Monitoring active: {zone_name}")
    
    # Simulate threat detection scenarios
    print("\n" + "=" * 60)
    print("SIMULATING THREAT DETECTION SCENARIOS")
    print("=" * 60)
    
    # Scenario 1: Suspicious activity (medium threat)
    print("\n[Scenario 1] Suspicious Activity Detected")
    result = agent.execute(
        "Detect and analyze threat",
        threat_type="suspicious_activity",
        confidence=0.75,
        zone="parking"
    )
    print(f"Status: {result['status']}")
    print(f"Threat Level: {result['analysis']['threat_level']}")
    print(f"Action Required: {result['analysis']['requires_action']}")
    
    time.sleep(1)
    
    # Scenario 2: Intrusion detected (high threat - auto alert)
    print("\n[Scenario 2] Intrusion Detected - HIGH THREAT")
    result = agent.execute(
        "Detect and analyze threat",
        threat_type="intrusion",
        confidence=0.92,
        zone="entrance"
    )
    print(f"Status: {result['status']}")
    print(f"Threat Level: {result['analysis']['threat_level']}")
    print(f"Alert Sent: {result['analysis'].get('alert_sent', False)}")
    print(f"Emergency Called: {result['analysis'].get('emergency_called', False)}")
    
    time.sleep(1)
    
    # Scenario 3: Fire detected (critical threat - emergency call)
    print("\n[Scenario 3] Fire Detected - CRITICAL THREAT")
    result = agent.execute(
        "Analyze threat",
        threat_type="fire",
        confidence=0.95,
        zone="shop_floor"
    )
    print(f"Status: {result['status']}")
    print(f"Threat Level: {result['analysis']['threat_level']}")
    print(f"Alert Sent: {result['analysis'].get('alert_sent', False)}")
    print(f"Emergency Called: {result['analysis'].get('emergency_called', False)}")
    
    time.sleep(1)
    
    # Scenario 4: Fall detection (medical emergency)
    print("\n[Scenario 4] Person Fall Detected - Medical Emergency")
    result = agent.execute(
        "Analyze threat",
        threat_type="fall_detection",
        confidence=0.88,
        zone="cash_counter"
    )
    print(f"Status: {result['status']}")
    print(f"Threat Level: {result['analysis']['threat_level']}")
    print(f"Emergency Service: Ambulance")
    
    time.sleep(1)
    
    # Scenario 5: Weapon detected (critical)
    print("\n[Scenario 5] Weapon Detected - CRITICAL THREAT")
    result = agent.execute(
        "Analyze threat",
        threat_type="weapon_detected",
        confidence=0.91,
        zone="entrance"
    )
    print(f"Status: {result['status']}")
    print(f"Threat Level: {result['analysis']['threat_level']}")
    
    # Manual emergency call
    print("\n[6] Manual Emergency Call to Police...")
    result = agent.execute(
        "Initiate emergency call",
        threat_type="violence",
        zone="shop_floor",
        priority="critical"
    )
    if result["status"] == "success":
        print(f"✓ Emergency call initiated to: {result['service_called']}")
        print(f"  Number: {result['emergency_number']}")
        print(f"  Call ID: {result['call_id']}")
        print(f"  Owner Notified: {result['owner_notified']}")
    
    # Get monitoring status
    print("\n" + "=" * 60)
    print("MONITORING STATUS SUMMARY")
    print("=" * 60)
    
    result = agent.execute("Get monitoring status")
    if result["status"] == "success":
        print(f"\nActive Monitoring Zones: {len(result['monitoring_zones'])}")
        for zone, details in result['monitoring_zones'].items():
            print(f"  - {zone}: {details['status']} (Camera: {details['camera_id']})")
            if 'threats_detected' in details:
                print(f"    Threats detected: {details['threats_detected']}")
        
        print(f"\nActive Alerts: {result['active_alerts']}")
        print(f"Total Alerts (History): {result['total_alerts']}")
    
    # Show alert history
    print("\n" + "=" * 60)
    print("RECENT ALERT HISTORY")
    print("=" * 60)
    
    history = agent.get_alert_history(limit=5)
    for idx, alert in enumerate(history, 1):
        print(f"\n[Alert {idx}] {alert['id']}")
        print(f"  Type: {alert['threat_type']}")
        print(f"  Zone: {alert['zone']}")
        print(f"  Confidence: {alert['confidence']:.2%}")
        print(f"  Time: {alert['timestamp']}")
        print(f"  Message: {alert['message']}")
    
    # Agent status
    print("\n" + "=" * 60)
    print("AGENT STATUS")
    print("=" * 60)
    status = agent.get_status()
    print(f"Agent: {status['name']}")
    print(f"Description: {status['description']}")
    print(f"Total Zones: {len(agent.monitoring_zones)}")
    print(f"Total Alerts Sent: {len(agent.alert_history)}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
