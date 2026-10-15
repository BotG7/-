#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
from pathlib import Path


def r(c, chk=False, sdo=False, cap=True, sln=False):
    if sdo and os.geteuid() != 0:
        c = ["sudo"] + c
    try:
        res = subprocess.run(c, check=chk, capture_output=cap, text=True)
        if not sln and res.stdout:
            print(res.stdout.strip().lower())
        return res
    except FileNotFoundError:
        if not sln:
            print(f"[!] команда не найдена: {c[0]}".lower())
        return None
    except subprocess.CalledProcessError as e:
        if not sln:
            print(f"[!] ошибка выполнения {c}: {e}".lower())
        return None


def ce(n):
    return shutil.which(n) is not None


def ps(t):
    print(f"\n{'=' * 60}")
    print(f"  {t}".lower())
    print('=' * 60)


def la(m):
    print(f"  [+] {m}".lower())


def se(cl, sln=True):
    return r(cl, sdo=True, sln=sln)


def rf(p):
    if os.path.isdir(p):
        try:
            shutil.rmtree(p)
        except Exception:
            pass
    elif os.path.isfile(p):
        try:
            os.remove(p)
        except Exception:
            pass


def rc(p):
    if not os.path.isdir(p):
        return
    for i in os.listdir(p):
        f = os.path.join(p, i)
        try:
            if os.path.isdir(f) and not os.path.islink(f):
                shutil.rmtree(f, ignore_errors=True)
            else:
                os.remove(f)
        except Exception:
            pass


def sd(u):
    ps("настройка рабочего стола")
    dp = Path(f"/home/{u}/Рабочий стол")
    if dp.exists():
        r(["chmod", "a-w", str(dp)])
        la(f"заблокирован рабочий стол: {dp}")
    flds = ["ис125", "ис225", "ис24", "оиб24", "исп23", "исв23", "другие"]
    for f in flds:
        fp = dp / f
        if not fp.is_dir():
            print(f"создаем директорию: {fp}".lower())
            fp.mkdir(parents=True, exist_ok=True)
        else:
            print(f"директория существует: {fp}".lower())
    if dp.exists():
        r(["chmod", "a-w", str(dp)])
        print("заблокирован рабочий стол.".lower())


def cc():
    ps("очистка данных chromium")
    h = Path.home()
    cl = h / ".config" / "chromium" / "Default"
    r(["pkill", "chromium"], sln=True)
    la("chromium процессы завершены")
    if not cl.is_dir():
        print(f"[!] директория chromium не найдена: {cl}".lower())
        return
    fr = [
        "Login Data", "Login Data-journal", "Preferences", "Cookies", "Cookies-journal",
        "Web Data", "Web Data-journal", "Top Sites", "Top Sites-journal",
        "Favicons", "Favicons-journal", "TransportSecurity", "Shortcuts", "Shortcuts-journal",
        "MediaDeviceSalts", "MediaDeviceSalts-journal", "heavy_ad_intervention_opt_out.db",
    ]
    dr = [
        "Cache", "Cache Storage", "IndexedDB", "Local Storage",
        "Service Worker", "Sessions", "Sync Data", "DIPS", "History Provider Cache",
    ]
    for n in fr:
        t = cl / n
        if t.exists():
            rf(str(t))
            la(f"удален файл: {n}")
    for n in dr:
        t = cl / n
        if t.exists():
            rf(str(t))
            la(f"удалена папка: {n}")
    print("пароли удалены. данные пользователей google сохранены.".lower())


def cu(u):
    ps("очистка пользовательских папок")
    h = Path(f"/home/{u}")
    flds = ["Видео", "Загрузки", "Документы", "Изображения", "Общедоступные", "Шаблоны"]
    for f in flds:
        fp = h / f
        if fp.is_dir():
            rc(str(fp))
            la(f"очищено: {fp}")
    rc(str(Path.home() / ".local" / "share" / "Trash" / "files"))
    rc(str(Path.home() / ".local" / "share" / "Trash" / "info"))
    la("корзина очищена")


def cp():
    ps("очистка кэша пакетов")
    if ce("apt"):
        la("очистка кэша apt")
        se(["apt", "clean"])
        se(["apt", "autoclean"])
        se(["apt", "autoremove", "-y"])
    if ce("dnf"):
        la("очистка кэша dnf...")
        se(["dnf", "clean", "all"])
        se(["dnf", "autoremove", "-y"])
    if ce("pacman"):
        la("очистка кэша pacman")
        se(["pacman", "-Scc", "--noconfirm"])


def ct():
    ps("очистка временных файлов")
    la("очистка временных файлов пользователя...")
    rc(str(Path.home() / ".cache"))
    rc("/tmp")
    rc(str(Path.home() / ".local" / "share" / "Trash"))
    rc(str(Path.home() / ".thumbnails"))
    la("очистка логов приложений...")
    se(["journalctl", "--vacuum-time=7d"])


def main():
    u = os.getlogin() if hasattr(os, "getlogin") else os.environ.get("USER", "")
    print(f"текущий пользователь: {u}".lower())
    sd(u)
    cc()
    cu(u)
    cp()
    ct()
    ps("отладка")
    ok = Path("/home/скрипты/okclean.txt")
    try:
        ok.parent.mkdir(parents=True, exist_ok=True)
        ok.touch()
        la(f"создан файл: {ok}")
    except Exception as e:
        print(f"[!] не удалось создать {ok}: {e}".lower())
    if ce("dnf"):
        se(["dnf", "makecache"])
        se(["dnf", "upgrade", "-y"])
    se(["shutdown", "-a"])
    print("\n[!] готово.".lower())


if __name__ == "__main__":
    main()
