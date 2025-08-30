import json
import threading
import time
from typing import Callable, Optional

import requests

try:
    import websocket  # websocket-client
except Exception as _exc:  # pragma: no cover
    websocket = None  # Will fail fast at runtime if missing


class Reward:
    def __init__(self, title: str):
        self.title = title


class RedemptionEvent:
    def __init__(self, reward_title: str, user_input: Optional[str]):
        self.reward = Reward(reward_title)
        self.input = user_input


class EventSubWebSocketClient:
    """
    Minimal EventSub WebSocket client for channel points redemptions.

    Flow:
    - Connect to wss://eventsub.wss.twitch.tv/ws
    - On session_welcome, POST a subscription with transport.method = websocket and session_id
    - Handle notifications; map payload to RedemptionEvent and invoke callback
    - Handle keepalives and reconnect messages
    """

    EVENTSUB_WS_URL = "wss://eventsub.wss.twitch.tv/ws"
    SUBSCRIPTIONS_URL = "https://api.twitch.tv/helix/eventsub/subscriptions"

    def __init__(
        self,
        *,
        token: str,
        client_id: str,
        broadcaster_id: str,
        on_redemption: Callable[[RedemptionEvent], None],
        log_message: Callable[[str], None],
    ) -> None:
        self.token = token
        self.client_id = client_id
        self.broadcaster_id = broadcaster_id
        self.on_redemption = on_redemption
        self.log_message = log_message

        self._ws_app: Optional[websocket.WebSocketApp] = None
        self._session_id: Optional[str] = None
        self._stop_flag = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if websocket is None:
            raise RuntimeError("websocket-client is not installed. Add 'websocket-client' to requirements.txt")
        if self._thread and self._thread.is_alive():
            return

        self._stop_flag.clear()
        self._thread = threading.Thread(target=self._run_forever, name="eventsub-ws", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_flag.set()
        try:
            if self._ws_app:
                self._ws_app.close()
        except Exception:
            pass

    # Internal
    def _run_forever(self) -> None:
        while not self._stop_flag.is_set():
            try:
                self._ws_app = websocket.WebSocketApp(
                    self.EVENTSUB_WS_URL,
                    on_message=self._on_message,
                    on_open=self._on_open,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                self._ws_app.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as exc:
                self.log_message(f"EventSub WS error: {exc}")
            # Backoff before reconnect
            if not self._stop_flag.is_set():
                time.sleep(3)

    def _on_open(self, _ws) -> None:
        self.log_message("EventSub WS connected")

    def _on_close(self, _ws, status_code, msg) -> None:  # noqa: ARG002
        self.log_message(f"EventSub WS closed ({status_code})")
        self._session_id = None

    def _on_error(self, _ws, error) -> None:
        self.log_message(f"EventSub WS error: {error}")

    def _on_message(self, _ws, message: str) -> None:
        try:
            data = json.loads(message)
        except Exception:
            self.log_message("EventSub WS received non-JSON message")
            return

        metadata = data.get("metadata", {})
        message_type = metadata.get("message_type")

        if message_type == "session_welcome":
            self._handle_session_welcome(data)
        elif message_type == "session_keepalive":
            # Nothing to do; server keepalive
            pass
        elif message_type == "session_reconnect":
            # Server instructs to reconnect to a new URL
            self._handle_session_reconnect(data)
        elif message_type == "notification":
            self._handle_notification(data)
        else:
            # Other message types: revocation, etc.
            pass

    def _handle_session_welcome(self, data: dict) -> None:
        try:
            self._session_id = data["payload"]["session"]["id"]
            self.log_message("EventSub session established")
            self._create_redemption_subscription()
        except Exception as exc:
            self.log_message(f"Failed to process session_welcome: {exc}")

    def _handle_session_reconnect(self, data: dict) -> None:
        try:
            reconnect_url = data["payload"]["session"]["reconnect_url"]
        except Exception:
            reconnect_url = None
        if reconnect_url and self._ws_app is not None:
            self.log_message("EventSub WS reconnecting to new URL")
            try:
                self._ws_app.close()
            except Exception:
                pass
            # Establish a new connection to the provided URL
            try:
                self._ws_app = websocket.WebSocketApp(
                    reconnect_url,
                    on_message=self._on_message,
                    on_open=self._on_open,
                    on_error=self._on_error,
                    on_close=self._on_close,
                )
                self._ws_app.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as exc:
                self.log_message(f"EventSub WS reconnect error: {exc}")

    def _create_redemption_subscription(self) -> None:
        if not self._session_id:
            return

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "type": "channel.channel_points_custom_reward_redemption.add",
            "version": "1",
            "condition": {
                "broadcaster_user_id": self.broadcaster_id,
            },
            "transport": {
                "method": "websocket",
                "session_id": self._session_id,
            },
        }
        try:
            resp = requests.post(self.SUBSCRIPTIONS_URL, headers=headers, json=payload, timeout=10)
            if resp.status_code in (202, 200):
                self.log_message("Subscribed to channel points (EventSub WS)")
            else:
                self.log_message(f"Failed to subscribe (EventSub WS): {resp.status_code} - {resp.text}")
        except Exception as exc:
            self.log_message(f"Subscription request failed: {exc}")

    def _handle_notification(self, data: dict) -> None:
        try:
            event = data["payload"]["event"]
            reward_title = event["reward"]["title"]
            user_input = event.get("user_input")
            self.on_redemption(RedemptionEvent(reward_title, user_input))
        except Exception as exc:
            self.log_message(f"Failed to process notification: {exc}")


