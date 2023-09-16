# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import inspect
import ipaddress
import logging
import requests
import socket


def convert_to_ip_global(ip_or_domain: str) -> ipaddress.IPv4Address|ipaddress.IPv6Address:
    """
    Converts given IP or domain, which may me local or global, to a guaranteed global IP using "https://ident.me/".

    Arguments:
    - ip_local: IP to convert

    Returns:
    - ip_global: converted IP, guaranteed global

    Raises:
    - ValueError: IP or domain cannot be converted to IP object.
    - TimeoutError: Converting local IP to global IP via "https://ident.me/" timed out.
    """

    ip_local_or_global: ipaddress.IPv4Address|ipaddress.IPv6Address # ip which may be local or global
    ip_global: ipaddress.IPv4Address|ipaddress.IPv6Address          # ip that is guaranteed global, result
    TIMEOUT: int=50                                                 # internet connection timeout


    logging.info(f"Converting given IP or domain \"{ip_or_domain}\" to IP...")
    try:
        ip_local_or_global=ipaddress.ip_address(socket.gethostbyname(ip_or_domain)) # convert domain to IP, construct IP object
    except socket.gaierror:
        logging.error(f"\rConverting given IP or domain \"{ip_or_domain}\" to IP failed. Unable to get IP address information. Check the given domain/IP and the internet connection.")
        raise ValueError(f"Error in {convert_to_ip_global.__name__}{inspect.signature(convert_to_ip_global)}: Converting given IP or domain \"{ip_or_domain}\" to IP failed. Unable to get IP address information. Check the given domain/IP and the internet connection.")
    logging.info(f"\rConverted given IP or domain \"{ip_or_domain}\" to IP \"{ip_local_or_global.exploded.upper()}\".")

    if ip_local_or_global.is_global==True:  # if already global IP: work done, return
        ip_global=ip_local_or_global
        return ip_global

    logging.info(f"Converting local IP \"{ip_local_or_global.exploded.upper()}\" to global IPv4...")
    try:
        ip_global=ipaddress.ip_address(requests.get("https://4.ident.me/", timeout=TIMEOUT).text)   # try to convert to global IPv4 first
    except TimeoutError:
        logging.error(f"\rConverting local IP \"{ip_local_or_global.exploded.upper()}\" to global IPv4 timed out.")
        raise
    except ValueError:
        logging.error(f"\rConverting local IP \"{ip_local_or_global.exploded.upper()}\" to global IPv4 failed with ValueError. Response from  https://4.ident.me/: \"{requests.get('https://4.ident.me/', timeout=TIMEOUT)}\" Network does not seem to have an IPv4.")
    else:
        logging.info(f"\rConverted local IP \"{ip_local_or_global.exploded.upper()}\" to global IPv4 \"{ip_global.exploded.upper()}\".")
        return ip_global
    
    logging.info(f"Converting local IP \"{ip_local_or_global.exploded.upper()}\" to global IP...")
    try:
        ip_global=ipaddress.ip_address(requests.get("https://ident.me/", timeout=TIMEOUT).text) # convert to global IP, don't care about IPv4 or IPv6
    except TimeoutError:
        logging.error(f"\rConverting local IP \"{ip_local_or_global.exploded.upper()}\" to global IP timed out.")
        raise
    else:
        logging.info(f"\rConverted local IP \"{ip_local_or_global.exploded.upper()}\" to global IP \"{ip_global.exploded.upper()}\".")
        return ip_global