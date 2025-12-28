"""
Fogbed Network Topology Definition
Creates a distributed mesh topology with fog nodes and IoT devices
"""

from mininet.net import Containernet
from mininet.node import Controller, OVSSwitch, Docker
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


class FogTopology:
    """Manages the fog computing network topology"""
    
    def __init__(self, num_fog_nodes=6, num_iot_devices=20, architecture='distributed_ai'):
        """
        Initialize fog topology
        
        Args:
            num_fog_nodes: Number of fog nodes in the mesh
            num_iot_devices: Number of IoT devices
            architecture: 'centralized', 'distributed_no_ai', or 'distributed_ai'
        """
        self.num_fog_nodes = num_fog_nodes
        self.num_iot_devices = num_iot_devices
        self.architecture = architecture
        self.net = None
        self.fog_nodes = []
        self.iot_devices = []
        
    def create_topology(self):
        """Create the network topology"""
        info('*** Creating Fog Computing Topology\n')
        
        # Initialize Containernet
        self.net = Containernet(controller=Controller, switch=OVSSwitch, link=TCLink)
        
        info('*** Adding controller\n')
        # Add Ryu controller (will be started separately)
        c0 = self.net.addController('c0', controller=Controller, ip='127.0.0.1', port=6633)
        
        info('*** Adding switches (Fog Nodes)\n')
        # Create fog nodes as switches with Docker containers
        for i in range(1, self.num_fog_nodes + 1):
            fog_name = f'fog{i}'
            # Each fog node runs in a Docker container
            fog_node = self.net.addDocker(
                fog_name,
                dimage='fog-node:latest',
                dcmd='python /app/fog_node.py',
                ip=f'10.0.0.{i}/24',
                cpu_quota=50000,  # 50% CPU
                mem_limit='512m'
            )
            self.fog_nodes.append(fog_node)
            
            # Create switch for fog node
            switch = self.net.addSwitch(f's{i}', cls=OVSSwitch, protocols='OpenFlow13')
            self.net.addLink(fog_node, switch, bw=1000, delay='1ms')
        
        info('*** Creating mesh connections between fog nodes\n')
        # Create mesh topology between fog nodes
        for i in range(len(self.fog_nodes)):
            for j in range(i + 1, len(self.fog_nodes)):
                # Connect switches (fog nodes) in mesh
                self.net.addLink(
                    self.net.get(f's{i+1}'),
                    self.net.get(f's{j+1}'),
                    bw=100,  # 100 Mbps between fog nodes
                    delay='5ms'
                )
        
        info('*** Adding IoT devices\n')
        # Create IoT devices
        for i in range(1, self.num_iot_devices + 1):
            iot_name = f'iot{i}'
            # IoT devices as lightweight containers
            iot_device = self.net.addDocker(
                iot_name,
                dimage='iot-device:latest',
                dcmd='python /app/iot_client.py',
                ip=f'10.0.1.{i}/24',
                cpu_quota=10000,  # 10% CPU
                mem_limit='128m'
            )
            self.iot_devices.append(iot_device)
            
            # Connect IoT device to nearest fog node (round-robin assignment)
            fog_idx = (i - 1) % len(self.fog_nodes)
            fog_switch = self.net.get(f's{fog_idx + 1}')
            self.net.addLink(iot_device, fog_switch, bw=10, delay='2ms')
        
        info('*** Adding cloud node (monitoring only)\n')
        # Cloud node for monitoring (not involved in routing)
        cloud = self.net.addDocker(
            'cloud',
            dimage='cloud-monitor:latest',
            dcmd='python /app/cloud_monitor.py',
            ip='10.0.2.1/24',
            cpu_quota=20000,
            mem_limit='256m'
        )
        cloud_switch = self.net.addSwitch('s0', cls=OVSSwitch, protocols='OpenFlow13')
        self.net.addLink(cloud, cloud_switch, bw=1000, delay='10ms')
        
        # Connect cloud to one fog node
        self.net.addLink(cloud_switch, self.net.get('s1'), bw=100, delay='10ms')
        
        info('*** Topology created\n')
        return self.net
    
    def start(self):
        """Start the network"""
        if self.net is None:
            self.create_topology()
        
        info('*** Starting network\n')
        self.net.start()
        
        info('*** Configuring OpenFlow switches\n')
        # Configure switches for OpenFlow
        for i in range(1, self.num_fog_nodes + 1):
            switch = self.net.get(f's{i}')
            # Set OpenFlow controller
            switch.cmd('ovs-vsctl set-controller', switch, 'tcp:127.0.0.1:6633')
        
        info('*** Network started\n')
        return self.net
    
    def stop(self):
        """Stop the network"""
        if self.net:
            info('*** Stopping network\n')
            self.net.stop()
            self.net = None
    
    def get_fog_nodes(self):
        """Get list of fog node containers"""
        return self.fog_nodes
    
    def get_iot_devices(self):
        """Get list of IoT device containers"""
        return self.iot_devices


def create_topology(num_fog_nodes=6, num_iot_devices=20, architecture='distributed_ai'):
    """
    Factory function to create topology
    
    Args:
        num_fog_nodes: Number of fog nodes
        num_iot_devices: Number of IoT devices
        architecture: Architecture type
    """
    topology = FogTopology(num_fog_nodes, num_iot_devices, architecture)
    return topology


if __name__ == '__main__':
    setLogLevel('info')
    
    # Create and start topology
    topo = create_topology(num_fog_nodes=6, num_iot_devices=20)
    net = topo.start()
    
    try:
        CLI(net)
    finally:
        topo.stop()

