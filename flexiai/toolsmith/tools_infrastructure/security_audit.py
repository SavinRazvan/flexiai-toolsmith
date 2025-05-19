# FILE: flexiai/toolsmith/tools_infrastructure/security_audit.py

import os
import platform
import shutil
import socket
import subprocess
import psutil
import logging
import json
import functools
import re
import ipaddress
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _audit_log(func):
    """
    Decorator to wrap SecurityAudit methods to log a structured JSON record
    after each operation, with timing, parameters, status, message, and result.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start = datetime.now(timezone.utc)
        resp = func(self, *args, **kwargs)
        end = datetime.now(timezone.utc)
        duration_ms = int((end - start).total_seconds() * 1000)

        record: Dict[str, Any] = {
            "timestamp": start.isoformat(),
            "operation": func.__name__,
            "parameters": kwargs or {},
            "status": resp.get("status"),
            "message": resp.get("message"),
            "duration_ms": duration_ms,
            "result": resp.get("result"),
        }
        self.logger.info(json.dumps(record, ensure_ascii=False))
        return resp
    return wrapper


class SecurityAudit:
    """
    Performs various security audit operations using platform-appropriate shell commands.

    Methods:
      - reconnaissance(): structured network connections + ARP neighbors.
      - detect_processes(): structured list of processes.
      - port_scan(): structured summary of open ports.
      - network_scan(): ping-sweep a CIDR to discover live hosts.
      - defense_actions(): structured summary of blocked IPs/ports and killed PIDs.
      - update_system(): structured summary of update actions.
    """

    def __init__(self) -> None:
        """
        Initialize the SecurityAudit instance, detect the platform,
        and attach a rotating handler for logs/security_audit.log.
        """
        self.logger = logger

        try:
            from logging.handlers import RotatingFileHandler
            log_dir = Path("logs")
            log_dir.mkdir(parents=True, exist_ok=True)
            exists = any(
                isinstance(h, RotatingFileHandler) and "security_audit.log" in getattr(h, "baseFilename", "")
                for h in self.logger.handlers
            )
            if not exists:
                handler = RotatingFileHandler(
                    log_dir / "security_audit.log",
                    maxBytes=5 * 1024 * 1024,
                    backupCount=3,
                    encoding="utf-8",
                )
                handler.setLevel(logging.INFO)
                handler.setFormatter(logging.Formatter("%(message)s"))
                self.logger.addHandler(handler)
        except Exception:
            logger.warning("Could not set up security_audit.log handler", exc_info=True)

        sys_name = platform.system().lower()
        self.is_windows = sys_name.startswith("win")
        self.is_linux = sys_name.startswith("linux")
        # treat WSL as linux for our purposes
        self.is_wsl = False
        if self.is_linux and Path("/proc/version").exists():
            ver = Path("/proc/version").read_text().lower()
            self.is_wsl = "microsoft" in ver or "wsl" in ver

        self.logger.debug(
            f"Initialized SecurityAudit (windows={self.is_windows}, wsl={self.is_wsl}, linux={self.is_linux})"
        )

    def _run_shell(self, cmd: List[str], use_cmd_exe: bool = False) -> subprocess.CompletedProcess:
        """
        Execute a shell command, optionally via Windows cmd.exe /c.
        """
        full_cmd = (["cmd.exe", "/c"] + cmd) if (use_cmd_exe and self.is_windows) else cmd
        return subprocess.run(full_cmd, check=True, capture_output=True, text=True)

    def _safe_run(self, cmd: List[str], use_cmd_exe: bool = False) -> str:
        """
        Like _run_shell but returns stdout or empty string on error.
        """
        try:
            return self._run_shell(cmd, use_cmd_exe).stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return ""

    def _parse_recon(self, raw: str) -> Dict[str, Any]:
        """
        Parse netstat/ss + arp raw output into structured JSON.
        """
        parts = raw.split("\n\n", 1)
        net_raw = parts[0]
        arp_raw = parts[1] if len(parts) > 1 else ""

        connections: List[Dict[str, str]] = []
        for line in net_raw.splitlines():
            m = re.match(r"^(tcp|udp)\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)", line)
            if m:
                proto, local, remote, state = m.groups()
                connections.append({
                    "proto": proto,
                    "local": local,
                    "remote": remote,
                    "state": state
                })

        neighbors: List[Dict[str, str]] = []
        for line in arp_raw.splitlines():
            m = re.match(r"^(\S+)\s+.*lladdr\s+([\da-f:]+)\s+(\S+)", line, re.I)
            if m:
                ip, mac, state = m.groups()
                neighbors.append({
                    "ip": ip,
                    "mac": mac,
                    "state": state.upper()
                })

        return {"connections": connections, "neighbors": neighbors}

    @_audit_log
    def reconnaissance(self) -> Dict[str, Any]:
        """
        Gather network connections and ARP/neighbor table.

        Returns:
            {
                "status": True,
                "message": "Recon complete",
                "result": { "connections": [...], "neighbors": [...] }
            }
        """
        if self.is_windows:
            net = self._safe_run(["netstat", "-ano"], use_cmd_exe=True)
            arp = self._safe_run(["arp", "-a"], use_cmd_exe=True)
        else:
            if shutil.which("netstat"):
                net = self._safe_run(["netstat", "-tunap"])
            elif shutil.which("ss"):
                net = self._safe_run(["ss", "-tunap"])
            else:
                net = ""
            arp = (
                self._safe_run(["ip", "neigh"]) if shutil.which("ip")
                else self._safe_run(["arp", "-n"])
            )

        combined = f"{net}\n\n{arp}"
        structured = self._parse_recon(combined)
        return {"status": True, "message": "Recon complete", "result": structured}

    @_audit_log
    def detect_processes(self) -> Dict[str, Any]:
        """
        Enumerate running processes via psutil.

        Returns:
            {
                "status": True,
                "message": "Process audit complete",
                "result": { "processes": [ {pid, user, name}, ... ] }
            }
        """
        try:
            procs = [
                {"pid": p.info["pid"], "user": p.info["username"], "name": p.info["name"]}
                for p in psutil.process_iter(["pid", "name", "username"])
            ]
            return {"status": True, "message": "Process audit complete", "result": {"processes": procs}}
        except Exception as e:
            self.logger.error("Process detection error", exc_info=True)
            return {"status": False, "message": str(e), "result": None}

    @_audit_log
    def port_scan(self, target: str, start_port: int = 1, end_port: int = 1024) -> Dict[str, Any]:
        """
        Scan a range of TCP ports on a given target.

        Returns:
            {
                "status": True,
                "message": "Port scan complete",
                "result": {
                    "target": target,
                    "range": [start_port, end_port],
                    "open_ports": [...],
                    "total_open": int
                }
            }
        """
        if not target:
            return {"status": False, "message": "Target cannot be empty", "result": None}
        if start_port < 1 or end_port < start_port:
            return {"status": False, "message": "Invalid port range", "result": None}

        open_ports: List[int] = []
        try:
            if self.is_windows:
                # Windows via PowerShell if available
                if shutil.which("powershell"):
                    cmd = (
                        f"1..{end_port} | ForEach-Object {{ "
                        f"if (Test-NetConnection -ComputerName {target} -Port $_ -Quiet) {{ Write-Output $_ }} }}"
                    )
                    out = self._safe_run(["powershell", "-Command", cmd], use_cmd_exe=True)
                    open_ports = [int(p) for p in out.split() if p.isdigit()]
                else:
                    # fallback to netstat parsing
                    net = self._safe_run(["netstat", "-an"], use_cmd_exe=True)
                    for line in net.splitlines():
                        parts = line.split()
                        # look for lines ending with LISTENING or LISTEN
                        if parts and ("LISTEN" in parts[-1].upper()):
                            # local address is at index 1
                            addr = parts[1]
                            port_str = addr.rsplit(":", 1)[-1]
                            if port_str.isdigit():
                                open_ports.append(int(port_str))
            else:
                for port in range(start_port, end_port + 1):
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(0.3)
                        if sock.connect_ex((target, port)) == 0:
                            open_ports.append(port)

            summary = {
                "target": target,
                "range": [start_port, end_port],
                "open_ports": open_ports,
                "total_open": len(open_ports),
            }
            return {"status": True, "message": "Port scan complete", "result": summary}
        except Exception as e:
            self.logger.error("Port scan error", exc_info=True)
            return {"status": False, "message": str(e), "result": None}

    @_audit_log
    def network_scan(self, network: str) -> Dict[str, Any]:
        """
        Ping-sweep every host in a given CIDR to discover live hosts.

        Returns:
            {
                "status": True,
                "message": "Network scan complete",
                "result": {
                    "network": network,
                    "alive_hosts": [...],
                    "total_alive": int
                }
            }
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
        except ValueError as e:
            return {"status": False, "message": f"Invalid network '{network}': {e}", "result": None}

        alive: List[str] = []
        for host in net.hosts():
            ip = str(host)
            cmd = ["ping", "-n", "1", "-w", "1000", ip] if self.is_windows else ["ping", "-c", "1", "-W", "1", ip]
            out = self._safe_run(cmd)
            if out and ("ttl=" in out.lower() or "bytes=" in out.lower()):
                alive.append(ip)

        result = {
            "network": network,
            "alive_hosts": alive,
            "total_alive": len(alive)
        }
        return {"status": True, "message": "Network scan complete", "result": result}

    @_audit_log
    def defense_actions(
        self,
        bad_ips: Optional[List[str]] = None,
        bad_pids: Optional[List[int]] = None,
        bad_ports: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Block IPs, kill PIDs, and block TCP ports.

        Returns:
            {
                "status": True,
                "message": "Defense complete",
                "result": {
                    "blocked_ips": [...],
                    "killed_pids": [...],
                    "blocked_ports": [...],
                    "errors": [...]
                }
            }
        """
        bad_ips = bad_ips or []
        bad_pids = bad_pids or []
        bad_ports = bad_ports or []
        summary = {"blocked_ips": [], "killed_pids": [], "blocked_ports": [], "errors": []}

        try:
            for ip in bad_ips:
                cmd = (
                    ["netsh", "advfirewall", "firewall", "add", "rule",
                     f"name=Block_{ip}", "dir=in", "action=block", f"remoteip={ip}"]
                    if self.is_windows
                    else ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"]
                )
                self._safe_run(cmd)
                summary["blocked_ips"].append(ip)

            for pid in bad_pids:
                cmd = (
                    ["taskkill", "/PID", str(pid), "/F"]
                    if self.is_windows
                    else ["kill", "-9", str(pid)]
                )
                self._safe_run(cmd)
                summary["killed_pids"].append(pid)

            for port in bad_ports:
                cmd = (
                    ["netsh", "advfirewall", "firewall", "add", "rule",
                     f"name=BlockPort_{port}", "dir=in", "action=block",
                     "protocol=TCP", f"localport={port}"]
                    if self.is_windows
                    else ["iptables", "-A", "INPUT", "-p", "tcp", "--dport", str(port), "-j", "DROP"]
                )
                self._safe_run(cmd)
                summary["blocked_ports"].append(port)

            return {"status": True, "message": "Defense complete", "result": summary}
        except Exception as e:
            self.logger.error("Defense actions error", exc_info=True)
            summary["errors"].append(str(e))
            return {"status": False, "message": str(e), "result": summary}

    @_audit_log
    def update_system(self) -> Dict[str, Any]:
        """
        Trigger operating system updates.

        Returns:
            {
                "status": True,
                "message": "Update complete",
                "result": { "ran_as": "...", "skipped": bool?, "commands": [...] }
            }
        """
        summary: Dict[str, Any] = {}
        try:
            if self.is_windows:
                self._safe_run(["wuauclt", "/detectnow"], use_cmd_exe=True)
                mp = Path(r"C:\Program Files\Windows Defender\MpCmdRun.exe")
                if mp.exists():
                    self._safe_run([str(mp), "-SignatureUpdate"], use_cmd_exe=True)
                summary[ "ran_as"] = "windows"
            else:
                if os.geteuid() != 0:
                    summary["ran_as"] = "non-root"
                    summary["skipped"] = True
                    return {"status": False, "message": "Not root; skipping update", "result": summary}
                summary["ran_as"] = "root"
                summary["commands"] = ["apt-get update", "apt-get upgrade -y"]

            return {"status": True, "message": "Update complete", "result": summary}
        except Exception as e:
            self.logger.error("System update error", exc_info=True)
            return {"status": False, "message": str(e), "result": {"error": str(e)}}


def security_audit_dispatcher(operation: str, **kwargs: Any) -> Dict[str, Any]:
    """
    Dispatch a SecurityAudit operation by name, enforcing its required and
    optional parameters, filling defaults, and returning structured results.
    """
    logger.info(f"[security_audit_dispatcher] operation={operation!r}, parameters={kwargs!r}")

    sa = SecurityAudit()

    ops_params = {
        "reconnaissance": [],
        "detect_processes": [],
        "port_scan": ["target", "start_port", "end_port"],
        "network_scan": ["network"],
        "defense_actions": ["bad_ips", "bad_pids", "bad_ports"],
        "update_system": []
    }
    defaults = {
        "start_port": 1,
        "end_port": 1024,
        "bad_ips": [],
        "bad_pids": [],
        "bad_ports": []
    }

    if operation not in ops_params:
        msg = f"Unsupported operation '{operation}'."
        logger.error(msg)
        return {"status": False, "message": msg, "result": None}

    allowed = ops_params[operation]

    if operation == "port_scan" and "target" not in kwargs:
        return {"status": False, "message": "port_scan requires 'target'", "result": None}
    if operation == "network_scan" and "network" not in kwargs:
        return {"status": False, "message": "network_scan requires 'network' (CIDR)", "result": None}

    unexpected = set(kwargs) - set(allowed)
    if unexpected:
        msg = f"Unexpected parameter(s) for '{operation}': {', '.join(sorted(unexpected))}"
        logger.error(msg)
        return {"status": False, "message": msg, "result": None}

    call_args: Dict[str, Any] = {}
    for param in allowed:
        if param in kwargs:
            call_args[param] = kwargs[param]
        elif param in defaults:
            call_args[param] = defaults[param]

    try:
        logger.info(f"[security_audit_dispatcher] invoking {operation} with {call_args}")
        resp = getattr(sa, operation)(**call_args)
        logger.info(f"[security_audit_dispatcher] {operation} completed: status={resp.get('status')}")
        return resp
    except Exception as e:
        logger.exception(f"[security_audit_dispatcher] Unexpected error in '{operation}'")
        return {"status": False, "message": str(e), "result": None}
