"""
AI-Enhanced SDN Controller (Ryu Application)
Architecture 3: Distributed fog with AI (LSTM, Autoencoder, RL)
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from ryu.lib import hub
from loguru import logger
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from ai_models.lstm.model import LoadPredictor
from ai_models.autoencoder.model import AnomalyDetectionModel
from ai_models.rl.dqn_agent import DQNAgent
from fog_nodes.load_monitor import LoadMonitor


class AIRoutingApp(app_manager.RyuApp):
    """
    AI-Enhanced SDN Controller
    Integrates LSTM, Autoencoder, and RL for intelligent routing
    """
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(AIRoutingApp, self).__init__(*args, **kwargs)
        
        # Initialize AI components
        self.load_predictor = LoadPredictor(
            input_size=5,
            hidden_size=64,
            num_layers=2,
            sequence_length=60
        )
        
        self.anomaly_detector = AnomalyDetectionModel(
            input_size=10,
            encoding_dim=5,
            anomaly_threshold=0.1
        )
        
        # RL agent: state_size includes current metrics, predicted load, 
        # anomaly score, and neighbor states (approx 25 features)
        state_size = 25
        action_size = 5  # Max 5 neighbors
        self.rl_agent = DQNAgent(
            state_size=state_size,
            action_size=action_size,
            learning_rate=0.001,
            gamma=0.95
        )
        
        # Monitoring
        self.load_monitor = LoadMonitor(node_id='controller')
        self.metrics_history = []
        
        # Switch management
        self.switch_metrics = {}  # Switch ID to metrics
        self.switch_neighbors = {}  # Switch ID to neighbor list
        self.mac_to_port = {}
        
        # Start monitoring thread
        self.monitor_thread = hub.spawn(self._monitoring_loop)
        
        logger.info("AI Routing App initialized")
    
    def _monitoring_loop(self):
        """Continuous monitoring and AI update loop"""
        while True:
            hub.sleep(10)  # Update every 10 seconds
            
            # Collect metrics
            metrics = self.load_monitor.collect_metrics()
            self.metrics_history.append(metrics)
            
            # Keep only recent history
            if len(self.metrics_history) > 300:
                self.metrics_history = self.metrics_history[-300:]
            
            # Retrain LSTM periodically
            if len(self.metrics_history) > 120:
                try:
                    self.load_predictor.train(self.metrics_history, epochs=5)
                except Exception as e:
                    logger.error(f"Error training LSTM: {e}")
    
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
        
        # Initialize switch data
        self.switch_metrics[datapath.id] = {'load': 0.0, 'anomaly_score': 0.0}
        self.switch_neighbors[datapath.id] = []
        
        logger.info(f"Switch {datapath.id} connected")
    
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
    
    def ai_route_decision(self, current_switch, destination, packet_info):
        """
        Make routing decision using AI components
        
        Args:
            current_switch: Current switch ID
            destination: Destination switch ID
            packet_info: Packet information
        
        Returns:
            Selected next hop switch ID
        """
        # Get current metrics
        current_metrics = self.load_monitor.get_current_metrics()
        if not current_metrics:
            current_metrics = self.load_monitor.collect_metrics()
        
        # Predict future load
        predicted_load = 0.5  # Default
        if len(self.metrics_history) >= 60:
            try:
                predicted_load = self.load_predictor.predict_next_load(
                    self.metrics_history[-60:]
                )
            except Exception as e:
                logger.error(f"Error in load prediction: {e}")
        
        # Detect anomalies
        anomaly_score = 0.0
        is_anomaly = False
        if len(self.metrics_history) >= 10:
            try:
                features = self.anomaly_detector.extract_features(self.metrics_history)
                is_anomaly, anomaly_score = self.anomaly_detector.detect_anomaly(features)
            except Exception as e:
                logger.error(f"Error in anomaly detection: {e}")
        
        # Get neighbor states
        neighbors = self.switch_neighbors.get(current_switch, [])
        neighbor_states = []
        for neighbor_id in neighbors[:5]:  # Max 5 neighbors
            neighbor_metrics = self.switch_metrics.get(neighbor_id, {})
            neighbor_states.append({
                'load': neighbor_metrics.get('load', 0.0),
                'latency': 5.0,  # Default latency
                'anomaly_score': neighbor_metrics.get('anomaly_score', 0.0)
            })
        
        # Build state for RL agent
        state = self.rl_agent.build_state(
            current_metrics, predicted_load, neighbor_states, anomaly_score
        )
        
        # Get action from RL agent
        action = self.rl_agent.act(state, training=True)
        
        # Map action to neighbor (if available)
        if action < len(neighbors):
            selected_neighbor = neighbors[action]
        elif neighbors:
            selected_neighbor = neighbors[0]  # Fallback to first neighbor
        else:
            selected_neighbor = None
        
        logger.debug(f"AI routing decision: switch={current_switch}, "
                    f"predicted_load={predicted_load:.2f}, "
                    f"anomaly_score={anomaly_score:.2f}, "
                    f"next_hop={selected_neighbor}")
        
        return selected_neighbor
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """Handle packet-in events with AI routing"""
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
        
        # Use AI for routing decision
        packet_info = {
            'src': src,
            'dst': dst,
            'in_port': in_port
        }
        
        # Determine output port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            # Use AI routing
            next_hop = self.ai_route_decision(dpid, dst, packet_info)
            if next_hop:
                # Map next hop to port (simplified)
                out_port = 2  # Default port for next hop
            else:
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

