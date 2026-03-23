from .k8s_tools import restart_kubernetes_pod
from .log_tools import get_log_tools


def get_all_tools():
    return get_log_tools() + [restart_kubernetes_pod]
