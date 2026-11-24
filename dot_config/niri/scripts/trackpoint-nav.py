#!/usr/bin/env python3
"""Convierte el TrackPoint del ThinkPad en navegación de ventanas de niri (Mod+Cursor).

No requiere paquetes externos (solo biblioteca estándar de Python 3).
Requiere que el usuario pertenezca al grupo `input` para leer /dev/input/eventX.
"""

import fcntl
import os
import re
import select
import struct
import subprocess
import sys
import time

# Ajusta estos valores si lo notas muy sensible o poco sensible:
THRESHOLD = 45      # Movimiento acumulado necesario para cambiar de ventana
COOLDOWN = 0.25     # Segundos mínimos entre saltos de ventana
IDLE_RESET = 0.15   # Segundos sin movimiento tras los que se reinicia el acumulador

EV_REL = 0x02
REL_X = 0x00
REL_Y = 0x01
INPUT_EVENT = struct.Struct("llHHi")


def find_trackpoint_device() -> str | None:
    try:
        with open("/proc/bus/input/devices", "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except OSError:
        return None

    for block in content.split("\n\n"):
        if "trackpoint" in block.lower():
            m = re.search(r"H: Handlers=.*\b(event\d+)\b", block)
            if m:
                return f"/dev/input/{m.group(1)}"
    return None


def trigger(action: str) -> None:
    try:
        subprocess.run(
            ["niri", "msg", "action", action],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1.0,
            check=False,
        )
    except Exception:
        pass


def main() -> int:
    lock_path = f"/tmp/niri-trackpoint-nav-{os.getuid()}.lock"
    lock_file = open(lock_path, "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return 0

    dev_path = None
    for _ in range(10):
        dev_path = find_trackpoint_device()
        if dev_path:
            break
        time.sleep(0.5)

    if not dev_path:
        print("trackpoint-nav: no se encontró el dispositivo TrackPoint.", file=sys.stderr)
        return 1

    try:
        fd = os.open(dev_path, os.O_RDONLY)
    except PermissionError:
        print(
            f"trackpoint-nav: sin permiso para leer {dev_path}. "
            f"Ejecuta: sudo usermod -aG input {os.environ.get('USER', '$USER')} "
            "y vuelve a iniciar sesión.",
            file=sys.stderr,
        )
        return 1

    dx = 0
    dy = 0
    last_trigger = 0.0
    event_size = INPUT_EVENT.size

    try:
        while True:
            ready, _, _ = select.select([fd], [], [], IDLE_RESET)
            if not ready:
                dx = 0
                dy = 0
                continue

            data = os.read(fd, event_size * 32)
            if not data:
                break

            now = time.monotonic()
            for offset in range(0, len(data) - (len(data) % event_size), event_size):
                _, _, ev_type, code, value = INPUT_EVENT.unpack_from(data, offset)
                if ev_type != EV_REL:
                    continue
                if now - last_trigger < COOLDOWN:
                    dx = 0
                    dy = 0
                    continue
                if code == REL_X:
                    dx += value
                elif code == REL_Y:
                    dy += value

            if now - last_trigger < COOLDOWN:
                continue

            if abs(dx) >= THRESHOLD or abs(dy) >= THRESHOLD:
                if abs(dx) >= abs(dy):
                    action = "focus-column-left" if dx < 0 else "focus-column-right"
                else:
                    action = "focus-window-up" if dy < 0 else "focus-window-down"
                trigger(action)
                dx = 0
                dy = 0
                last_trigger = now
    except KeyboardInterrupt:
        pass
    finally:
        os.close(fd)
        lock_file.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
