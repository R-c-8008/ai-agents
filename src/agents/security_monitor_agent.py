from src.agents.base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SecurityMonitorAgent(BaseAgent):
    """AI Agent for CCTV monitoring and emergency response"""
    
    def __init__(self):
        super().__init__(
            name="SecurityMonitorAgent",
            description="Monitors CCTV feeds for security threats and coordinates emergency response"
        )
        self.active_alerts = []
        self.monitoring_zones = {}
        self.emergency_contacts = {
            "police": {"number": "100", "enabled": True},
            "ambulance": {"number": "102", "enabled": True},
            "fire": {"number": "101", "enabled": True},
            "owner": {"number": "", "enabled": True}
        }
        self.threat_levels = {
            "intrusion": "high",
            "fire": "critical",
            "medical_emergency": "critical",
            "suspicious_activity": "medium",
            "unauthorized_access": "high",
            "fall_detection": "high",
            "violence": "critical",
            "weapon_detected": "critical"
        }
        self.alert_history = []
        
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """Execute security monitoring task"""
        logger.info(f"Security task: {task}")
        
        task_lower = task.lower()
        
        try:
            if "monitor" in task_lower:
                return self._start_monitoring(**kwargs)
            elif "detect" in task_lower or "analyze" in task_lower:
                return self._analyze_threat(**kwargs)
            elif "alert" in task_lower or "notify" in task_lower:
                return self._send_alert(**kwargs)
            elif "emergency" in task_lower or "call" in task_lower:
                return self._initiate_emergency_call(**kwargs)
            elif "status" in task_lower:
                return self._get_monitoring_status()
            else:
                return {
                    "status": "success",
                    "message": "Task processed",
                    "task": task
                }
        except Exception as e:
            logger.error(f"Security task failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "task": task
            }
    
    def _start_monitoring(self, **kwargs) -> Dict[str, Any]:
        """Start CCTV monitoring"""
        zone = kwargs.get('zone', 'main')
        camera_id = kwargs.get('camera_id', 'cam_01')
        
        self.monitoring_zones[zone] = {
            "camera_id": camera_id,
            "status": "active",
            "started_at": datetime.now().isoformat(),
            "threats_detected": 0
        }
        
        logger.info(f"Started monitoring zone: {zone}, camera: {camera_id}")
        
        return {
            "status": "success",
            "message": f"Monitoring started for {zone}",
            "zone": zone,
            "camera_id": camera_id,
            "monitoring_active": True
        }
    
    def _analyze_threat(self, **kwargs) -> Dict[str, Any]:
        """Analyze potential threat from CCTV feed"""
        threat_type = kwargs.get('threat_type', 'unknown')
        confidence = kwargs.get('confidence', 0.0)
        zone = kwargs.get('zone', 'main')
        frame_data = kwargs.get('frame_data', {})
        
        threat_level = self.threat_levels.get(threat_type, "low")
        
        analysis = {
            "threat_detected": confidence > 0.7,
            "threat_type": threat_type,
            "threat_level": threat_level,
            "confidence": confidence,
            "zone": zone,
            "timestamp": datetime.now().isoformat(),
            "requires_action": confidence > 0.8 and threat_level in ["high", "critical"]
        }
        
        # Auto-alert for high-confidence critical threats
        if analysis["requires_action"]:
            alert_result = self._send_alert(
                threat_type=threat_type,
                zone=zone,
                confidence=confidence
            )
            analysis["alert_sent"] = alert_result["status"] == "success"
            
            # Auto-call emergency services for critical threats
            if threat_level == "critical":
                emergency_result = self._initiate_emergency_call(
                    threat_type=threat_type,
                    zone=zone
                )
                analysis["emergency_called"] = emergency_result["status"] == "success"
        
        # Update monitoring zone stats
        if zone in self.monitoring_zones:
            self.monitoring_zones[zone]["threats_detected"] += 1
            self.monitoring_zones[zone]["last_threat"] = threat_type
        
        logger.info(f"Threat analysis: {threat_type} - {threat_level} (confidence: {confidence})")
        
        return {
            "status": "success",
            "analysis": analysis
        }
    
    def _send_alert(self, **kwargs) -> Dict[str, Any]:
        """Send alert notification"""
        threat_type = kwargs.get('threat_type', 'unknown')
        zone = kwargs.get('zone', 'unknown')
        confidence = kwargs.get('confidence', 0.0)
        message = kwargs.get('message', '')
        
        alert = {
            "id": f"alert_{len(self.alert_history) + 1}",
            "threat_type": threat_type,
            "zone": zone,
            "confidence": confidence,
            "message": message or f"{threat_type.replace('_', ' ').title()} detected in {zone}",
            "timestamp": datetime.now().isoformat(),
            "status": "sent",
            "notification_channels": []
        }
        
        # Simulate sending notifications
        channels = ["mobile_app", "email", "sms"]
        for channel in channels:
            alert["notification_channels"].append({
                "channel": channel,
                "status": "sent",
                "sent_at": datetime.now().isoformat()
            })
        
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        
        logger.warning(f"ALERT SENT: {alert['message']}")
        
        return {
            "status": "success",
            "alert_id": alert["id"],
            "message": "Alert sent successfully",
            "alert": alert
        }
    
    def _initiate_emergency_call(self, **kwargs) -> Dict[str, Any]:
        """Initiate emergency call to police/ambulance"""
        threat_type = kwargs.get('threat_type', 'unknown')
        zone = kwargs.get('zone', 'unknown')
        priority = kwargs.get('priority', 'high')
        
        # Determine which emergency service to call
        service_type = self._determine_emergency_service(threat_type)
        
        if not service_type:
            return {
                "status": "failed",
                "error": "Could not determine appropriate emergency service"
            }
        
        contact = self.emergency_contacts.get(service_type, {})
        
        if not contact.get("enabled"):
            return {
                "status": "failed",
                "error": f"{service_type} contact not enabled"
            }
        
        emergency_call = {
            "call_id": f"emergency_{len(self.alert_history) + 1}",
            "service_type": service_type,
            "number": contact["number"],
            "threat_type": threat_type,
            "zone": zone,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "status": "initiated",
            "message": f"Emergency: {threat_type.replace('_', ' ').title()} detected in {zone}. Immediate assistance required."
        }
        
        logger.critical(f"EMERGENCY CALL INITIATED: {service_type.upper()} - {emergency_call['message']}")
        
        # Also notify owner
        owner_notification = {
            "recipient": "owner",
            "number": self.emergency_contacts["owner"]["number"],
            "message": f"Emergency call made to {service_type}: {emergency_call['message']}",
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "call_id": emergency_call["call_id"],
            "service_called": service_type,
            "emergency_number": contact["number"],
            "message": f"Emergency call initiated to {service_type}",
            "emergency_call": emergency_call,
            "owner_notified": True,
            "owner_notification": owner_notification
        }
    
    def _determine_emergency_service(self, threat_type: str) -> Optional[str]:
        """Determine which emergency service to call based on threat type"""
        emergency_mapping = {
            "intrusion": "police",
            "violence": "police",
            "weapon_detected": "police",
            "unauthorized_access": "police",
            "fire": "fire",
            "medical_emergency": "ambulance",
            "fall_detection": "ambulance",
            "suspicious_activity": "police"
        }
        return emergency_mapping.get(threat_type)
    
    def _get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            "status": "success",
            "monitoring_zones": self.monitoring_zones,
            "active_alerts": len(self.active_alerts),
            "total_alerts": len(self.alert_history),
            "emergency_contacts": self.emergency_contacts
        }
    
    def configure_emergency_contacts(self, contacts: Dict[str, Dict]) -> None:
        """Configure emergency contact numbers"""
        for service, details in contacts.items():
            if service in self.emergency_contacts:
                self.emergency_contacts[service].update(details)
                logger.info(f"Updated emergency contact: {service}")
    
    def add_monitoring_zone(self, zone_name: str, camera_id: str) -> Dict[str, Any]:
        """Add a new monitoring zone"""
        self.monitoring_zones[zone_name] = {
            "camera_id": camera_id,
            "status": "inactive",
            "added_at": datetime.now().isoformat()
        }
        return {"status": "success", "zone": zone_name}
    
    def get_alert_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def clear_alert(self, alert_id: str) -> Dict[str, Any]:
        """Clear/acknowledge an active alert"""
        self.active_alerts = [a for a in self.active_alerts if a["id"] != alert_id]
        return {"status": "success", "message": f"Alert {alert_id} cleared"}
