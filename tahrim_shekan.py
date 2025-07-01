import os
import platform
import requests
import time
import subprocess

# 📍 پیدا کردن رابط فعال شبکه در ویندوز
def get_active_interface_name():
    try:
        result = subprocess.check_output('netsh interface show interface', shell=True, text=True)
        lines = result.splitlines()
        for line in lines:
            if "Connected" in line:
                parts = line.split()
                if len(parts) >= 4:
                    return parts[-1]
    except Exception as e:
        print(f"❗ Error detecting active network interface: {e}")
    return None

# ⚙️ تنظیم DNS در ویندوز
def set_dns_windows(dns_ip):
    interface_name = get_active_interface_name()
    if interface_name:
        print(f"🎯 Active network interface detected: {interface_name}")
        os.system(f'netsh interface ip set dns name="{interface_name}" static {dns_ip} primary')
    else:
        print("⛔️ Unable to find active network interface.")

# ⚙️ تنظیم DNS در لینوکس (نیاز به sudo)
def set_dns_linux(dns_ip):
    try:
        with open("/etc/resolv.conf", 'w') as f:
            f.write(f"nameserver {dns_ip}\n")
        print(f"🔧 DNS updated to: {dns_ip}")
    except Exception as e:
        print(f"❗ Error setting DNS: {e}")

# 🌐 بررسی دسترسی به سایت
def check_site(site_url):
    try:
        response = requests.get(site_url, timeout=5)
        return response.status_code != 403
    except Exception:
        return False

# 📦 تشخیص سیستم‌عامل
def get_system():
    sys_name = platform.system().lower()
    if "windows" in sys_name:
        return "windows"
    elif "linux" in sys_name:
        return "linux"
    else:
        return None

# 🚀 اجرای اصلی برنامه
def main():
    site = input("🔍 Enter the website address to check for 403 error: ").strip()
    if not site.startswith("http"):
        site = "http://" + site

    system = get_system()
    if system not in ["windows", "linux"]:
        print("⛔️ Unsupported operating system.")
        return

    if not os.path.exists("dns_list.txt"):
        print("📄 File dns_list.txt not found.")
        return

    with open("dns_list.txt") as f:
        dns_list = [line.strip() for line in f if line.strip()]

    for dns_ip in dns_list:
        print(f"\n🛠 Changing DNS to: {dns_ip}")
        if system == "windows":
            set_dns_windows(dns_ip)
        else:
            set_dns_linux(dns_ip)

        time.sleep(2)

        print(f"🌐 Checking access to: {site}")
        if check_site(site):
            print(f"✅ Access granted using DNS: {dns_ip}")
            return
        else:
            print("🚫 403 Forbidden still received. Trying next DNS...")

    print("\n❌ Unfortunately, none of the DNS servers resolved the 403 error.")

if __name__ == "__main__":
    main()
