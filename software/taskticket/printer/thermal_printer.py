from escpos.printer import Usb
from typing import Optional, Dict
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv
import usb.core
import usb.util
from dataclasses import dataclass
from printer.logo import raster_logo

logger = logging.getLogger(__name__)

@dataclass
class ThermalFormatting:
    """ESC/POS formatting commands"""
    # Basic formatting
    INIT = '\x1b\x40'  # Initialize printer
    BOLD_ON = '\x1b\x45\x01'
    BOLD_OFF = '\x1b\x45\x00'
    UNDERLINE_ON = '\x1b\x2d\x01'
    UNDERLINE_OFF = '\x1b\x2d\x00'
    REVERSE_ON = '\x1d\x42\x01'
    REVERSE_OFF = '\x1d\x42\x00'
    
    # Text size
    NORMAL = '\x1b\x21\x00'
    DOUBLE_HEIGHT = '\x1b\x21\x10'
    DOUBLE_WIDTH = '\x1b\x21\x20'
    DOUBLE_SIZE = '\x1b\x21\x30'
    
    # Alignment
    ALIGN_LEFT = '\x1b\x61\x00'
    ALIGN_CENTER = '\x1b\x61\x01'
    ALIGN_RIGHT = '\x1b\x61\x02'
    
    # Paper control
    FEED_LINE = '\n'
    FEED_AND_CUT = '\n\n\n\n\x1d\x56\x41\x03'
    
    @staticmethod
    def create_header(text: str) -> str:
        """Create a centered header with borders"""
        border = "=" * 48
        return f"{border}\n{text.center(48)}\n{border}"

