import pytest

from cooldown import Cooldown
from time import sleep, time


def test_init():
    c = Cooldown(1)
    assert c.duration == 1
    assert c.paused is False
    assert c.remaining >= 0

    c = Cooldown(1, cold=True)
    assert c.duration == 1
    assert c.remaining == 0
    assert c.cold
    assert not c.hot


def test_reset():
    c = Cooldown(1)
    sleep(2)
    assert c.remaining == 0
    assert c.cold
    assert not c.hot
    assert not c.paused
    c.reset(2)
    assert c.duration == 2
    assert c.remaining == c.duration
    assert not c.cold
    assert c.hot
    assert not c.paused


def test_remaining():
    c = Cooldown(1)
    assert round(c.remaining) == 1
    with pytest.raises(ValueError) as e:
        c.remaining = 2
    assert e.type is ValueError
    assert 'Cannot set remaining' in str(e.value)
    assert round(c.remaining) == 1
    assert not c.cold
    assert c.hot
    sleep(0.5)
    assert not c.cold
    assert c.hot
    assert c.remaining > 0
    sleep(1)
    assert c.cold
    assert not c.hot
    assert c.remaining == 0


def test_pause():
    c = Cooldown(5).pause()
    assert c.remaining == 5
    sleep(1)
    assert c.remaining == 5
    c.start()
    sleep(1)
    c.pause()
    assert round(c.remaining) == 4
    sleep(1)
    assert round(c.remaining) == 4
    c.start()
    sleep(1)
    assert round(c.remaining) == 3
    c.reset()
    c.pause()
    c.remaining = 4.1
    assert c.remaining == 4.1
    c.start()
    sleep(0.1)
    assert round(c.remaining) == 4



def test_cold():
    c = Cooldown(1)
    c.cold = True
    assert c.cold
    assert not c.hot
    assert c.duration == 1
    assert c.remaining == 0


def test_normalized():
    c = Cooldown(4)
    # Multiply by 100, since we can't round the 0..1 fractions
    assert round(c.normalized * 100) == 0
    sleep(1)
    assert round(c.normalized * 100) == 25
    sleep(1)
    assert round(c.normalized * 100) == 50
    sleep(1)
    assert round(c.normalized * 100) == 75
    sleep(1)
    assert round(c.normalized * 100) == 100
    assert c.cold


if __name__ == '__main__':
    test_init()
    test_reset()
    test_pause()
    test_cold()
    test_remaining()
    test_normalized()
