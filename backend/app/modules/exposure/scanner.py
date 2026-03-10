"""
Nmap TCP scan wrapper.

Design:
- parse_nmap_xml() is a pure function — easy to unit-test with fixture XML.
- run_nmap() is async and runs nmap as a subprocess.
- Called from Celery tasks via asyncio.run() or directly in async contexts.

Safety: caller MUST verify asset.status == 'authorized' before calling run_nmap().
"""
import asyncio
import xml.etree.ElementTree as ET


def parse_nmap_xml(xml_output: str) -> list[dict]:
    """
    Parse nmap -oX output into a list of service dicts.

    Returns:
        list of dicts with keys: port, protocol, service, version, banner, cpe
    """
    services: list[dict] = []
    try:
        root = ET.fromstring(xml_output)
    except ET.ParseError:
        return services

    for host in root.findall("host"):
        ports_elem = host.find("ports")
        if not ports_elem:
            continue

        for port_elem in ports_elem.findall("port"):
            state = port_elem.find("state")
            if state is None or state.get("state") != "open":
                continue

            port_num = int(port_elem.get("portid", 0))
            protocol = port_elem.get("protocol", "tcp")

            service_elem = port_elem.find("service")
            service_name = "unknown"
            version_str = None
            cpe_str = None

            if service_elem is not None:
                service_name = service_elem.get("name", "unknown")

                # Build version string from product + version + extrainfo
                parts = [
                    service_elem.get("product", ""),
                    service_elem.get("version", ""),
                    service_elem.get("extrainfo", ""),
                ]
                version_str = " ".join(p for p in parts if p) or None
                if version_str:
                    version_str = version_str[:255]

                # Take first CPE if present
                for cpe_elem in service_elem.findall("cpe"):
                    cpe_str = (cpe_elem.text or "")[:255]
                    break

            # Banner from script output
            banner = None
            for script in port_elem.findall("script"):
                if script.get("id") == "banner":
                    banner = (script.get("output", "") or "")[:500]
                    break

            services.append(
                {
                    "port": port_num,
                    "protocol": protocol,
                    "service": service_name,
                    "version": version_str,
                    "banner": banner,
                    "cpe": cpe_str,
                }
            )

    return services


async def run_nmap(target: str, timeout: int = 300) -> list[dict]:
    """
    Execute nmap TCP scan against target (IP or hostname).

    Args:
        target: IP address or hostname. Must be pre-validated as authorized.
        timeout: Max seconds to wait for nmap to complete.

    Returns:
        List of service dicts from parse_nmap_xml().

    Raises:
        RuntimeError: if nmap is not installed, times out, or returns error.
    """
    cmd = [
        "nmap",
        "-sT",          # TCP connect scan (no root needed)
        "-sV",          # Version detection
        "-T4",          # Aggressive timing
        "--open",       # Only open ports
        "--script", "banner",  # Banner grabbing
        "-oX", "-",     # XML to stdout
        target,
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        raise RuntimeError(f"Nmap scan timed out after {timeout}s for target {target}")
    except FileNotFoundError:
        raise RuntimeError(
            "nmap not found. Install nmap: apt-get install -y nmap (or equivalent)"
        )

    # nmap returns 0 on success, 1 when no hosts responded — both are acceptable
    if proc.returncode not in (0, 1):
        err = stderr.decode(errors="replace")[:500]
        raise RuntimeError(f"nmap exited with code {proc.returncode}: {err}")

    return parse_nmap_xml(stdout.decode(errors="replace"))
