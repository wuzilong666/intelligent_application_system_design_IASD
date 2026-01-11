"""
预警系统模块
用于发布天气预警
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
import config
from utils.helpers import log_message, get_alert_level_name, save_json


class WeatherAlertSystem:
    """天气预警系统"""
    
    def __init__(self):
        """初始化预警系统"""
        self.alert_config = config.ALERT_CONFIG
        self.alert_levels = config.ALERT_LEVELS
        self.alert_history = []
        self.output_dir = "outputs/alerts"
        os.makedirs(self.output_dir, exist_ok=True)
        
        log_message("预警系统初始化完成")
    
    def issue_alert(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        发布预警
        
        参数:
            detection_result: 极端天气检测结果
            
        返回:
            预警信息字典
        """
        if not detection_result.get("has_extreme", False):
            log_message("未检测到极端天气，无需发布预警")
            return {
                "issued": False,
                "message": "当前无极端天气预警"
            }
        
        log_message("准备发布天气预警")
        
        # 创建预警信息
        alert = self._create_alert_message(detection_result)
        
        # 发布预警
        self._publish_alert(alert)
        
        # 记录预警历史
        self.alert_history.append(alert)
        
        log_message(f"预警发布完成，级别: {alert['level_name']}")
        return alert
    
    def _create_alert_message(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建预警消息
        
        参数:
            detection_result: 检测结果
            
        返回:
            预警消息字典
        """
        detections = detection_result.get("detections", [])
        max_severity = detection_result.get("max_severity", 1)
        
        # 确定预警级别
        alert_level = self._determine_alert_level(max_severity)
        level_name = get_alert_level_name(alert_level)
        
        # 构建预警消息
        alert = {
            "alert_id": f"ALERT_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "level": alert_level,
            "level_name": level_name,
            "severity": max_severity,
            "events": [],
            "message": "",
            "suggestions": []
        }
        
        # 添加事件详情
        for detection in detections:
            event = {
                "type": detection["type_name"],
                "severity": detection["severity"],
                "description": detection["description"],
                "level": detection.get("level", "未知")
            }
            alert["events"].append(event)
            
            # 收集建议
            if "suggestions" in detection:
                alert["suggestions"].extend(detection["suggestions"])
        
        # 生成消息文本
        alert["message"] = self._format_alert_message(alert)
        
        return alert
    
    def _determine_alert_level(self, severity: int) -> int:
        """
        确定预警级别
        
        参数:
            severity: 严重程度 (1-4)
            
        返回:
            预警级别 (1-4)
        """
        # 直接映射严重程度到预警级别
        return min(4, max(1, severity))
    
    def _format_alert_message(self, alert: Dict[str, Any]) -> str:
        """
        格式化预警消息
        
        参数:
            alert: 预警信息
            
        返回:
            格式化的消息文本
        """
        message = f"""
{'='*60}
🚨 天气预警 - {alert['level_name']}
{'='*60}

预警编号: {alert['alert_id']}
发布时间: {alert['timestamp']}
预警级别: {alert['level_name']}

极端天气事件:
"""
        
        for i, event in enumerate(alert['events'], 1):
            message += f"\n{i}. {event['type']} ({event['level']})\n"
            message += f"   {event['description']}\n"
        
        if alert['suggestions']:
            message += f"\n{'='*60}\n"
            message += "应对建议:\n"
            for i, suggestion in enumerate(set(alert['suggestions']), 1):
                message += f"{i}. {suggestion}\n"
        
        message += f"\n{'='*60}\n"
        message += "请密切关注天气变化，做好防范措施！\n"
        message += f"{'='*60}\n"
        
        return message
    
    def _publish_alert(self, alert: Dict[str, Any]):
        """
        发布预警到各个渠道
        
        参数:
            alert: 预警信息
        """
        # 1. 控制台输出
        if self.alert_config.get("enable_console", True):
            print("\n" + alert["message"])
            log_message("预警已输出到控制台")
        
        # 2. 保存到文件
        if self.alert_config.get("enable_file", True):
            self._save_alert_to_file(alert)
        
        # 3. 邮件通知（如果启用）
        if self.alert_config.get("enable_email", False):
            self._send_email_alert(alert)
        
        # 4. 短信通知（如果启用）
        if self.alert_config.get("enable_sms", False):
            self._send_sms_alert(alert)
    
    def _save_alert_to_file(self, alert: Dict[str, Any]):
        """
        保存预警到文件
        
        参数:
            alert: 预警信息
        """
        # 保存JSON格式
        json_path = f"{self.output_dir}/{alert['alert_id']}.json"
        save_json(alert, json_path)
        
        # 保存文本格式
        txt_path = f"{self.output_dir}/{alert['alert_id']}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(alert["message"])
        
        log_message(f"预警已保存到文件: {json_path}")
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """
        发送邮件预警（示例实现）
        
        参数:
            alert: 预警信息
        """
        # 这里应该实现实际的邮件发送逻辑
        # 例如使用 smtplib 发送邮件
        log_message("邮件预警功能未启用（需要配置邮件服务器）", "WARNING")
    
    def _send_sms_alert(self, alert: Dict[str, Any]):
        """
        发送短信预警（示例实现）
        
        参数:
            alert: 预警信息
        """
        # 这里应该实现实际的短信发送逻辑
        # 例如调用短信服务API
        log_message("短信预警功能未启用（需要配置短信服务）", "WARNING")
    
    def get_alert_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取预警历史
        
        参数:
            limit: 返回的最大数量
            
        返回:
            预警历史列表
        """
        return self.alert_history[-limit:]
    
    def clear_alert_history(self):
        """清除预警历史"""
        self.alert_history = []
        log_message("预警历史已清除")
    
    def generate_alert_report(self, start_date: str = None, 
                            end_date: str = None) -> Dict[str, Any]:
        """
        生成预警统计报告
        
        参数:
            start_date: 开始日期
            end_date: 结束日期
            
        返回:
            统计报告
        """
        log_message("生成预警统计报告")
        
        # 筛选时间范围内的预警
        filtered_alerts = self.alert_history
        
        if not filtered_alerts:
            return {
                "total_alerts": 0,
                "message": "统计期间无预警记录"
            }
        
        # 统计分析
        total_alerts = len(filtered_alerts)
        
        # 按级别统计
        level_counts = {}
        for alert in filtered_alerts:
            level = alert["level_name"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # 按事件类型统计
        event_counts = {}
        for alert in filtered_alerts:
            for event in alert.get("events", []):
                event_type = event["type"]
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        report = {
            "total_alerts": total_alerts,
            "level_distribution": level_counts,
            "event_distribution": event_counts,
            "period": {
                "start": start_date or "开始",
                "end": end_date or "结束"
            },
            "generated_at": datetime.now().isoformat()
        }
        
        # 保存报告
        report_path = f"{self.output_dir}/alert_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        save_json(report, report_path)
        
        log_message(f"预警报告已生成: {report_path}")
        return report


if __name__ == "__main__":
    # 测试代码
    alert_system = WeatherAlertSystem()
    
    # 创建测试检测结果
    test_detection = {
        "has_extreme": True,
        "max_severity": 3,
        "detections": [
            {
                "type_name": "暴雨",
                "severity": 3,
                "level": "大暴雨",
                "description": "检测到大暴雨，降水量65 mm/h",
                "suggestions": [
                    "避免外出",
                    "注意防范城市内涝",
                    "检查排水系统"
                ]
            }
        ]
    }
    
    # 发布预警
    alert = alert_system.issue_alert(test_detection)
    print(f"\n✓ 预警发布测试完成")
    print(f"  预警ID: {alert.get('alert_id', 'N/A')}")
