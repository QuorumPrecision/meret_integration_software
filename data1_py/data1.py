#!/usr/bin/env python3


def checksum(summ):
    nbits = 8
    val = 256 - summ
    checksum = (val + (1 << nbits)) % (1 << nbits)
    return checksum
