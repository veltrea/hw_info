import argparse
import json
import sys
import psutil
import wmi
import yaml
import csv
import io
from datetime import datetime
from typing import Dict, Any, List, Optional

class HardwareInfo:
    def __init__(self, fast_mode: bool = False, threads: int = None, timeout: int = None):
        self.wmi = wmi.WMI()
        self.fast_mode = fast_mode
        self.threads = threads
        self.timeout = timeout

    def get_system_info(self, minimal: bool = False, exclude_serials: bool = False) -> Dict[str, Any]:
        os_info = self.wmi.Win32_OperatingSystem()[0]
        cs_info = self.wmi.Win32_ComputerSystem()[0]
        
        system_info = {
            "hostname": cs_info.Name,
            "os": {
                "name": os_info.Caption,
                "version": os_info.Version,
                "architecture": os_info.OSArchitecture,
            }
        }

        if not minimal:
            system_info["os"].update({
                "build_number": os_info.BuildNumber,
                "install_date": str(os_info.InstallDate),
                "last_boot": str(os_info.LastBootUpTime),
                "manufacturer": os_info.Manufacturer,
            })
            
            if not exclude_serials:
                system_info["os"]["serial_number"] = os_info.SerialNumber

        return system_info

    def get_cpu_info(self, minimal: bool = False) -> Dict[str, Any]:
        cpu = self.wmi.Win32_Processor()[0]
        
        cpu_info = {
            "name": cpu.Name.strip(),
            "cores": cpu.NumberOfCores,
            "threads": cpu.NumberOfLogicalProcessors,
            "architecture": cpu.AddressWidth,
        }

        if not minimal:
            cpu_info.update({
                "manufacturer": cpu.Manufacturer,
                "max_clock_speed": cpu.MaxClockSpeed,
                "socket": cpu.SocketDesignation,
                "status": cpu.Status,
                "virtualization": cpu.VirtualizationFirmwareEnabled,
            })

        return cpu_info

    def get_memory_info(self, minimal: bool = False) -> Dict[str, Any]:
        total_memory = psutil.virtual_memory().total
        memory_banks = self.wmi.Win32_PhysicalMemory()
        
        memory_info = {
            "total": total_memory,
            "banks": []
        }

        for bank in memory_banks:
            bank_info = {
                "capacity": bank.Capacity,
                "speed": bank.Speed,
            }
            
            if not minimal:
                bank_info.update({
                    "manufacturer": bank.Manufacturer,
                    "part_number": bank.PartNumber.strip(),
                    "device_locator": bank.DeviceLocator,
                })

            memory_info["banks"].append(bank_info)

        return memory_info

    def get_storage_info(self, minimal: bool = False, exclude_serials: bool = False) -> Dict[str, Any]:
        disks = self.wmi.Win32_DiskDrive()
        storage_info = []

        for disk in disks:
            disk_info = {
                "name": disk.Caption,
                "size": disk.Size,
                "interface_type": disk.InterfaceType,
            }

            if not minimal:
                disk_info.update({
                    "manufacturer": disk.Manufacturer,
                    "model": disk.Model,
                    "partitions": disk.Partitions,
                    "status": disk.Status,
                })
                
                if not exclude_serials:
                    disk_info["serial_number"] = disk.SerialNumber.strip()

            storage_info.append(disk_info)

        return storage_info

    def get_gpu_info(self, minimal: bool = False) -> Dict[str, Any]:
        gpus = self.wmi.Win32_VideoController()
        gpu_info = []

        for gpu in gpus:
            gpu_data = {
                "name": gpu.Name.strip(),
                "adapter_ram": gpu.AdapterRAM if gpu.AdapterRAM is not None else 0,
                "driver_version": gpu.DriverVersion,
            }

            if not minimal:
                gpu_data.update({
                    "video_processor": gpu.VideoProcessor,
                    "video_memory_type": gpu.VideoMemoryType,
                    "video_architecture": gpu.VideoArchitecture,
                    "status": gpu.Status,
                })

            gpu_info.append(gpu_data)

        return gpu_info

    def get_motherboard_info(self, minimal: bool = False, exclude_serials: bool = False) -> Dict[str, Any]:
        board = self.wmi.Win32_BaseBoard()[0]
        bios = self.wmi.Win32_BIOS()[0]
        
        mb_info = {
            "manufacturer": board.Manufacturer,
            "product": board.Product,
        }

        if not minimal:
            mb_info.update({
                "version": board.Version,
                "bios_manufacturer": bios.Manufacturer,
                "bios_version": bios.Version,
                "bios_release_date": str(bios.ReleaseDate),
            })
            
            if not exclude_serials:
                mb_info.update({
                    "serial_number": board.SerialNumber.strip(),
                    "bios_serial_number": bios.SerialNumber.strip(),
                })

        return mb_info

    def collect_all(self, minimal: bool = False, exclude_serials: bool = False) -> Dict[str, Any]:
        return {
            "system": self.get_system_info(minimal, exclude_serials),
            "cpu": self.get_cpu_info(minimal),
            "memory": self.get_memory_info(minimal),
            "storage": self.get_storage_info(minimal, exclude_serials),
            "gpu": self.get_gpu_info(minimal),
            "motherboard": self.get_motherboard_info(minimal, exclude_serials),
        }

