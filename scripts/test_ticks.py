import sys
from os import path

import math

sys.path.append(path.abspath("scripts"))
from utilities import *
from UniswapPool import *


# Instead of testing tickBitmap library, we test the UniswapPool ticks python dict and
# nextTick functionality, which should be equivalent.


# nextTick

# Pass tickSpacing as a workaround since originally TickBitmap is a library but now 
# it is part of the UniswapPool. 
def initializePoolWithMockTicks(tickSpacing):
    # To mimic tickBitmaps we need to create a dict of initialized ticks (ticks)
    pool = UniswapPool("A", "B", 1, tickSpacing )
    insertUninitializedTickstoMapping(pool.ticks, [-200, -55, -4, 70, 78, 84, 139, 240, 535])
    return pool


# lte == False

def test_lte_eq_false_notLte_notLte():
    print('returns tick to right if at initialized tick')
    pool = initializePoolWithMockTicks(1)
    (next, initialized) = pool.nextTick(78,False)

    assert next == 84
    assert initialized == True

def test_tickRight_ifAtInitializedTick_notLte():
    print('returns tick to right if at initialized tick')
    pool = initializePoolWithMockTicks(1)
    (next, initialized) = pool.nextTick(-55,False)

    assert next == -4
    assert initialized == True

def test_tickRight_nonInit_notLte():
    print('returns the tick directly to the right')
    pool = initializePoolWithMockTicks(1)
    (next, initialized) = pool.nextTick(77,False)

    assert next == 78
    assert initialized == True

def test_tickRight_init_notLte():
    print('returns the tick directly to the right')
    pool = initializePoolWithMockTicks(1)
    (next, initialized) = pool.nextTick(-56,False)

    assert next == -55
    assert initialized == True

## Now we are not limited to 256 visibility from the current tick
def test_nextInit_rightBoundary_notLte():
    print('returns the next words initialized tick if on the right boundary')
    pool = initializePoolWithMockTicks(1)
    (next, initialized) = pool.nextTick(255,False)

    assert next == 535
    assert initialized == True

def test_nextInit_leftBoundary_notLte():
    print('returns the next words initialized tick if on the left boundary')
    pool = initializePoolWithMockTicks(1)
    (next, initialized) = pool.nextTick(-257,False)

    assert next == -200
    assert initialized == True

def test_nextInit_notLte():
    print('returns the next initialized tick from the next word')
    pool = initializePoolWithMockTicks(1)
    insertUninitializedTickstoMapping(pool.ticks, [340])
    (next, initialized) = pool.nextTick(328,False)

    assert next == 340
    assert initialized == True

## Now we are not limited to 256 visibility from the current tick
def test_return_rightNoWordBoundaries_notLte():
    print('returns the next tick regardless of 256 word boundaries')
    pool = initializePoolWithMockTicks(1)
    (next, initialized) = pool.nextTick(508,False)
    assert next == 535
    assert initialized == True

    (next, initialized) = pool.nextTick(255,False)
    assert next == 535
    assert initialized == True


    (next, initialized) = pool.nextTick(383,False)
    assert next == 535
    assert initialized == True


# lte == True

def test_sameTick_ifInitialized():
    print('returns the same tick if initialized tick')
    pool = initializePoolWithMockTicks(1)
    (next, initialized) = pool.nextTick(78,True)

    assert next == 78
    assert initialized == True

