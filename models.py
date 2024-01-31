import dataclasses
from typing import Callable
import copy
import pendulum


@dataclasses.dataclass(frozen=True)
class OrderLine:
    order_reference: str
    sku: str
    quantity: int


@dataclasses.dataclass(frozen=True)
class Batch:
    reference: str
    sku: str
    quantity: int
    eta: pendulum.DateTime | None
    processed_order_lines: set[OrderLine] = dataclasses.field(default_factory=set)

    @property
    def remaining_quantity(self) -> int:
        return self.quantity - sum(line.quantity for line in self.processed_order_lines)

    def allocate(self, order_line: OrderLine) -> "Batch":
        if not self.can_allocate(order_line):
            print(f"Cannot allocate {order_line} in {self}")
            return self

        return update_processed_lines_with_copy(
            batch=self,
            order_line=order_line,
            operation=add_to_set,
        )

    def deallocate(self, order_line: OrderLine) -> "Batch":
        if order_line not in self.processed_order_lines:
            return self

        return update_processed_lines_with_copy(
            batch=self,
            order_line=order_line,
            operation=remove_from_set,
        )

    def can_allocate(self, order_line: OrderLine) -> bool:
        return (
            order_line.sku == self.sku
            and order_line.quantity <= self.remaining_quantity
            and order_line not in self.processed_order_lines
        )


def remove_from_set(
    order_lines: set[OrderLine], order_line: OrderLine
) -> set[OrderLine]:
    order_lines.remove(order_line)
    return order_lines


def add_to_set(order_lines: set[OrderLine], order_line: OrderLine) -> set[OrderLine]:
    order_lines.add(order_line)
    return order_lines


def update_processed_lines_with_copy(
    batch: Batch,
    order_line: OrderLine,
    operation: Callable[[set[OrderLine], OrderLine], set[OrderLine]],
) -> Batch:
    processed_lines = copy.copy(batch.processed_order_lines)
    processed_lines = operation(processed_lines, order_line)
    return Batch(
        reference=batch.reference,
        sku=batch.sku,
        quantity=batch.quantity,
        eta=batch.eta,
        processed_order_lines=processed_lines,
    )
