#!/usr/bin/env python
# coding: utf-8
"""
Transport Neutral Encapsulation Format (TNEF) files (winmail.dat) data extractor

References:
https://msdn.microsoft.com/en-us/library/ee203101(v=exchg.80).aspx
https://msdn.microsoft.com/en-us/library/ee157583(v=exchg.80).aspx
"""

from __future__ import print_function

from urllib.parse import quote

import argparse
import os
import struct
from io import BytesIO as StringIO
import compressed_rtf


TNEF_SIGNATURE = 0x223e9f78


def unpack_uint8(data):
    return struct.unpack('<B', data)[0]


def unpack_uint16(data):
    return struct.unpack('<H', data)[0]


def unpack_uint32(data):
    return struct.unpack('<I', data)[0]


def read_attribute(stream):
    """Read attribute"""
    level = unpack_uint8(stream.read(1))
    id_value = unpack_uint32(stream.read(4))
    length = unpack_uint32(stream.read(4))
    data = stream.read(length)
    checksum = unpack_uint16(stream.read(2))
    return level, id_value, length, data, checksum


def read_tnef_version(stream):
    """Read TNEF version"""
    level, id_value, length, data, checksum = read_attribute(stream)
    assert level == 1  # Message-level attribute
    assert id_value == 0x00089006  # TNEF version attribute id
    version = unpack_uint32(data)
    return level, id_value, length, version, checksum


def read_oem_codepage(stream):
    """Read OEM codepage"""
    level, id_value, length, data, checksum = read_attribute(stream)
    assert level == 1  # Message-level attribute
    assert id_value == 0x00069007  # OEM codepage attribute id
    assert length == 8
    primary = unpack_uint32(data[:4])
    secondary = unpack_uint32(data[4:])
    return level, id_value, length, primary, secondary, checksum


def parse_msg_props(stream):
    """Parse message properties"""
    msg_property_count = unpack_uint32(stream.read(4))
    compressed_rtf_data = []
    while True:
        try:
            msg_prop_type = unpack_uint16(stream.read(2))
            msg_prop_id = unpack_uint16(stream.read(2))
            # read binary data type
            if msg_prop_type == 0x0102:  # TypeBinary
                count = unpack_uint32(stream.read(4))
                length = unpack_uint32(stream.read(4))
                value = stream.read(length + (4 - length % 4) % 4)
            # parse types
            if msg_prop_id == 0x1009:  # compressed RTF (also known as "LZFu")
                compressed_rtf_data.append(value)
        except struct.error:
            break
    return compressed_rtf_data

def save_data(title, data, meta_data, out_dir):
    """Save 1 found data to `out_dir`"""
    # make out dir if not exists
    # if not os.path.exists(out_dir):
    #     os.makedirs(out_dir)

    out_dir = os.path.dirname(out_dir)

    # save attachments and meta files
    # filename = title.decode('windows-1252').encode('ascii', 'ignore').decode('ascii').replace("?", "")
    print('Saving attachment to: {}'.format(title))
    with open(os.path.join(out_dir, title), 'wb') as out_file:
        out_file.write(data)

    print('file saved')
    # meta_filename = '{}_meta.raw'.format(title)
    # print('Saving attachment meta file to: {}'.format(meta_filename))
    # with open(os.path.join(out_dir, meta_filename), 'wb') as out_file:
    #     out_file.write(meta_data)

def save_datas(in_filename, titles, data, meta_data, compressed_rtfs, out_dir):
    """Save found data to `out_dir`"""
    # make out dir if not exists
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # decode compressed RTF
    for index, compressed_rtf_data in enumerate(compressed_rtfs):
        if not compressed_rtf_data:
            continue
        filename = '{}_data_{}.rtf'.format(in_filename, index)
        print('Saving decompressed RTF data to: {}'.format(filename))
        out_data = compressed_rtf.decompress(compressed_rtf_data)
        with open(os.path.join(out_dir, filename), 'wb') as out_file:
            out_file.write(out_data)

    # save attachments and meta files
    for index, title in enumerate(titles):
        filename = str(index) + " - " + title.decode('windows-1252').encode('ascii', 'ignore').decode('ascii').replace("?", "")
        print('Saving attachment to: {}'.format(filename))
        with open(os.path.join(out_dir, filename), 'wb') as out_file:
            out_file.write(data[index])

        meta_filename = '{}_meta_{}.raw'.format(filename, index)
        print('Saving attachment meta file to: {}'.format(meta_filename))
        with open(os.path.join(out_dir, meta_filename), 'wb') as out_file:
            out_file.write(meta_data[index])


def parse_tnef(stream):
    """Parse TNEF file, get attachments and compressed RTF data form it"""
    tnef_signature = unpack_uint32(stream.read(4))
    if tnef_signature != TNEF_SIGNATURE:
        print('Invalid TNEF signature')
        exit(1)
    # read fields without printing
    stream.read(2)  # legacy_key
    read_tnef_version(stream)
    read_oem_codepage(stream)

    attach_titles = []
    attach_data = []
    attach_meta_data = []
    compressed_rtfs = []
    while True:
        try:
            attribute = read_attribute(stream)
        except struct.error:
            break
        _, id_value, _, data, _ = attribute

        if id_value == 0x00018010:  # idAttachTitle
            attach_titles.append(data.rstrip(b'\x00'))
        elif id_value == 0x0006800f:  # idAttachData
            attach_data.append(data)
        elif id_value == 0x00068011:  # idAttachMetaFile
            attach_meta_data.append(data)
        elif id_value == 0x00069003:  # idMsgProps
            compressed_rtf_data = parse_msg_props(StringIO(data))
            compressed_rtfs.extend(compressed_rtf_data)
        
    return stream.name, attach_titles, attach_data, attach_meta_data, compressed_rtfs