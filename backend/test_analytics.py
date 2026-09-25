import asyncio
import json

from app.services.analytics import get_engagement_dashboard
from app.core.config import get_settings

def test():
    print("Fetching settings to confirm env loaded...")
    s = get_settings()
    print("Supabase URL:", s.supabase_url)
    
    print("\nRunning get_engagement_dashboard()...")
    dashboard = get_engagement_dashboard()
    print("\n--- Analytics Dashboard Results ---")
    print(f"Total Users: {dashboard['total_users']}")
    print(f"At-Risk Count: {dashboard['at_risk_count']}")
    print(f"Avg Risk Score: {dashboard['avg_risk_score']}")
    print(f"CV Metrics: {dashboard['cv_metrics']}")
    
    print("\nTop 3 Users (sorted by risk_score desc):")
    for u in dashboard["users"][:3]:
        print(f"\nUser ID: {u['user_id']}")
        print(f"Risk Score: {u['risk_score']} ({u['risk_label']})")
        print("Top SHAP Explanations:")
        for shap_expl in u["shap_explanations"]:
            print(f"  - {shap_expl['feature_name']}: val={shap_expl['feature_value']}, shap={shap_expl['shap_value']}")

if __name__ == "__main__":
    test()
