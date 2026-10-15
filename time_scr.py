#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Настройка автоочистки рабочей станции."""

import os
import sys
import shutil
import getpass
import subprocess
from pathlib import Path

# --- параметры подключения к хранилищу скриптов ---
SRV_LOGIN = "students"
SRV_ADDR  = "10.179.100.153"
SRV_PASS  = "12345"
SRV_FILE  = "/home/students/scripts303/cleanALL.sh"

# --- локальные пути ---
BASE_DIR   = Path(__file__).resolve().parent
LOCAL_SH   = BASE_DIR / "cleanALL.sh"
SUDO_DIR   = Path("/etc/sudoers.d")

TASK_LINE  = "00 16 * * * {}"


def whoami():
    """Имя текущего пользователя."""
    try:
        return getpass.getuser()
    except Exception:
        return os.environ.get("USER", "unknown")


def sh(args, as_root=False, strict=True):
    """Обёртка над subprocess.run."""
    if as_root and os.geteuid() != 0:
        args = ["sudo"] + args
    try:
        subprocess.run(args, check=strict, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as err:
        print(f"  !! {err}")
        return False


def out(args, as_root=False):
    """Получить stdout команды."""
    if as_root and os.geteuid() != 0:
        args = ["sudo"] + args
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def step(num, title):
    print(f"\n[{num}] {title}")


def main():
    user = whoami()
    print(f"Пользователь: {user}")

    # ---------- шаг 1: разрешения sudo ----------
    step(1, "Настройка sudo")
    rule_file = SUDO_DIR / user

    if not rule_file.exists():
        sh(["touch", str(rule_file)], as_root=True)

    existing = out(["cat", str(rule_file)], as_root=True)
    wanted = f"{user} ALL=(ALL) NOPASSWD:ALL"

    if wanted not in existing:
        sh(
            ["bash", "-c", f"printf '%s\\n' '{wanted}' >> {rule_file}"],
            as_root=True,
        )
        print(f"  + добавлено правило для {user}")

    sh(["chmod", "0440", str(rule_file)], as_root=True)

    # ---------- шаг 2: получение скрипта ----------
    step(2, "Получение cleanALL.sh")

    if not os.access(BASE_DIR, os.W_OK):
        print(f"  нет записи в {BASE_DIR}")
        return 1

    if shutil.which("sshpass") is None:
        print("  sshpass отсутствует — установите пакет")
        return 1

    if LOCAL_SH.exists():
        print(f"  файл уже на месте: {LOCAL_SH}")
    else:
        fetch = [
            "sshpass", "-p", SRV_PASS,
            "scp",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            f"{SRV_LOGIN}@{SRV_ADDR}:{SRV_FILE}",
            str(LOCAL_SH),
        ]
        print(f"  забираю {SRV_LOGIN}@{SRV_ADDR}:{SRV_FILE}")
        if not sh(fetch):
            print("  не удалось скачать")
            return 1

    try:
        LOCAL_SH.chmod(0o755)
    except OSError as err:
        print(f"  chmod не сработал: {err}")

    # ---------- шаг 3: регистрация в cron ----------
    step(3, "Регистрация задания")

    schedule = TASK_LINE.format(LOCAL_SH)
    table = out(["crontab", "-l"])

    if str(LOCAL_SH) in table:
        print("  задание уже зарегистрировано")
    else:
        if table.strip():
            merged = table.rstrip("\n") + "\n" + schedule + "\n"
        else:
            merged = schedule + "\n"

        proc = subprocess.Popen(
            ["crontab", "-"],
            stdin=subprocess.PIPE,
            text=True,
        )
        proc.communicate(merged)

        if proc.returncode != 0:
            print("  crontab отказался принять запись")
            return 1
        print(f"  + добавлено: {schedule}")

    print("\nВсе шаги выполнены.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
