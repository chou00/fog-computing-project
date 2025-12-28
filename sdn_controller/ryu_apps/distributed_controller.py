"""
Distributed SDN Controller (Ryu Application)
Architecture 2: Rule-based load balancing without AI
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from ryu.lib import hub
from loguru import logger
import time


class DistributedController(app_manager.RyuApp):
    """
    Distributed SDN Controller with Rule-Based Load Balancing
    Implements load balancing using heuristics (no AI)
    """
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(DistributedController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.switch_loads = {}  # Switch ID to load mapping
        self.switch_stats = {}  # Switch statistics
        self.monitor_thread = hub.spawn(self._monitor_switches)
        logger.info("Distributed Controller (No AI) initialized")
    
    def _monitor_switches(self):
        """Monitor switch loads periodically"""
        while True:
            hub.sleep(5)  # Update every 5 seconds
            self._update_switch_loads()
    
    def _update_switch_loads(self):
        """Update load information for all switches"""
        for datapath in self.switch_stats:
            # Request flow statistics
            ofproto = datapath.ofproto
            parser = datapath.ofproto_parser
            req = parser.OFPFlowStatsRequest(datapath)
            datapath.send_msg(req)
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Handle switch features event"""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Install default flow
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)
        
        # Initialize switch stats
        self.switch_loads[datapath.id] = 0.0
        self.switch_stats[datapath] = {'packets': 0, 'bytes': 0}
        
        logger.info(f"Switch {datapath.id} connected")
    
    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply_handler(self, ev):
        """Handle flow statistics reply"""
        body = ev.msg.body
        datapath = ev.msg.datapath
        
        total_packets = 0
        total_bytes = 0
        
        for stat in body:
            total_packets += stat.packet_count
            total_bytes += stat.byte_count
        
        # Update load (simple metric: bytes per second)
        if datapath in self.switch_stats:
            prev_bytes = self.switch_stats[datapath]['bytes']
            time_delta = 5.0  # 5 seconds between updates
            if time_delta > 0:
                load = (total_bytes - prev_bytes) / time_delta / 1e6  # Mbps
                self.switch_loads[datapath.id] = load
            self.switch_stats[datapath] = {'packets': total_packets, 'bytes': total_bytes}
    
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """Add a flow entry"""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(
                datapath=datapath, buffer_id=buffer_id,
                priority=priority, match=match, instructions=inst
            )
        else:
            mod = parser.OFPFlowMod(
                datapath=datapath, priority=priority,
                match=match, instructions=inst
            )
        
        datapath.send_msg(mod)
    
    def select_next_hop(self, current_switch, destination, available_neighbors):
        """
        Select next hop using rule-based load balancing
        
        Args:
            current_switch: Current switch ID
            destination: Destination switch ID
            available_neighbors: List of neighbor switch IDs
        
        Returns:
            Selected next hop switch ID
        """
        if not available_neighbors:
            return None
        
        # Rule 1: If destination is a neighbor, route directly
        if destination in available_neighbors:
            return destination
        
        # Rule 2: Select least-loaded neighbor
        neighbor_loads = [
            (neighbor, self.switch_loads.get(neighbor, 0.0))
            for neighbor in available_neighbors
        ]
        
        # Sort by load (ascending)
        neighbor_loads.sort(key=lambda x: x[1])
        
        # Select least loaded neighbor
        selected = neighbor_loads[0][0]
        
        logger.debug(f"Selected next hop: {selected} (load: {neighbor_loads[0][1]:.2f} Mbps)")
        return selected
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Handle packet-in events with load balancing"""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        dst = eth.dst
        src = eth.src
        
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        
        # Determine output port using load balancing
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            # Use load balancing to select port
            # For simplicity, use round-robin or least-loaded
            # In real implementation, would query neighbor switches
            out_port = ofproto.OFPP_FLOOD
        
        actions = [parser.OFPActionOutput(out_port)]
        
        # Install flow rule
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        
        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id,
            in_port=in_port, actions=actions, data=data
        )
        datapath.send_msg(out)

