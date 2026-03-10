from pymavlink import mavutil
import time
import threading
import sys
import select

# =====================================================
# CONNECTION SECTION
# =====================================================

m = mavutil.mavlink_connection('/dev/ttyAMA0', baud=57600)

m.wait_heartbeat()
print("Connected")

land_now = False

# =====================================================
# KEYBOARD FAILSAFE THREAD
# =====================================================

def keyboard_listener():
    global land_now
    while True:
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.readline().strip()
            if key == "l":
                print("EMERGENCY LAND TRIGGERED")
                land_now = True
                break

threading.Thread(target=keyboard_listener, daemon=True).start()

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def set_mode(mode):
    print(f"Setting mode: {mode}")
    m.set_mode_apm(mode)
    time.sleep(2)

def arm():
    print("Sending ARM command")
    m.arducopter_arm()

    for i in range(10):
        hb = m.recv_match(
            type='HEARTBEAT',
            blocking=True,
            timeout=1
        )

        if hb and (hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
            print("Armed SUCCESS")
            return True

    print("ARM FAILED (check QGC messages)")
    return False

def rc_override(pitch=1500, roll=1500, throttle=1500, yaw=1500, t=1):
    global land_now

    end = time.time() + t

    while time.time() < end:

        if land_now:
            print("Switching to LAND")
            set_mode("LAND")
            return

        m.mav.rc_channels_override_send(
            m.target_system,
            m.target_component,
            roll,
            pitch,
            throttle,
            yaw,
            0,0,0,0
        )

        time.sleep(0.1)

# =====================================================
# FLIGHT SEQUENCE
# =====================================================

set_mode("ALT_HOLD")

if not arm():
    print("Stopping script because arm failed")
    exit()

print("Type 'l' + ENTER anytime for emergency LAND")

print("Takeoff")
rc_override(throttle=1600, t=3)

print("Hover")
rc_override(throttle=1500, t=2)

print("Forward")
rc_override(pitch=1600, throttle=1500, t=2)

print("Hover")
rc_override(throttle=1500, t=2)

print("Landing")
set_mode("LAND")

print("Mission complete")