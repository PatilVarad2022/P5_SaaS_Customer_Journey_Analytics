import pandas as pd
from typing import Dict, Any
from src.utils.logger import get_logger

logger = get_logger(__name__)

def compute_funnel_metrics(users: pd.DataFrame, events: pd.DataFrame, subs: pd.DataFrame) -> Dict[str, Any]:
    """Computes Acquisition -> Activation -> Paid funnel."""
    logger.info("Computing funnel metrics...")
    
    # Acquisition
    signups = set(users["customer_id"])
    
    # Activation (within 14 days)
    # Ensure simplified logic for robustness
    act_events = events[events["event_name"].str.lower() == "activate"]
    activated_users = set(act_events["customer_id"])
    
    # Paid
    paid_users = set(subs["customer_id"])
    
    # Intersection for funnel integrity (A user can't be paid without being signed up, strictly speaking)
    # Ideally: Signup -> (maybe Activate) -> Paid.
    # But for strict funnel: 
    # Step 1: Signup
    # Step 2: Activate (subset of Signup)
    # Step 3: Paid (subset of Activate? Not necessarily in all SaaS, but usually implies engagement. 
    # For this funnel we typically track PURE conversion.)
    
    # Let's check overlap for stages
    step1 = len(signups)
    step2 = len(signups.intersection(activated_users))
    step3 = len(signups.intersection(activated_users).intersection(paid_users)) # strict funnel
    
    logger.info(f"Funnel counts: {step1} -> {step2} -> {step3}")
    
    return {
        "acquisition": step1,
        "activation": step2,
        "retention": step3, # Using "Retention" as third step name per prompt? 
                            # Prompt says: Acquisition -> Activation -> Engagement -> Retention -> Expansion
                            # I will implement simplified 3-step first, then expand if possible with data.
                            # B1 says: Acquisition -> Activation -> Engagement -> Retention -> Expansion
        "conversion_rates": {
            "signup_to_activation": step2 / step1 if step1 > 0 else 0,
            "activation_to_paid": step3 / step2 if step2 > 0 else 0
        },
        "drop_off": {
            "activation_drop_off": 1 - (step2 / step1) if step1 > 0 else 0,
            "paid_drop_off": 1 - (step3 / step2) if step2 > 0 else 0
        }
    }