class ThermalPrinter:
    def __init__(self):
        load_dotenv()
        
        # Get printer configuration from environment variables
        self.vendor_id = int(os.getenv('PRINTER_VENDOR_ID', '0x0416'), 16)
        self.product_id = int(os.getenv('PRINTER_PRODUCT_ID', '0x5011'), 16)
        self.in_ep = int(os.getenv('PRINTER_IN_EP', '0x82'), 16)
        self.out_ep = int(os.getenv('PRINTER_OUT_EP', '0x01'), 16)
        
        self.printer = None
        self.is_initialized = False
        self.debug_mode = os.getenv('PRINTER_DEBUG', 'false').lower() == 'true'
        
        # Add formatting helper
        self.format = ThermalFormatting()
        
        # Use direct access by default
        self.use_direct_access = True
        self.printer_device = '/dev/usb/lp0'
    
    def initialize(self) -> bool:
        """Initialize the printer connection."""
        if self.is_initialized:
            return True
        
        if self.use_direct_access:
            try:
                # Check if printer device exists
                if not os.path.exists(self.printer_device):
                    print(f"Printer device {self.printer_device} not found.")
                    return False
                
                # Test if we can write to it
                with open(self.printer_device, 'wb') as f:
                    f.write(b'\x1b@')  # ESC @ - initialize printer
                
                self.is_initialized = True
                print(f"Printer initialized successfully using direct access to {self.printer_device}")
                return True
            except Exception as e:
                print(f"Error initializing printer with direct access: {e}")
                return False
        else:
            # Original USB initialization
            try:
                # Find the printer device
                device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
                
                if device is None:
                    print(f"Printer not found. Vendor ID: {self.vendor_id:04x}, Product ID: {self.product_id:04x}")
                    return False

                # Try to connect to the printer
                try:
                    self.printer = Usb(
                        self.vendor_id,
                        self.product_id,
                        timeout=0,
                        in_ep=self.in_ep,
                        out_ep=self.out_ep
                    )
                    self.is_initialized = True
                    print("Printer initialized successfully!")
                    return True
                    
                except Exception as e:
                    print(f"Error connecting to printer: {e}")
                    return False
                
            except Exception as e:
                print(f"Printer initialization error: {e}")
                return False

    def print_text(self, text: str, logo: bool = False) -> bool:
        """Print text to the thermal printer."""
        logo_bytes = b''
        if logo and os.getenv('PRINTER_TASK_LOGO', '1').lower() in ('1', 'true', 'yes'):
            try:
                logo_path = Path(__file__).resolve().parents[1] / 'static/lumon-print.png'
                logo_bytes = raster_logo(logo_path, int(os.getenv('PRINTER_WIDTH_DOTS', '576')))
            except (OSError, ValueError):
                # Prepare everything before opening USB. A missing asset must
                # not prevent the task text from printing.
                logger.warning('Ticket logo unavailable; printing the task text only.')
        if self.debug_mode:
            print("\n=== DEBUG: PRINTER OUTPUT ===")
            if logo_bytes:
                print('[Lumon bitmap logo]')
            print(text)
            print("===========================\n")
            return True
            
        if not self.is_initialized and not self.initialize():
            return False
            
        try:
            if self.use_direct_access:
                # Print using direct file access
                with open(self.printer_device, 'wb') as f:
                    # One job, no reset between image and task, one final cut.
                    job = (self.format.INIT.encode('utf-8') + logo_bytes +
                           text.encode('utf-8', errors='replace') +
                           self.format.FEED_AND_CUT.encode('utf-8'))
                    f.write(job)
            else:
                # Print using python-escpos
                self.printer.text(self.format.INIT)
                if logo_bytes:
                    self.printer._raw(logo_bytes)
                self.printer.text(text)
                self.printer.text(self.format.FEED_AND_CUT)
                
            return True
                
        except Exception as e:
            print(f"Printing error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_printer(self) -> bool:
        """Print a test page with all formatting options."""
        test_text = (
            f"{self.format.INIT}"  # Initialize printer
            f"{self.format.create_header('PRINTER TEST')}\n\n"
            "Normal text\n"
            f"{self.format.DOUBLE_HEIGHT}Double Height Text\n"
            f"{self.format.DOUBLE_WIDTH}Double Width Text\n"
            f"{self.format.DOUBLE_SIZE}Large Text\n"
            f"{self.format.NORMAL}"  # Reset to normal
            f"{self.format.BOLD_ON}Bold Text\n"
            f"{self.format.BOLD_OFF}Normal Text\n"
            f"{self.format.UNDERLINE_ON}Underlined Text\n"
            f"{self.format.UNDERLINE_OFF}Normal Text\n"
            f"{self.format.REVERSE_ON}Reverse Text\n"
            f"{self.format.REVERSE_OFF}Normal Text\n\n"
            f"{self.format.ALIGN_LEFT}Left aligned\n"
            f"{self.format.ALIGN_CENTER}Center aligned\n"
            f"{self.format.ALIGN_RIGHT}Right aligned\n"
            f"{self.format.ALIGN_LEFT}"  # Reset alignment
            "\n┌──────────────┐\n"
            "│  Box Test    │\n"
            "└──────────────┘\n\n"
            "Test Complete!\n"
        )
        return self.print_text(test_text)

    def print_simple_test(self) -> bool:
        """Print a simple test without any special formatting."""
        if not self.initialize():
            return False
            
        try:
            test_text = (
                f"{self.format.INIT}"
                f"{self.format.create_header('BASIC PRINTER TEST')}\n\n"
                "Normal text\n"
                f"{self.format.BOLD_ON}Bold text\n"
                f"{self.format.BOLD_OFF}Normal text\n"
                f"{self.format.DOUBLE_SIZE}Large text\n"
                f"{self.format.NORMAL}Back to normal\n"
                "Test complete!\n"
            )
            
            return self.print_text(test_text)
            
        except Exception as e:
            print(f"Printing error: {str(e)}")
            return False

    def print_ticket(self, title: str, content: Dict[str, str], footer: str = "") -> bool:
        """Print a formatted ticket."""
        try:
            ticket_text = (
                f"{self.format.INIT}"
                f"{self.format.ALIGN_CENTER}"
                f"{self.format.create_header(title)}\n\n"
                f"{self.format.ALIGN_LEFT}"
            )
            
            # Add content
            for key, value in content.items():
                ticket_text += f"{self.format.BOLD_ON}{key}:{self.format.BOLD_OFF} {value}\n"
            
            # Add footer if provided
            if footer:
                ticket_text += (
                    f"\n{self.format.ALIGN_CENTER}"
                    f"{footer}\n"
                    f"{self.format.ALIGN_LEFT}"
                )
            
            return self.print_text(ticket_text)
            
        except Exception as e:
            print(f"Error printing ticket: {str(e)}")
            return False

def find_printer():
    """Utility function to find USB printer IDs and suggest .env settings."""
    devices = usb.core.find(find_all=True)
    
    print("Available USB devices:")
    print("\nAdd these lines to your .env file for detected printers:\n")
    
    found_printers = False
    for device in devices:
        try:
            if device.product and ('POS' in device.product or 'print' in device.product.lower()):
                found_printers = True
                print(f"# {device.manufacturer} - {device.product}")
                print(f"PRINTER_VENDOR_ID=0x{device.idVendor:04x}")
                print(f"PRINTER_PRODUCT_ID=0x{device.idProduct:04x}")
                print(f"PRINTER_IN_EP=0x82  # Default value, might need adjustment")
                print(f"PRINTER_OUT_EP=0x01  # Default value, might need adjustment")
                print("PRINTER_DEBUG=false")
                print()
                
                # Try to get endpoint information
                try:
                    cfg = device.get_active_configuration()
                    intf = cfg[(0,0)]
                    ep_in = usb.util.find_descriptor(
                        intf,
                        custom_match=lambda e: \
                            usb.util.endpoint_direction(e.bEndpointAddress) == \
                            usb.util.ENDPOINT_IN
                    )
                    ep_out = usb.util.find_descriptor(
                        intf,
                        custom_match=lambda e: \
                            usb.util.endpoint_direction(e.bEndpointAddress) == \
                            usb.util.ENDPOINT_OUT
                    )
                    if ep_in and ep_out:
                        print(f"# Detected endpoints:")
                        print(f"# IN_EP=0x{ep_in.bEndpointAddress:02x}")
                        print(f"# OUT_EP=0x{ep_out.bEndpointAddress:02x}")
                        print()
                except:
                    pass
        except:
            pass
    
    if not found_printers:
        print("No POS/printer devices found!")

if __name__ == "__main__":
    # Find available printers
    find_printer()
    
    # Test the printer
    print("\nTesting printer...")
    printer = ThermalPrinter()
    print("\nRunning simple test first...")
    printer.print_simple_test()
    print("\nRunning formatted test...")
    printer.test_printer()
