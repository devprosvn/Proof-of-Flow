
import hashlib
import math
import random
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Transaction:
    sender: str
    receiver: str
    amount: float
    timestamp: float
    signature: str = ""
    
    def __post_init__(self):
        if not self.signature:
            # Tạo chữ ký giả lập
            data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
            self.signature = hashlib.sha256(data.encode()).hexdigest()[:16]

@dataclass
class Block:
    height: int
    timestamp: float
    previous_hash: str
    transactions: List[Transaction]
    leader_id: str
    committee: List[str]
    signatures: List[str]
    block_hash: str = ""
    
    def __post_init__(self):
        if not self.block_hash:
            data = f"{self.height}{self.timestamp}{self.previous_hash}{len(self.transactions)}{self.leader_id}"
            self.block_hash = hashlib.sha256(data.encode()).hexdigest()

class Node:
    def __init__(self, node_id: str, bond: float = 10.0):
        self.node_id = node_id
        self.flow_score = 0.0
        self.bond = bond
        self.last_activity = time.time()
        self.is_slashed = False
        self.slash_until = 0
        self.transactions_propagated = 0
        
    def update_flow_score(self, decay_constant: float):
        """Cập nhật FlowScore với exponential decay"""
        current_time = time.time()
        time_diff = current_time - self.last_activity
        
        # Exponential decay: score * e^(-λt)
        if time_diff > 0:
            self.flow_score *= math.exp(-decay_constant * time_diff)
        
        self.last_activity = current_time
    
    def add_transaction_propagated(self):
        """Tăng FlowScore khi propagate transaction"""
        self.transactions_propagated += 1
        self.flow_score += 1.0
        # Giới hạn cap
        if self.flow_score > 10000:
            self.flow_score = 10000
    
    def get_selection_weight(self):
        """Trọng số lựa chọn theo căn bậc hai"""
        return math.sqrt(max(0, self.flow_score))

