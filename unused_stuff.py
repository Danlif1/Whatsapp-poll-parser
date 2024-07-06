import subprocess


def turn_off_wifi():
    # This command works for macOS
    subprocess.run(["networksetup", "-setairportpower", "airport", "off"], check=True)


def turn_on_wifi():
    # This command works for macOS
    subprocess.run(["networksetup", "-setairportpower", "airport", "on"], check=True)


def force_quit_whatsapp():
    """Force quit WhatsApp application on macOS"""
    try:
        subprocess.run(["pkill", "WhatsApp"], check=True)
        print("WhatsApp has been force-quit.")
    except subprocess.CalledProcessError:
        print("Failed to force-quit WhatsApp or WhatsApp is not running.")


def open_whatsapp():
    """Open WhatsApp application on macOS"""
    try:
        subprocess.run(["open", "-a", "WhatsApp"], check=True)
        print("WhatsApp has been opened.")
    except subprocess.CalledProcessError:
        print("Failed to open WhatsApp or WhatsApp is not installed.")
