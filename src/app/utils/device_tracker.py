from user_agents import parse
from fastapi import Request

class DeviceTracker:
    @staticmethod
    def get_client_ip(request: Request):
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host
        return ip

    @staticmethod
    def get_device_info(request: Request):
        user_agent_msg = request.headers.get("User-Agent", "Unknown")
        user_agent = parse(user_agent_msg)

        return {
            "ip": DeviceTracker.get_client_ip(request),
            "is_mobile": f"{user_agent.is_mobile}",
            "is_tablet": f"{user_agent.is_tablet}",
            "is_pc": f"{user_agent.is_pc}",
            "browser": f"{user_agent.browser.family} {user_agent.browser.version_string}",
            "browser_version": user_agent.browser.version_string,
            "os": f"{user_agent.os.family} {user_agent.os.version_string}",
            "os_version": f"{user_agent.os.version_string}",
            "device": f"{user_agent.device.family}"
        }