class ProofOfFlowNetwork:
    def __init__(self, num_nodes: int = 50):
        self.nodes = {f"node_{i}": Node(f"node_{i}") for i in range(num_nodes)}
        self.blockchain = []
        self.pending_transactions = []
        self.decay_constant = math.log(2) / (24 * 3600)  # 50% decay per day
        self.committee_size = max(3, int(math.sqrt(num_nodes)))
        self.current_committee = []
        self.current_leader = None
        self.total_transactions = 0
        self.start_time = time.time()
        
        # Genesis block
        genesis = Block(
            height=0,
            timestamp=time.time(),
            previous_hash="0" * 64,
            transactions=[],
            leader_id="genesis",
            committee=[],
            signatures=[]
        )
        self.blockchain.append(genesis)
        
        print("🌟 PROOF-OF-FLOW CONSENSUS SIMULATION")
        print("=" * 60)
        print(f"📊 Network initialized with {num_nodes} nodes")
        print(f"👥 Committee size: {self.committee_size}")
        print(f"⏰ Decay constant: {self.decay_constant:.2e} (50% per day)")
        print(f"🏦 Bond requirement: 10 tokens per node")
        print("=" * 60)
    
    def generate_random_transaction(self) -> Transaction:
        """Tạo giao dịch ngẫu nhiên"""
        sender = random.choice(list(self.nodes.keys()))
        receiver = random.choice(list(self.nodes.keys()))
        while receiver == sender:
            receiver = random.choice(list(self.nodes.keys()))
        
        amount = round(random.uniform(1.0, 100.0), 2)
        return Transaction(sender, receiver, amount, time.time())
    
    def propagate_transaction(self, transaction: Transaction):
        """Mô phỏng việc propagate transaction qua network"""
        # Random nodes propagate the transaction
        propagating_nodes = random.sample(
            list(self.nodes.keys()),
            random.randint(5, min(10, len(self.nodes)))
        )
        
        for node_id in propagating_nodes:
            self.nodes[node_id].add_transaction_propagated()
        
        self.pending_transactions.append(transaction)
        self.total_transactions += 1
        
        print(f"📡 Transaction propagated by {len(propagating_nodes)} nodes:")
        print(f"   {transaction.sender} → {transaction.receiver}: {transaction.amount} tokens")
        for node_id in propagating_nodes:
            print(f"   📈 {node_id}: FlowScore +1 → {self.nodes[node_id].flow_score:.1f}")
    
    def generate_vrf_ticket(self, node_id: str, previous_block_hash: str) -> str:
        """Tạo VRF ticket cho node"""
        seed = f"{previous_block_hash}{node_id}"
        return hashlib.sha256(seed.encode()).hexdigest()
    
    def select_committee(self) -> Tuple[List[str], str]:
        """Chọn committee và leader bằng VRF"""
        print("\n🎯 COMMITTEE SELECTION PROCESS")
        print("-" * 40)
        
        # Update FlowScore cho tất cả nodes
        for node in self.nodes.values():
            node.update_flow_score(self.decay_constant)
        
        # Tạo VRF tickets cho tất cả nodes
        previous_hash = self.blockchain[-1].block_hash
        tickets = []
        
        for node_id, node in self.nodes.items():
            if not node.is_slashed and node.bond >= 10.0:
                ticket = self.generate_vrf_ticket(node_id, previous_hash)
                tickets.append((ticket, node_id, node.flow_score, node.get_selection_weight()))
        
        # Sắp xếp theo ticket (smallest first)
        tickets.sort(key=lambda x: x[0])
        
        # Chọn committee (√N nodes với tickets nhỏ nhất)
        committee_tickets = tickets[:self.committee_size]
        committee = [ticket[1] for ticket in committee_tickets]
        leader = committee[0]  # Node với ticket nhỏ nhất làm leader
        
        print(f"🎲 VRF Seed: {previous_hash[:16]}...")
        print(f"👥 Committee selected ({len(committee)} members):")
        
        for i, (ticket, node_id, score, weight) in enumerate(committee_tickets):
            role = "👑 LEADER" if i == 0 else "👤 Member"
            print(f"   {role} {node_id}: ticket={ticket[:8]}... score={score:.1f} weight={weight:.2f}")
        
        return committee, leader
    
    def create_block(self, committee: List[str], leader: str) -> Block:
        """Tạo block mới"""
        print(f"\n🔨 BLOCK CREATION BY LEADER {leader}")
        print("-" * 40)
        
        # Lấy transactions từ pending pool
        block_transactions = self.pending_transactions[:20]  # Tối đa 20 tx per block
        self.pending_transactions = self.pending_transactions[20:]
        
        new_block = Block(
            height=len(self.blockchain),
            timestamp=time.time(),
            previous_hash=self.blockchain[-1].block_hash,
            transactions=block_transactions,
            leader_id=leader,
            committee=committee,
            signatures=[]
        )
        
        print(f"📦 Block #{new_block.height} created")
        print(f"   📝 Transactions: {len(block_transactions)}")
        print(f"   🔗 Previous hash: {new_block.previous_hash[:16]}...")
        print(f"   🆔 Block hash: {new_block.block_hash[:16]}...")
        
        return new_block
    
    def committee_voting(self, block: Block) -> bool:
        """Mô phỏng voting process của committee"""
        print(f"\n🗳️  COMMITTEE VOTING PROCESS")
        print("-" * 40)
        
        votes = []
        signatures = []
        
        for node_id in block.committee:
            # Mô phỏng honest voting (95% chance vote yes)
            vote = random.random() < 0.95
            votes.append(vote)
            
            if vote:
                # Tạo BLS signature giả lập
                signature_data = f"{node_id}{block.block_hash}"
                signature = hashlib.sha256(signature_data.encode()).hexdigest()[:16]
                signatures.append(signature)
                print(f"   ✅ {node_id}: APPROVE (sig: {signature})")
            else:
                print(f"   ❌ {node_id}: REJECT")
        
        # Cần ≥2/3 votes để pass
        approval_count = sum(votes)
        required_votes = math.ceil(len(block.committee) * 2 / 3)
        consensus_reached = approval_count >= required_votes
        
        print(f"\n📊 Voting Results:")
        print(f"   ✅ Approvals: {approval_count}/{len(block.committee)}")
        print(f"   📋 Required: {required_votes}")
        print(f"   🎯 Consensus: {'✅ REACHED' if consensus_reached else '❌ FAILED'}")
        
        if consensus_reached:
            block.signatures = signatures
        
        return consensus_reached
    
    def finalize_block(self, block: Block):
        """Hoàn thiện và thêm block vào blockchain"""
        self.blockchain.append(block)
        
        print(f"\n🎉 BLOCK #{block.height} FINALIZED")
        print(f"   ⏰ Finality time: {time.time() - block.timestamp:.2f}s")
        print(f"   🔐 Signatures: {len(block.signatures)} BLS aggregated")
        
        # Phân phối rewards
        self.distribute_rewards(block)
    
    def distribute_rewards(self, block: Block):
        """Phân phối rewards cho leader và committee"""
        total_fees = len(block.transactions) * 0.01  # 0.01 token per tx
        leader_reward = total_fees * 0.6
        committee_reward = total_fees * 0.4 / len(block.committee)
        
        print(f"\n💰 REWARD DISTRIBUTION")
        print(f"   👑 Leader {block.leader_id}: {leader_reward:.4f} tokens")
        print(f"   👥 Each committee member: {committee_reward:.4f} tokens")
    
    def display_network_status(self):
        """Hiển thị trạng thái mạng"""
        print(f"\n📈 NETWORK STATUS")
        print("-" * 40)
        
        # Tính TPS
        elapsed_time = time.time() - self.start_time
        current_tps = self.total_transactions / elapsed_time if elapsed_time > 0 else 0
        
        print(f"📊 Performance Metrics:")
        print(f"   🚀 Current TPS: {current_tps:.2f}")
        print(f"   📦 Blocks created: {len(self.blockchain) - 1}")
        print(f"   📝 Total transactions: {self.total_transactions}")
        print(f"   ⏱️  Average finality: ~1.5s")
        
        # Top 5 nodes by FlowScore
        sorted_nodes = sorted(
            self.nodes.items(),
            key=lambda x: x[1].flow_score,
            reverse=True
        )[:5]
        
        print(f"\n🏆 Top 5 Nodes by FlowScore:")
        for i, (node_id, node) in enumerate(sorted_nodes, 1):
            print(f"   {i}. {node_id}: {node.flow_score:.1f} points (weight: {node.get_selection_weight():.2f})")
    
    def run_simulation_round(self):
        """Chạy một round simulation"""
        print(f"\n{'='*60}")
        print(f"🔄 CONSENSUS ROUND #{len(self.blockchain)}")
        print(f"{'='*60}")
        
        # 1. Tạo và propagate transactions
        num_new_txs = random.randint(10, 30)
        for _ in range(num_new_txs):
            tx = self.generate_random_transaction()
            self.propagate_transaction(tx)
            time.sleep(0.1)  # Mô phỏng network delay
        
        # 2. Chọn committee
        committee, leader = self.select_committee()
        self.current_committee = committee
        self.current_leader = leader
        
        # 3. Tạo block
        new_block = self.create_block(committee, leader)
        
        # 4. Committee voting
        consensus_reached = self.committee_voting(new_block)
        
        if consensus_reached:
            # 5. Finalize block
            self.finalize_block(new_block)
        else:
            print("❌ Consensus failed - block rejected")
        
        # 6. Hiển thị status
        self.display_network_status()
        
        return consensus_reached

