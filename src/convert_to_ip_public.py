# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import inspect
import ipaddress
import logging
import requests
import socket


def convert_to_ip_public(ip_or_domain: str, ip_public_version: int=4) -> str:
    """
    Converts given IP or domain, which may me local or public, to a guaranteed public IP using "https://ident.me/".

    Arguments:
    - ip_or_domain: IP given to convert
    - ip_public_version: try to convert to IPv4 or IPv6, if fails will fallback to other version, if fails again try any version, if fails again raises ValueError

    Returns:
    - ip_public: converted IP, guaranteed public

    Raises:
    - ValueError: IP or domain cannot be converted to IP object.
    - TimeoutError: Converting given IP or domain to public IP via "https://ident.me/" timed out.
    """

    ip: ipaddress.IPv4Address|ipaddress.IPv6Address         # ip which may be local or public
    ip_public: ipaddress.IPv4Address|ipaddress.IPv6Address  # ip that is guaranteed public, result
    TIMEOUT: int=50                                         # internet connection timeout


    if ip_public_version not in (4, 6):
        logging.error(f"ip_public_version ({ip_public_version}) must be 4 or 6.")
        raise ValueError(f"Error in {convert_to_ip_public.__name__}{inspect.signature(convert_to_ip_public)}: ip_public_version ({ip_public_version}) must be 4 or 6.")


    logging.info(f"Converting given IP or domain \"{ip_or_domain}\" to IP...")
    try:
        ip=ipaddress.ip_address(socket.gethostbyname(ip_or_domain)) # convert IP or domain to IP, construct IP object
    except socket.gaierror:
        logging.error(f"\rConverting given IP or domain \"{ip_or_domain}\" to IP failed. Unable to get IP address information. Check the given domain/IP and the internet connection.")
        raise ValueError(f"Error in {convert_to_ip_public.__name__}{inspect.signature(convert_to_ip_public)}: Converting given IP or domain \"{ip_or_domain}\" to IP failed. Unable to get IP address information. Check the given domain/IP and the internet connection.")
    logging.info(f"\rConverted given IP or domain \"{ip_or_domain}\" to IP \"{ip.exploded.upper()}\".")


    for _ in range(2):  # try to convert to IPv4 or IPv6, if fails will fallback to other version
        logging.info(f"Converting given IP \"{ip.exploded.upper()}\" to public IPv{ip_public_version}...")
        try:
            ip_public=ipaddress.ip_address(requests.get(f"https://{ip_public_version}.ident.me/", timeout=TIMEOUT).text)    # try to convert
        except TimeoutError:
            logging.error(f"\rConverting given IP \"{ip.exploded.upper()}\" to public IPv{ip_public_version} timed out.")
            ip_public_version=6
        except ValueError as e:
            logging.error(f"\rConverting given IP \"{ip.exploded.upper()}\" to public IPv{ip_public_version} failed with ValueError. Network does not seem to have an IPv{ip_public_version}. Error message:\n{e.args}")
            match ip_public_version: # fallback to other version
                case 4:
                    ip_public_version=6
                case 6:
                    ip_public_version=4
                case _:
                    logging.critical(f"ip_public_version ({ip_public_version}) is neither 4 nor 6 despite having checked earlier.")
                    raise RuntimeError(f"Error in {convert_to_ip_public.__name__}{inspect.signature(convert_to_ip_public)}: ip_public_version ({ip_public_version}) is neither 4 nor 6 despite having checked earlier.")
        else:
            logging.info(f"\rConverted given IP \"{ip.exploded.upper()}\" to public IPv{ip_public_version} \"{ip_public.exploded.upper()}\".")
            match ip_public_version: # specific formatting depending on version
                case 4:
                    return ip_public.exploded.upper()
                case 6:
                    return f"[{ip_public.exploded.upper()}]"
                case _:
                    logging.critical(f"ip_public_version ({ip_public_version}) is neither 4 nor 6 despite having checked earlier.")
                    raise RuntimeError(f"Error in {convert_to_ip_public.__name__}{inspect.signature(convert_to_ip_public)}: ip_public_version ({ip_public_version}) is neither 4 nor 6 despite having checked earlier.")

    logging.info(f"Converting given IP \"{ip.exploded.upper()}\" to public IP...")    # last ditch effort, try any version
    try:
        ip_public=ipaddress.ip_address(requests.get("https://ident.me/", timeout=TIMEOUT).text)                 # convert to public IP, don't care about IPv4 or IPv6
    except TimeoutError:
        logging.error(f"\rConverting given IP \"{ip.exploded.upper()}\" to public IP timed out.")
        raise
    except ValueError as e:
        logging.error(f"\rConverting given IP \"{ip.exploded.upper()}\" to public IP failed with ValueError. Network does not seem to have an IP. Error message:\n{e.args}")
        raise
    else:
        logging.info(f"\rConverted given IP \"{ip.exploded.upper()}\" to public IP \"{ip_public.exploded.upper()}\".")
        return ip_public.exploded.upper()