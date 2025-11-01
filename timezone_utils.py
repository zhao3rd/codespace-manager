"""
时间处理工具模块 - 统一使用东八区（北京时间，UTC+8）
为Streamlit应用提供统一的时间处理功能
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
import os


# 东八区时区定义
BEIJING_TZ = timezone(timedelta(hours=8))

# 东八区时区名称
BEIJING_TZ_NAME = "Asia/Shanghai"


def get_beijing_time() -> datetime:
    """
    获取东八区当前时间

    Returns:
        datetime: 带时区信息的东八区当前时间
    """
    return datetime.now(BEIJING_TZ)


def to_beijing_time(dt: datetime) -> datetime:
    """
    将任意时间转换为东八区时间

    Args:
        dt: 输入的时间对象（可带时区或不带时区）

    Returns:
        datetime: 转换为东八区的时间对象（无时区信息，但值为东八区时间）
    """
    if dt.tzinfo is None:
        # 如果是naive datetime，假设为东八区时间
        # 这种处理方式保持向后兼容性
        return dt.replace(tzinfo=BEIJING_TZ).replace(tzinfo=None)
    else:
        # 如果是aware datetime，转换为东八区
        return dt.astimezone(BEIJING_TZ).replace(tzinfo=None)


def format_beijing_time(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """
    格式化时间为东八区字符串

    Args:
        dt: 时间对象
        format_str: 时间格式字符串

    Returns:
        str: 格式化后的东八区时间字符串
    """
    beijing_dt = to_beijing_time(dt)
    return beijing_dt.strftime(format_str)


def parse_datetime_to_beijing(dt_str: str, assume_beijing: bool = True) -> datetime:
    """
    解析时间字符串为东八区时间

    Args:
        dt_str: 时间字符串（ISO格式或其他格式）
        assume_beijing: 如果字符串无时区信息，是否假设为东八区时间

    Returns:
        datetime: 东八区时间对象（无时区信息，但值为东八区时间）
    """
    try:
        # 尝试解析ISO格式
        if 'T' in dt_str and ('+' in dt_str or 'Z' in dt_str):
            # 处理带时区信息的ISO格式
            if dt_str.endswith('Z'):
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                dt = datetime.fromisoformat(dt_str)
            return to_beijing_time(dt)
        else:
            # 处理无时区信息的时间
            dt = datetime.fromisoformat(dt_str)
            if assume_beijing:
                # 假设是东八区时间，直接返回
                return dt
            else:
                # 假设是本地时间，转换为东八区
                return to_beijing_time(dt)
    except ValueError:
        # 尝试其他常见格式
        try:
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            if assume_beijing:
                return dt
            else:
                return to_beijing_time(dt)
        except ValueError:
            # 如果都无法解析，返回当前东八区时间
            return get_beijing_time().replace(tzinfo=None)


def get_beijing_time_iso() -> str:
    """
    获取东八区当前时间的ISO格式字符串

    Returns:
        str: ISO格式的时间字符串
    """
    return get_beijing_time().isoformat()


def format_duration_for_display(hours: float) -> str:
    """
    格式化持续时间为用户友好的显示格式

    Args:
        hours: 小时数

    Returns:
        str: 格式化的持续时间字符串
    """
    if hours < 1:
        minutes = int(hours * 60)
        return f"{minutes}分钟"
    elif hours < 24:
        return f"{hours:.1f}小时"
    else:
        days = int(hours // 24)
        remaining_hours = hours % 24
        if remaining_hours < 1:
            return f"{days}天"
        else:
            return f"{days}天{remaining_hours:.1f}小时"


def calculate_elapsed_hours(start_time: datetime, end_time: Optional[datetime] = None) -> float:
    """
    计算经过的小时数（使用东八区时间）

    Args:
        start_time: 开始时间
        end_time: 结束时间，默认为当前东八区时间

    Returns:
        float: 经过的小时数
    """
    if end_time is None:
        end_time = get_beijing_time().replace(tzinfo=None)

    # 确保两个时间都是东八区时间
    start_beijing = to_beijing_time(start_time)
    end_beijing = to_beijing_time(end_time)

    elapsed = end_beijing - start_beijing
    return elapsed.total_seconds() / 3600


def is_timezone_configured() -> bool:
    """
    检查系统时区是否正确配置为东八区

    Returns:
        bool: 是否配置为东八区
    """
    try:
        # 检查环境变量
        tz_env = os.getenv('TZ', '')
        if 'Shanghai' in tz_env or 'Beijing' in tz_env or 'Chongqing' in tz_env:
            return True

        # 检查系统时区
        import time
        local_offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
        beijing_offset = -8 * 3600  # 东八区偏移（秒）

        # 允许1小时的误差范围（考虑夏令时等因素）
        return abs(local_offset - beijing_offset) <= 3600
    except Exception:
        return False


def ensure_timezone_environment() -> None:
    """
    确保环境时区设置正确
    """
    if not is_timezone_configured():
        # 尝试设置环境变量
        os.environ['TZ'] = BEIJING_TZ_NAME
        try:
            import time
            time.tzset()
        except AttributeError:
            # Windows系统可能不支持tzset
            pass


def get_log_timestamp() -> str:
    """
    获取日志时间戳（东八区格式）

    Returns:
        str: 日志时间戳，格式：YYYY-MM-DD HH:MM:SS
    """
    return format_beijing_time(get_beijing_time())


# 模块初始化时确保时区环境
ensure_timezone_environment()