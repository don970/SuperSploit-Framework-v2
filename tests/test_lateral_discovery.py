
import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Dynamically resolve paths
current_dir = os.path.dirname(os.path.abspath(__file__))
framework_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(framework_root, "source"))
sys.path.append(os.path.join(framework_root, "recon", "native-discovery"))

# Mock Scapy before importing the module
sys.modules['scapy'] = MagicMock()
sys.modules['scapy.all'] = MagicMock()
sys.modules['scapy.error'] = MagicMock()

import lateral_discovery

class TestLateralDiscovery(unittest.TestCase):
    def setUp(self):
        self.engine = lateral_discovery.LateralDiscoveryEngine(debug_mode=False)

    @patch('lateral_discovery.sr')
    def test_nbns_parsing(self, mock_sr):
        # Mock a Scapy response for NBNS
        mock_rcv = MagicMock()
        mock_rcv.src = "192.168.1.50"
        mock_rcv.haslayer.return_value = True
        
        # Create a fake raw layer with a NetBIOS name at index 57
        fake_raw = MagicMock()
        # "WORKSTATION-01" is 14 chars, padded to 15
        name = "WORKSTATION-01 ".encode('utf-8')
        fake_raw.load = b"A" * 57 + name + b"B" * 10
        mock_rcv.getlayer.return_value = fake_raw
        
        mock_sr.return_value = ([(None, mock_rcv)], [])
        
        results = self.engine.nbns_sweep("192.168.1.255")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ip'], "192.168.1.50")
        self.assertEqual(results[0]['hostname'], "WORKSTATION-01")
        self.assertEqual(results[0]['protocol'], "NBNS")

    @patch('lateral_discovery.sr')
    def test_mdns_sweep(self, mock_sr):
        mock_rcv = MagicMock()
        mock_rcv.src = "192.168.1.60"
        mock_rcv.haslayer.side_effect = lambda layer: layer == lateral_discovery.DNS
        
        # Mock DNS layer with a PTR record
        mock_dns = MagicMock()
        mock_dns.ancount = 1
        mock_ptr = MagicMock()
        mock_ptr.type = 12 # PTR
        mock_ptr.rdata = b"MyPrinter._ipp._tcp.local."
        mock_dns.an = [mock_ptr]
        mock_rcv.__getitem__.return_value = mock_dns
        
        mock_sr.return_value = ([(None, mock_rcv)], [])
        
        results = self.engine.mdns_sweep()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ip'], "192.168.1.60")
        self.assertEqual(results[0]['hostname'], "MyPrinter")
        self.assertEqual(results[0]['protocol'], "mDNS")

    @patch('lateral_discovery.sr')
    def test_llmnr_sweep(self, mock_sr):
        mock_rcv = MagicMock()
        mock_rcv.src = "192.168.1.70"
        mock_rcv.haslayer.side_effect = lambda layer: layer == lateral_discovery.DNS
        
        # Mock DNS layer with an Answer record
        mock_dns = MagicMock()
        mock_dns.ancount = 1
        mock_an = MagicMock()
        mock_an.rrname = b"WORKSTATION-X.local."
        mock_dns.an = [mock_an]
        mock_rcv.__getitem__.return_value = mock_dns
        
        mock_sr.return_value = ([(None, mock_rcv)], [])
        
        results = self.engine.llmnr_sweep()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ip'], "192.168.1.70")
        self.assertEqual(results[0]['hostname'], "WORKSTATION-X")
        self.assertEqual(results[0]['protocol'], "LLMNR")

    @patch('lateral_discovery.sr')
    def test_ssdp_sweep(self, mock_sr):
        mock_rcv = MagicMock()
        mock_rcv.src = "192.168.1.80"
        mock_rcv.haslayer.side_effect = lambda layer: layer == lateral_discovery.Raw
        
        # Mock Raw layer with SSDP response
        mock_raw = MagicMock()
        mock_raw.load = b"HTTP/1.1 200 OK\r\nSERVER: OS/version UPnP/1.1 product/version\r\nLOCATION: http://192.168.1.80/desc.xml\r\n"
        mock_rcv.getlayer.return_value = mock_raw
        
        mock_sr.return_value = ([(None, mock_rcv)], [])
        
        results = self.engine.ssdp_sweep()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['ip'], "192.168.1.80")
        self.assertEqual(results[0]['hostname'], "OS/version UPnP/1.1 product/version")
        self.assertEqual(results[0]['protocol'], "SSDP")

    @patch('lateral_discovery.DatabaseManagment')
    @patch('lateral_discovery.LateralDiscoveryEngine')
    def test_start_logic(self, mock_engine_class, mock_db):
        mock_engine = mock_engine_class.return_value
        
        # Setup mock returns for sweeps
        mock_engine.nbns_sweep.return_value = [{'ip': '192.168.1.10', 'hostname': 'SRV-01', 'protocol': 'NBNS'}]
        mock_engine.mdns_sweep.return_value = [{'ip': '192.168.1.10', 'hostname': 'mDNS Responder', 'protocol': 'mDNS'}]
        mock_engine.llmnr_sweep.return_value = [{'ip': '192.168.1.20', 'hostname': 'Windows (LLMNR)', 'protocol': 'LLMNR'}]
        mock_engine.ssdp_sweep.return_value = [{'ip': '192.168.1.30', 'hostname': 'UPnP Device', 'protocol': 'SSDP'}]
        
        # Mock database targets
        mock_db.getTargets.return_value = {}
        
        # Run the Start function logic (partially mocked)
        with patch('lateral_discovery.has_db_manager', True):
            lateral_discovery.Start()
            
        # Verify updateTargets was called with merged data
        args, kwargs = mock_db.updateTargets.call_args
        updated_targets = args[0]
        
        self.assertIn('192.168.1.10', updated_targets)
        self.assertEqual(updated_targets['192.168.1.10']['hostname'], 'SRV-01')
        self.assertIn('NBNS', updated_targets['192.168.1.10']['discovery_method'])
        self.assertIn('mDNS', updated_targets['192.168.1.10']['discovery_method'])
        
        self.assertIn('192.168.1.20', updated_targets)
        self.assertIn('192.168.1.30', updated_targets)

if __name__ == "__main__":
    unittest.main()
