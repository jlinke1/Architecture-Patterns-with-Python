from models import Batch, OrderLine
import pytest


@pytest.fixture
def order_line():
    return OrderLine(order_reference="order-ref", sku="RED-CHAIR", quantity=2)


@pytest.fixture
def batch():
    return Batch(reference="unique-id", sku="RED-CHAIR", quantity=10, eta=None)


@pytest.fixture
def batch_with_allocated_order_line(order_line):
    return Batch(
        reference="unique-id",
        sku="RED-CHAIR",
        quantity=10,
        eta=None,
        processed_order_lines={order_line},
    )


@pytest.fixture
def batch_with_other_sku():
    return Batch(reference="unique-id", sku="BLUE-CHAIR", quantity=10, eta=None)


def test_allocate_order_line_to_batch_reduces_available_quantity_by_x_for_x(
    order_line, batch
):
    expected_batch = Batch(
        reference="unique-id",
        sku="RED-CHAIR",
        quantity=10,
        eta=None,
        processed_order_lines={order_line},
    )

    result = batch.allocate(order_line)

    assert result == expected_batch


def test_allocate_does_not_allocate_if_x_is_larger_than_available(
    order_line,
):
    batch = Batch(
        reference="unique-id",
        sku="RED-CHAIR",
        quantity=10,
        eta=None,
        processed_order_lines={
            OrderLine(order_reference="other-order-ref", sku="RED-CHAIR", quantity=9)
        },
    )

    result = batch.allocate(order_line)

    assert result.remaining_quantity == 1


def test_allocate_does_not_allocate_order_line_twice(order_line, batch):
    expected_batch = Batch(
        reference="unique-id",
        sku="RED-CHAIR",
        quantity=10,
        eta=None,
        processed_order_lines={order_line},
    )

    result = batch.allocate(order_line)
    final_result = result.allocate(order_line)

    assert final_result == expected_batch


def test_allocate_does_not_allocate_if_skus_dont_match(
    order_line, batch_with_other_sku
):
    result = batch_with_other_sku.allocate(order_line)

    assert result == batch_with_other_sku


def test_deallocate_deallocates_allocated_order_line(
    order_line, batch_with_allocated_order_line, batch
):
    expected_batch = batch

    result = batch_with_allocated_order_line.deallocate(order_line)

    assert result == expected_batch


def test_deallocate_does_not_deallocate_unallocated_order_line(order_line, batch):
    result = batch.deallocate(order_line)

    assert result == batch
