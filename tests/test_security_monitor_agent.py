import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.security_monitor_agent import SecurityMonitorAgent

def test_agent_initialization():
    agent = SecurityMonitorAgent()
    assert agent.name == "SecurityMonitorAgent"
    assert len(agent.monitoring_zones) == 0
    assert len(agent.active_alerts) == 0
    assert "police" in agent.emergency_contacts
    assert "ambulance" in agent.emergency_contacts

def test_start_monitoring():
    agent = SecurityMonitorAgent()
    result = agent.execute(
        "Start monitoring",
        zone="entrance",
        camera_id="cam_01"
    )
    assert result["status"] == "success"
    assert result["monitoring_active"] == True
    assert "entrance" in agent.monitoring_zones

def test_threat_detection_low_confidence():
    agent = SecurityMonitorAgent()
    result = agent.execute(
        "Analyze threat",
        threat_type="suspicious_activity",
        confidence=0.5,
        zone="parking"
    )
    assert result["status"] == "success"
    assert result["analysis"]["requires_action"] == False

def test_threat_detection_high_confidence():
    agent = SecurityMonitorAgent()
    result = agent.execute(
        "Analyze threat",
        threat_type="intrusion",
        confidence=0.9,
        zone="entrance"
    )
    assert result["status"] == "success"
    assert result["analysis"]["requires_action"] == True
    assert result["analysis"]["threat_level"] == "high"

def test_critical_threat_auto_emergency():
    agent = SecurityMonitorAgent()
    result = agent.execute(
        "Analyze threat",
        threat_type="fire",
        confidence=0.95,
        zone="shop_floor"
    )
    assert result["status"] == "success"
    assert result["analysis"]["threat_level"] == "critical"
    assert "emergency_called" in result["analysis"]

def test_send_alert():
    agent = SecurityMonitorAgent()
    result = agent.execute(
        "Send alert",
        threat_type="intrusion",
        zone="entrance",
        confidence=0.9
    )
    assert result["status"] == "success"
    assert "alert_id" in result
    assert len(agent.alert_history) == 1

def test_emergency_call_police():
    agent = SecurityMonitorAgent()
    result = agent.execute(
        "Initiate emergency call",
        threat_type="intrusion",
        zone="entrance"
    )
    assert result["status"] == "success"
    assert result["service_called"] == "police"
    assert "call_id" in result

def test_emergency_call_ambulance():
    agent = SecurityMonitorAgent()
    result = agent.execute(
        "Initiate emergency call",
        threat_type="fall_detection",
        zone="shop_floor"
    )
    assert result["status"] == "success"
    assert result["service_called"] == "ambulance"

def test_emergency_call_fire():
    agent = SecurityMonitorAgent()
    result = agent.execute(
        "Initiate emergency call",
        threat_type="fire",
        zone="kitchen"
    )
    assert result["status"] == "success"
    assert result["service_called"] == "fire"

def test_configure_emergency_contacts():
    agent = SecurityMonitorAgent()
    agent.configure_emergency_contacts({
        "owner": {"number": "+91-9876543210", "enabled": True}
    })
    assert agent.emergency_contacts["owner"]["number"] == "+91-9876543210"

def test_add_monitoring_zone():
    agent = SecurityMonitorAgent()
    result = agent.add_monitoring_zone("parking", "cam_02")
    assert result["status"] == "success"
    assert "parking" in agent.monitoring_zones

def test_get_monitoring_status():
    agent = SecurityMonitorAgent()
    agent.execute("Start monitoring", zone="entrance", camera_id="cam_01")
    result = agent.execute("Get monitoring status")
    assert result["status"] == "success"
    assert "monitoring_zones" in result
    assert len(result["monitoring_zones"]) > 0

def test_alert_history():
    agent = SecurityMonitorAgent()
    agent.execute("Send alert", threat_type="intrusion", zone="entrance", confidence=0.9)
    agent.execute("Send alert", threat_type="fire", zone="kitchen", confidence=0.95)
    history = agent.get_alert_history(limit=5)
    assert len(history) == 2

def test_clear_alert():
    agent = SecurityMonitorAgent()
    result = agent.execute("Send alert", threat_type="intrusion", zone="entrance", confidence=0.9)
    alert_id = result["alert_id"]
    clear_result = agent.clear_alert(alert_id)
    assert clear_result["status"] == "success"
    assert len(agent.active_alerts) == 0

def test_threat_level_mapping():
    agent = SecurityMonitorAgent()
    assert agent.threat_levels["fire"] == "critical"
    assert agent.threat_levels["intrusion"] == "high"
    assert agent.threat_levels["suspicious_activity"] == "medium"

def test_multiple_zones_monitoring():
    agent = SecurityMonitorAgent()
    zones = [("entrance", "cam_01"), ("parking", "cam_02"), ("shop_floor", "cam_03")]
    
    for zone, camera in zones:
        result = agent.execute("Start monitoring", zone=zone, camera_id=camera)
        assert result["status"] == "success"
    
    assert len(agent.monitoring_zones) == 3
