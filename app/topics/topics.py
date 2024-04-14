import random

# Define the possible content for the quiz here
TOPIC_TO_SUBTOPIC_MAP = {
    "Basics of Cloud Computing": [
        "Definitions",
        "Resource Pooling",
        "Cloud Economics",
        "IaaS",
        "PaaS",
        "SaaS",
        "Opportunities and Challenges",
        "Advantages and Disadvantages of Cloud Computing",
    ],
    "Datacenter Networking": [
        "History of Computer Networking and the Internet",
        "Basics of Networking",
        "Multiplexing",
        "Layering",
        "TCP/IP",
        "Routing",
        "TCP Congestion Control - AIMD",
        "Network Topologies",
        "Clos Network",
    ],
    "Virtualization": [
        "Definition",
        "History",
        "Hypervisor",
        "OS Overview",
        "Types of CPU Virtualization",
        "Full-virtualization",
        "Para-virtualization",
        "Hardware-assisted virtualization",
        "RAID",
        "Caching",
    ],
    "CPU Scheduling": [
        "Definition",
        "Motivation",
        "Types of CPU Scheduling",
        "Fairness",
        "Utilization",
        "Schedulability",
        "Work-Conserving",
        "Credit Scheduler",
        "Stride Scheduler",
    ],
    "Cloud Security CAPTCHA-ReCAPTCHA": [
        "Crowdsourcing",
        "Mechanical Turk",
        "CAPTCHA",
        "ReCAPTCHA",
        "Autograding",
    ],
    "Cloud Security Cryptography": [
        "Principles of Security",
        "Confidentiality",
        "Integrity",
        "Authentication",
        "Non-repudiation",
        "Caesar Cipher",
        "Substitution",
        "Transposition",
        "Cryptography Basics",
        "Encryption",
        "Decryption",
        "Symmetric Key Cryptography",
        "Diffie-Hellman Key Exchange",
        "Asymmetric Key Cryptography",
        "RSA",
        "RSA - Key Generation",
        "RSA - Encryption and Decryption",
        "Digital Signatures",
        "Public Key Infrastructure",
    ],
    "CAP Theorem": [
        "Eventual Consistency",
        "Tradeoffs",
        "Importance",
        "Consistent and Partition Tolerant Examples",
        "Available and Partition Tolerant Examples",
        "Types of Consistency",
    ],
    "Google's Problem and Pagerank": [
        "Challenges",
        "Links",
        "Web as a Graph",
        "Random Surfer Model",
        "Modified Model",
        "Deadend nodes",
        "Power Iteration",
        "Dangling Links",
        "Convergence Property",
        "Web Spamming",
        "Random Walkers",
        "Spider Traps",
        "Taxation",
        "Transition Matrix",
    ],
}


def get_topics():
    return list(TOPIC_TO_SUBTOPIC_MAP.keys())


def get_subtopic(topic):
    return random.choice(TOPIC_TO_SUBTOPIC_MAP[topic])
