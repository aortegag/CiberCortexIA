"""
CIS Linux Benchmark Level 1 — hardcoded catalog (10 representative checks).

Each check is a plain dict so it can be serialised to JSON / stored in check_results
without a database lookup. Severity matches CVSS-like tiers used by scoring engine.
"""

from __future__ import annotations

from typing import TypedDict


class CISCheck(TypedDict):
    check_id: str          # e.g. "1.1.1"
    title: str
    severity: str          # critical | high | medium | low
    section: str           # human-readable section name
    recommendation: str    # remediation text shown to analyst
    effort_minutes: int    # estimated effort to remediate


CIS_L1_LINUX: list[CISCheck] = [
    {
        "check_id": "1.1.1",
        "title": "Ensure mounting of cramfs filesystems is disabled",
        "severity": "low",
        "section": "1. Initial Setup / Filesystem Configuration",
        "recommendation": (
            "Edit or create /etc/modprobe.d/cramfs.conf and add:\n"
            "  install cramfs /bin/false\n"
            "Run: rmmod cramfs"
        ),
        "effort_minutes": 5,
    },
    {
        "check_id": "1.3.1",
        "title": "Ensure sudo is installed",
        "severity": "high",
        "section": "1. Initial Setup / Configure sudo",
        "recommendation": (
            "Install sudo:\n"
            "  apt-get install sudo   # Debian/Ubuntu\n"
            "  yum install sudo       # RHEL/CentOS"
        ),
        "effort_minutes": 5,
    },
    {
        "check_id": "1.3.2",
        "title": "Ensure sudo commands use pty",
        "severity": "medium",
        "section": "1. Initial Setup / Configure sudo",
        "recommendation": (
            "Add the following line to /etc/sudoers or a file in /etc/sudoers.d/:\n"
            "  Defaults use_pty"
        ),
        "effort_minutes": 10,
    },
    {
        "check_id": "2.2.1",
        "title": "Ensure time synchronization is in use",
        "severity": "medium",
        "section": "2. Services / Time Synchronization",
        "recommendation": (
            "Install and enable chrony or ntp:\n"
            "  apt-get install chrony && systemctl enable chronyd\n"
            "Verify: timedatectl status"
        ),
        "effort_minutes": 15,
    },
    {
        "check_id": "3.1.1",
        "title": "Ensure IP forwarding is disabled",
        "severity": "high",
        "section": "3. Network Configuration / Network Parameters (Host Only)",
        "recommendation": (
            "Set in /etc/sysctl.d/60-netipv4_sysctl.conf:\n"
            "  net.ipv4.ip_forward = 0\n"
            "  net.ipv6.conf.all.forwarding = 0\n"
            "Apply: sysctl --system"
        ),
        "effort_minutes": 10,
    },
    {
        "check_id": "4.1.1",
        "title": "Ensure auditd is installed",
        "severity": "high",
        "section": "4. Logging and Auditing / Configure Logging",
        "recommendation": (
            "Install auditd:\n"
            "  apt-get install auditd audispd-plugins\n"
            "Enable: systemctl enable auditd && systemctl start auditd"
        ),
        "effort_minutes": 15,
    },
    {
        "check_id": "4.1.2",
        "title": "Ensure auditd service is enabled",
        "severity": "high",
        "section": "4. Logging and Auditing / Configure Logging",
        "recommendation": (
            "Enable and start auditd:\n"
            "  systemctl --now enable auditd"
        ),
        "effort_minutes": 5,
    },
    {
        "check_id": "5.2.1",
        "title": "Ensure permissions on /etc/ssh/sshd_config are configured",
        "severity": "medium",
        "section": "5. Access, Authentication and Authorization / SSH Server",
        "recommendation": (
            "Run:\n"
            "  chown root:root /etc/ssh/sshd_config\n"
            "  chmod og-rwx /etc/ssh/sshd_config"
        ),
        "effort_minutes": 5,
    },
    {
        "check_id": "5.2.7",
        "title": "Ensure SSH root login is disabled",
        "severity": "critical",
        "section": "5. Access, Authentication and Authorization / SSH Server",
        "recommendation": (
            "Edit /etc/ssh/sshd_config and set:\n"
            "  PermitRootLogin no\n"
            "Restart sshd: systemctl restart sshd"
        ),
        "effort_minutes": 5,
    },
    {
        "check_id": "6.1.1",
        "title": "Ensure permissions on /etc/passwd are configured",
        "severity": "critical",
        "section": "6. System Maintenance / File Permissions",
        "recommendation": (
            "Run:\n"
            "  chown root:root /etc/passwd\n"
            "  chmod u-x,go-wx /etc/passwd\n"
            "Expected permissions: 644"
        ),
        "effort_minutes": 5,
    },
]

# Quick lookup by check_id
CIS_BY_ID: dict[str, CISCheck] = {c["check_id"]: c for c in CIS_L1_LINUX}


def get_check(check_id: str) -> CISCheck | None:
    return CIS_BY_ID.get(check_id)
