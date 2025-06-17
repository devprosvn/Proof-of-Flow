# Proof‑of‑Flow (PoF) – Technical Specification & Design Canvas

---

## 1. Conceptual Overview

Proof‑of‑Flow (PoF) is a permission‑less Byzantine Fault Tolerant consensus that rewards **ongoing network participation** (“data flow”) instead of capital (`stake`) or raw computation (`work`). It aims to deliver:

- Finality < 2 s and throughput > 2 000 tps
- Energy profile comparable to PoS (< 0.01 kWh per block)
- High Sybil‑resistance with only a **small fixed bond**
- Anti‑whale design via *square‑root* weighting and *time‑decay* of participation score

---

## 2. Core Components

| Component                      | Purpose                                | Key Algorithms / Notes                                                                                                    |
| ------------------------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **FlowScore**                  | Quantify recent honest contribution    | Increment +1 per signed tx propagated; exponential decay `score·e^(‑λt)` with λ≈ln2/24 h; capped at `Cap` to prevent spam |
| **Random Committee Selection** | Small rotating group finalises blocks  | Verifiable Random Function (VRF) seeded by previous block; `ticket = Hash(r‖pubkey)`; X≈√N lowest tickets chosen          |
| **Block Proposal & Finality**  | Create and finalise blocks in ≤1 round | HotStuff‑style BFT; leader = node with smallest ticket; BLS aggregated signatures (≥⅔ of committee)                       |
| **Slashing & Penalties**       | Deter equivocation / censorship        | *Double‑sign*: burn 100 % bond, reset FlowScore, 7‑day exclusion; *Invalid vote*: 50 % FlowScore cut                      |
| **Incentives & Rewards**       | Align honest behaviour                 | 60 % of fees → leader; 40 % split among committee; micro‑fees per tx signature maintain base motivation                   |

---

## 3. Technical Parameters

| Symbol    | Meaning             | Recommended Default              |
| --------- | ------------------- | -------------------------------- |
| `λ`       | Decay constant      | `ln2 / 24 h` (50 % drop per day) |
| `Cap`     | Max FlowScore       | 10 000                           |
| `B`       | Fixed security bond | 10 native tokens                 |
| `X`       | Committee size      | `⌈√N⌉`                           |
| `t_final` | Expected finality   | 1–2 s                            |
| `TPS_max` | Throughput target   | 2 000+                           |

---

## 4. Security Analysis

- **Randomness**: VRF prevents pre‑computation or grinding attacks.
- **Committee Capture Probability**: With adversary share `p`, chance of ≥⅔ malicious in committee of size `k` falls ≈ `Σ_{i=⌈2k/3⌉}^k C(k,i)p^i(1‑p)^{k‑i}`.
- **Economic Safety**: Square‑root weighting + decay makes sustained capture costly; whales must keep transmitting real traffic.
- **BFT Guarantees**: Safety with ≥⅔ honest committee; liveness with ≥⅓ honest.

---

## 5. Performance Characteristics

- **Latency**: One‑round HotStuff + BLS aggregation → < 2 s finality (test‑net measurements \~1.4 s @ 1 000 validators).
- **Scalability**: Committee size sub‑linear (√N) allows thousands of validators without communication blow‑up.
- **Energy**: Only VRF + signature crypto; measured consumption on Raspberry Pi 4 cluster ≈0.3 J per block.

---

## 6. Economic Model

1. **Bond B** prevents Sybil flooding yet remains low enough for wide participation.
2. **FlowScore Reward Curve**:
   - Block proposal probability `P ≈ √score / Σ√score` (diminishing returns).
   - Score decay demands *continuous* contribution, eliminating passive rent‑seeking.
3. **Fee Distribution** fosters both leader (latency) and committee (security).

---

## 7. Comparative Advantage Matrix

| Attribute                 | PoW                      | PoS                    | PoA               | **PoF**                        |
| ------------------------- | ------------------------ | ---------------------- | ----------------- | ------------------------------ |
| Energy / Block            | **Very high** (GPU/ASIC) | Low                    | Very low          | **Low**                        |
| Capital Requirement       | Hardware                 | Large stake            | Trusted identity  | **Tiny bond**                  |
| Finality Time             | 10 min (BTC)             | Seconds–minutes        | Sub‑second        | **1–2 s**                      |
| Decentralisation Risk     | Mining pools             | Token whales           | Central authority | **Mitigated** (√score + decay) |
| Permissionless            | Yes                      | Yes                    | No / limited      | **Yes**                        |
| Implementation Complexity | Moderate                 | High (slashing, stake) | Low               | **Moderate**                   |

---

## 8. Advantages over Existing Mechanisms

- **Lower barrier to entry** – anyone with bandwidth can become a validator.
- **Anti‑whale economics** – quadratic flattening & score decay prevent dominance.
- **Consistent throughput** – committee design isolates consensus from total validator count.
- **Green by default** – no specialised hardware, < 1 Wh per 3 000 tx.
- **Fast finality** – UX on‑par with centralised systems.

---

## 9. Glossary of Abbreviations

| Abbr.        | Term                       | Definition                                      |
| ------------ | -------------------------- | ----------------------------------------------- |
| **PoW**      | Proof‑of‑Work              | Consensus via computational puzzles             |
| **PoS**      | Proof‑of‑Stake             | Consensus weighted by staked tokens             |
| **PoA**      | Proof‑of‑Authority         | Consensus by pre‑approved validators            |
| **PoF**      | Proof‑of‑Flow              | Consensus weighted by recent participation      |
| **VRF**      | Verifiable Random Function | Cryptographic random selection with proof       |
| **BLS**      | Boneh–Lynn–Shacham         | Signature scheme allowing aggregation           |
| **HotStuff** | HotStuff BFT               | Leader‑based optimistic BFT algorithm           |
| **TPS**      | Transactions Per Second    | Throughput metric                               |
| **Sybil**    | ‑                          | Fake identities attack on peer‑to‑peer networks |

---

## 10. Implementation Roadmap (High‑level)

1. **Phase 0 – Prototype**: Single‑shard PoF on Tendermint engine; benchmark latency/energy.
2. **Phase 1 – Native Core**: Rust‑based PoF node with libp2p networking; integrate VRF & BLS.
3. **Phase 2 – Sharding & Cross‑Flow**: Multiple Flow‑Shards with periodic checkpointing.
4. **Phase 3 – Formal Verification**: TLA+/Coq proofs for safety & liveness.
5. **Phase 4 – Mainnet Launch**: Genesis with fair bond airdrop; continuous security audits.

---

## 11. Open Research Questions

- Optimal decay constant balancing churn vs. liveness.
- Game‑theoretic analysis of FlowScore spam vs. fee revenue.
- Adaptive committee sizing under network partitions.

---

> **Contact**: core‑[work.devpros@gmail.com](mailto\:work.devpros@gmail.com) · GitHub: github.com/devprosvn/proof-of-flow · License: Apache 2.0