def main():
    parser = argparse.ArgumentParser(description="Hardware Information Tool")
    
    # Format options
    parser.add_argument("--format", choices=["text", "json", "yaml", "csv"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("--pretty", action="store_true",
                        help="Pretty print JSON output")
    
    # Detail level options
    parser.add_argument("--minimal", action="store_true",
                        help="Show only essential information")
    parser.add_argument("--detailed", action="store_true",
                        help="Show detailed information (default)")
    
    # Component selection
    parser.add_argument("--cpu", action="store_true",
                        help="Show CPU information only")
    parser.add_argument("--memory", action="store_true",
                        help="Show memory information only")
    parser.add_argument("--storage", action="store_true",
                        help="Show storage information only")
    parser.add_argument("--gpu", action="store_true",
                        help="Show GPU information only")
    parser.add_argument("--motherboard", action="store_true",
                        help="Show motherboard information only")
    parser.add_argument("--all", action="store_true",
                        help="Show all hardware information")
    
    # Output options
    parser.add_argument("--output", type=str,
                        help="Output file path")
    parser.add_argument("--no-timestamps", action="store_true",
                        help="Exclude timestamps from output")
    parser.add_argument("--exclude-serials", action="store_true",
                        help="Exclude serial numbers from output")
    
    # Performance options
    parser.add_argument("--fast", action="store_true",
                        help="Enable fast mode (may reduce accuracy)")
    parser.add_argument("--threads", type=int,
                        help="Number of threads to use")
    parser.add_argument("--timeout", type=int,
                        help="Timeout in seconds")
    
    # Other options
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress non-error output")
    parser.add_argument("--utf8", action="store_true",
                        help="Use UTF-8 encoding for output")

    args = parser.parse_args()
    
    if args.utf8:
        sys.stdout.reconfigure(encoding='utf-8')

    hw = HardwareInfo(fast_mode=args.fast, threads=args.threads, timeout=args.timeout)
    
    # Determine which components to show
    show_all = args.all or not any([args.cpu, args.memory, args.storage, args.gpu, args.motherboard])
    
    # Collect information
    data = {}
    if show_all:
        data = hw.collect_all(args.minimal, args.exclude_serials)
    else:
        if args.cpu:
            data["cpu"] = hw.get_cpu_info(args.minimal)
        if args.memory:
            data["memory"] = hw.get_memory_info(args.minimal)
        if args.storage:
            data["storage"] = hw.get_storage_info(args.minimal, args.exclude_serials)
        if args.gpu:
            data["gpu"] = hw.get_gpu_info(args.minimal)
        if args.motherboard:
            data["motherboard"] = hw.get_motherboard_info(args.minimal, args.exclude_serials)
    
    # Add timestamp if requested
    if not args.no_timestamps:
        data["timestamp"] = datetime.now().isoformat()
    
    # Format output
    output = ""
    if args.format == "json":
        if args.pretty:
            output = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            output = json.dumps(data, ensure_ascii=False)
    elif args.format == "yaml":
        output = yaml.dump(data, allow_unicode=True)
    elif args.format == "csv":
        output = ""
        csv_buffer = io.StringIO()
        writer = csv.writer(csv_buffer)
        
        def flatten_dict(d, parent_key=''):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key).items())
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        if isinstance(item, dict):
                            items.extend(flatten_dict(item, f"{new_key}[{i}]").items())
                        else:
                            items.append((f"{new_key}[{i}]", str(item)))
                else:
                    items.append((new_key, str(v)))
            return dict(items)
        
        flattened = flatten_dict(data)
        writer.writerow(flattened.keys())
        writer.writerow(flattened.values())
        output = csv_buffer.getvalue()
    else:  # text format
        def dict_to_text(d, indent=0):
            text = ""
            for k, v in d.items():
                if isinstance(v, dict):
                    text += " " * indent + f"{k}:\n{dict_to_text(v, indent + 2)}"
                elif isinstance(v, list):
                    text += " " * indent + f"{k}:\n"
                    for item in v:
                        if isinstance(item, dict):
                            text += dict_to_text(item, indent + 2)
                        else:
                            text += " " * (indent + 2) + f"{item}\n"
                else:
                    text += " " * indent + f"{k}: {v}\n"
            return text
        
        output = dict_to_text(data)
    
    # Output results
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        if not args.quiet:
            print(f"Results written to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()