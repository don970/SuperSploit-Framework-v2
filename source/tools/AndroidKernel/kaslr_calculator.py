#!/usr/bin/env python3
import sys
import argparse

def calculate(leaked, static, slide):
    """
    Calculates the missing KASLR parameter.
    
    KASLR (Kernel Address Space Layout Randomization) moves the kernel base in memory.
    The 'slide' is the offset added to the 'static' (default) base address.
    
    Formula: Leaked = Static + Slide
    """
    try:
        # Convert hex strings to integers
        l = int(leaked, 16) if leaked else None
        s = int(static, 16) if static else None
        sl = int(slide, 16) if slide else None

        results = {}
        
        if l is not None and s is not None:
            results['slide'] = l - s
            results['leaked'] = l
            results['static'] = s
        elif l is not None and sl is not None:
            results['static'] = l - sl
            results['leaked'] = l
            results['slide'] = sl
        elif s is not None and sl is not None:
            results['leaked'] = s + sl
            results['static'] = s
            results['slide'] = sl
        else:
            return None
        
        return results
    except ValueError as e:
        print(f"[-] Error: Invalid hex value provided: {e}")
        return None

def main():
    print("========================================")
    print("      SuperSploit KASLR Calculator")
    print("========================================\n")

    parser = argparse.ArgumentParser(description="Conceptual KASLR Slide Calculator")
    parser.add_argument("-l", "--leaked", help="Leaked address (hex, e.g., 0xffffffc012345678)")
    parser.add_argument("-s", "--static", help="Static/Default kernel base address (hex, e.g., 0xffffffc000080000)")
    parser.add_argument("-k", "--slide", help="KASLR slide (hex, e.g., 0x122c5678)")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    # If no arguments are provided, or interactive mode is requested
    if args.interactive or (not args.leaked and not args.static and not args.slide):
        print("[*] Entering Interactive Mode (Leave blank if unknown)")
        print("[*] Common Static Bases:")
        print("    - x86_64 Linux:      0xffffffff81000000")
        print("    - aarch64 Android:   0xffffffc000080000")
        print("    - aarch64 Android 12+: 0xffffff8008000000\n")
        
        leaked = input("Enter Leaked Address (hex): ").strip()
        static = input("Enter Static Base Address (hex): ").strip()
        slide = input("Enter KASLR Slide (hex): ").strip()
    else:
        leaked = args.leaked
        static = args.static
        slide = args.slide

    res = calculate(leaked, static, slide)

    if res:
        print("\n--- KASLR Calculation Results ---")
        print(f"Leaked Address:  {hex(res['leaked'])}")
        print(f"Static Base:    {hex(res['static'])}")
        print(f"KASLR Slide:    {hex(res['slide'])}")
        print(f"KASLR Slide:    {res['slide']} (decimal)")
        print("---------------------------------\n")
        print("[*] Note: The slide is typically aligned to 2MB (0x200000) or similar pages.")
    else:
        print("[-] Error: Need at least two values to calculate the third.")

if __name__ == "__main__":
    main()
