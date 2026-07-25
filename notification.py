try:
    from plyer import notification
    HAS_NOTIFICATION = True
except Exception:
    HAS_NOTIFICATION = False


class NotificationManager:

    def __init__(self):
        self.active = False

    def show(self, title="811 Assistant", message="Running..."):
        if not HAS_NOTIFICATION:
            return

        try:
            notification.notify(
                title=title,
                message=message,
                app_name="811 Assistant",
                ticker="811 Assistant",
                toast=False
            )
            self.active = True
        except Exception as e:
            print("Notification Error:", e)

    def close(self):
        self.active = False
