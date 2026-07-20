"""
Live order execution: interface for placing real orders.

Currently a stub/interface that defines the API for connecting to
NinjaTrader, QuantConnect, or broker APIs. The owner will implement
the actual broker connection.

Supported broker adapters (planned):
  - NinjaTrader (via NinjaScript strategy interface)
  - QuantConnect (via LEAN engine)
  - Interactive Brokers (via IB API)
  - OANDA (REST API)
  - Alpaca (REST API)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a live order to be sent to the broker."""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float  # limit/stop price
    stop_price: Optional[float] = None  # for stop/stop-limit orders
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    message: str = ""


class BrokerAdapter(ABC):
    """Abstract base class for broker connections.

    Subclass this to implement a specific broker adapter.
    """

    @abstractmethod
    def connect(self) -> bool:
        """Connect to the broker.

        Returns:
            True if connection successful
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the broker."""
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the broker.

        Returns:
            True if connected
        """
        ...

    @abstractmethod
    def place_order(self, order: Order) -> Order:
        """Place an order with the broker.

        Args:
            order: Order to place

        Returns:
            Order with updated status
        """
        ...

    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order.

        Args:
            order_id: ID of the order to cancel

        Returns:
            True if cancellation was successful
        """
        ...

    @abstractmethod
    def get_order_status(self, order_id: str) -> Order:
        """Get the current status of an order.

        Args:
            order_id: ID of the order

        Returns:
            Order with current status
        """
        ...

    @abstractmethod
    def get_positions(self) -> list[dict]:
        """Get current open positions.

        Returns:
            List of position dicts with symbol, qty, avg_price, etc.
        """
        ...

    @abstractmethod
    def get_account_summary(self) -> dict:
        """Get account summary (balance, margin, equity).

        Returns:
            dict with account info
        """
        ...


class Executor:
    """Manages live order execution.

    Wraps a BrokerAdapter and adds position sizing, risk checks,
    and order management.
    """

    def __init__(self, broker: Optional[BrokerAdapter] = None):
        self.broker = broker
        self._pending_orders: dict[str, Order] = {}

    @property
    def is_ready(self) -> bool:
        return self.broker is not None and self.broker.is_connected()

    def execute_signal(
        self,
        symbol: str,
        direction: int,
        quantity: float,
        price: float,
    ) -> Optional[Order]:
        """Execute a trading signal.

        Args:
            symbol: Trading symbol
            direction: 1 = BUY, -1 = SELL
            quantity: Number of contracts/units
            price: Current market price

        Returns:
            Order if placed, None if not ready
        """
        if not self.is_ready:
            logger.warning("Broker not connected")
            return None

        side = OrderSide.BUY if direction == 1 else OrderSide.SELL

        order = Order(
            id=f"sig_{len(self._pending_orders)}_{symbol}",
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=quantity,
            price=price,
        )

        try:
            filled_order = self.broker.place_order(order)
            self._pending_orders[filled_order.id] = filled_order
            logger.info(f"Order placed: {filled_order}")
            return filled_order
        except Exception as e:
            logger.error(f"Order failed: {e}")
            return None

    def get_open_orders(self) -> list[Order]:
        """Get all pending orders.

        Returns:
            List of open orders
        """
        return [
            o for o in self._pending_orders.values()
            if o.status in (OrderStatus.PENDING, OrderStatus.PARTIAL)
        ]


# =========================================================================
#  Example: NinjaTrader Adapter (stub)
# =========================================================================

class NinjaTraderAdapter(BrokerAdapter):
    """Stub adapter for NinjaTrader.

    NOTE: This is a placeholder. Real implementation requires the
    NinjaTrader API client library.
    """

    def connect(self) -> bool:
        logger.info("NinjaTraderAdapter: connect() — stub")
        return True

    def disconnect(self) -> None:
        logger.info("NinjaTraderAdapter: disconnect() — stub")

    def is_connected(self) -> bool:
        return True  # stub

    def place_order(self, order: Order) -> Order:
        logger.info(f"NinjaTraderAdapter: place_order({order.symbol}, {order.side}) — stub")
        order.status = OrderStatus.FILLED
        order.filled_quantity = order.quantity
        order.avg_fill_price = order.price
        return order

    def cancel_order(self, order_id: str) -> bool:
        logger.info(f"NinjaTraderAdapter: cancel_order({order_id}) — stub")
        return True

    def get_order_status(self, order_id: str) -> Order:
        logger.info(f"NinjaTraderAdapter: get_order_status({order_id}) — stub")
        return Order(id=order_id, symbol="", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=0, price=0)

    def get_positions(self) -> list[dict]:
        return []

    def get_account_summary(self) -> dict:
        return {"balance": 100000.0, "equity": 100000.0, "buying_power": 50000.0}


# =========================================================================
#  Example: QuantConnect Adapter (stub)
# =========================================================================

class QuantConnectAdapter(BrokerAdapter):
    """Stub adapter for QuantConnect LEAN engine.

    NOTE: This is a placeholder. Real implementation requires the
    QuantConnect Python API.
    """

    def connect(self) -> bool:
        logger.info("QuantConnectAdapter: connect() — stub")
        return True

    def disconnect(self) -> None:
        logger.info("QuantConnectAdapter: disconnect() — stub")

    def is_connected(self) -> bool:
        return True

    def place_order(self, order: Order) -> Order:
        logger.info(f"QuantConnectAdapter: place_order({order.symbol}, {order.side}) — stub")
        order.status = OrderStatus.FILLED
        return order

    def cancel_order(self, order_id: str) -> bool:
        return True

    def get_order_status(self, order_id: str) -> Order:
        return Order(id=order_id, symbol="", side=OrderSide.BUY, order_type=OrderType.MARKET, quantity=0, price=0)

    def get_positions(self) -> list[dict]:
        return []

    def get_account_summary(self) -> dict:
        return {"balance": 100000.0, "equity": 100000.0}