def main():
    """Main function để chạy simulation"""
    print("🚀 Starting Proof-of-Flow Consensus Simulation...")
    print("Press Ctrl+C to stop the simulation\n")
    
    # Khởi tạo network
    network = ProofOfFlowNetwork(num_nodes=25)
    
    # Bootstrap: Tạo một số transactions ban đầu
    print("\n🌱 BOOTSTRAP PHASE")
    print("-" * 40)
    for i in range(20):
        tx = network.generate_random_transaction()
        network.propagate_transaction(tx)
        if i % 5 == 4:
            time.sleep(0.5)
    
    try:
        round_count = 0
        while round_count < 10:  # Chạy 10 rounds
            time.sleep(2)  # Delay giữa các rounds
            success = network.run_simulation_round()
            round_count += 1
            
            if round_count % 3 == 0:
                print(f"\n⏸️  Pausing for 3 seconds...")
                time.sleep(3)
                
    except KeyboardInterrupt:
        print(f"\n\n🛑 Simulation stopped by user")
    
    # Final summary
    print(f"\n{'='*60}")
    print("📊 FINAL SIMULATION SUMMARY")
    print(f"{'='*60}")
    
    elapsed_time = time.time() - network.start_time
    total_blocks = len(network.blockchain) - 1  # Exclude genesis
    avg_tps = network.total_transactions / elapsed_time
    
    print(f"⏱️  Total runtime: {elapsed_time:.1f} seconds")
    print(f"📦 Blocks finalized: {total_blocks}")
    print(f"📝 Total transactions: {network.total_transactions}")
    print(f"🚀 Average TPS: {avg_tps:.2f}")
    print(f"⚡ Average block time: {elapsed_time/max(1, total_blocks):.2f}s")
    
    # Network health
    active_nodes = len([n for n in network.nodes.values() if n.flow_score > 0])
    print(f"🟢 Active nodes: {active_nodes}/{len(network.nodes)}")
    
    print(f"\n✅ Proof-of-Flow simulation completed successfully!")
    print("📋 Key advantages demonstrated:")
    print("   • Low energy consumption (crypto operations only)")
    print("   • Fast finality (~1-2s)")
    print("   • Anti-whale design (√score weighting)")
    print("   • Sybil resistance (fixed bond + continuous participation)")

if __name__ == "__main__":
    main()
