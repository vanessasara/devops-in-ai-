import subprocess

from agents import function_tool

from ..config import Config


@function_tool
def restart_kubernetes_pod(pod_name: str, namespace: str, reason: str) -> str:
    """Restart a Kubernetes pod by deleting it. The deployment recreates it automatically.
    IMPORTANT: Always get explicit user approval with yes before calling this tool.
    Never call this tool unless the user has said yes to the recommended action.
    Input: pod_name (exact name from the logs), namespace, reason for the restart.
    """
    if not Config.K8S_ENABLED:
        return (
            f"[SIMULATED] Would execute: kubectl delete pod {pod_name} -n {namespace}\n"
            f"Reason: {reason}\n"
            f"Expected outcome: Pod will be recreated by ReplicaSet automatically.\n"
            f"To enable real execution set K8S_ENABLED=true in .env"
        )

    try:
        result = subprocess.run(
            ["kubectl", "delete", "pod", pod_name, "-n", namespace],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return (
                f"Successfully deleted pod '{pod_name}' in namespace '{namespace}'. "
                f"It will be recreated by the Deployment automatically."
            )
        return f"Error restarting pod: {result.stderr}"
    except FileNotFoundError:
        return "Error: kubectl not found. Install kubectl or set K8S_ENABLED=false in .env"
    except subprocess.TimeoutExpired:
        return "Error: kubectl command timed out after 30 seconds."
    except Exception as e:
        return f"Error: {e}"
