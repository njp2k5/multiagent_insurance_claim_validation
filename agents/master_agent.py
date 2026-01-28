import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from state import ClaimState


def master_decision_agent(state: ClaimState) -> ClaimState:
    results = state["agent_results"]
    avg_conf = sum(r["confidence"] for r in results) / len(results)

    if any(r["status"] == "FAIL" for r in results):
        decision = "REJECTED"
    elif any(r["status"] == "FLAG" for r in results) or avg_conf < 0.7:
        decision = "HUMAN_REVIEW"
    else:
        decision = "APPROVED"

    state["final_decision"] = decision
    state["final_confidence"] = round(avg_conf, 2)
    return state


def get_agent_summary(state: ClaimState) -> Dict[str, Any]:
    """Extract and summarize information from all agents."""
    summary = {
        "claim_id": state.get("claim_id", "N/A"),
        "final_decision": state.get("final_decision", "PENDING"),
        "final_confidence": state.get("final_confidence", 0.0),
        "identity": None,
        "policy": None,
        "document": None,
        "fraud": None,
        "cross_validation": None
    }
    
    # Identity Agent Summary
    identity_result = state.get("identity_result")
    if identity_result:
        summary["identity"] = {
            "status": identity_result.get("status", "N/A"),
            "confidence": identity_result.get("confidence", 0.0),
            "message": identity_result.get("message", ""),
            "aadhaar_name": state.get("aadhaar_name"),
            "aadhaar_number": state.get("aadhaar_number"),
            "aadhaar_age": state.get("aadhaar_age")
        }
    
    # Policy Agent Summary
    policy_result = state.get("policy_result")
    if policy_result:
        metadata = policy_result.get("metadata", {})
        summary["policy"] = {
            "status": policy_result.get("status", "N/A"),
            "confidence": policy_result.get("confidence", 0.0),
            "message": policy_result.get("message", ""),
            "plan": metadata.get("current_plan"),
            "event": metadata.get("event"),
            "amount_claimed": metadata.get("amount_claimed")
        }
    
    # Document Agent Summary
    document_result = state.get("document_result")
    if document_result:
        summary["document"] = {
            "status": document_result.get("status", "N/A"),
            "confidence": document_result.get("confidence", 0.0),
            "message": document_result.get("message", ""),
            "summary": state.get("document_summary", ""),
            "extracted_name": state.get("document_name"),
            "extracted_age": state.get("document_age")
        }
    
    # Fraud Agent / Cross-validation Summary
    cross_validation = state.get("cross_validation_result")
    if cross_validation:
        summary["cross_validation"] = {
            "status": cross_validation.get("status", "N/A"),
            "name_match": cross_validation.get("name_match", False),
            "age_match": cross_validation.get("age_match", False),
            "confidence": cross_validation.get("confidence", 0.0),
            "message": cross_validation.get("message", ""),
            "inconsistencies": cross_validation.get("inconsistencies", [])
        }
    
    # Fraud result from agent_results
    for result in state.get("agent_results", []):
        if result.get("agent_name") == "FraudDetectionAgent":
            summary["fraud"] = {
                "status": result.get("status", "N/A"),
                "confidence": result.get("confidence", 0.0),
                "message": result.get("message", "")
            }
            break
    
    return summary


def draft_claim_email(user_email: str, summary: Dict[str, Any]) -> str:
    """Draft a customized email based on agent summaries."""
    
    decision = summary.get("final_decision", "PENDING")
    confidence = summary.get("final_confidence", 0.0)
    claim_id = summary.get("claim_id", "N/A")
    
    # Determine greeting and tone based on decision
    if decision == "APPROVED":
        subject_status = "Approved"
        opening = "Great news! Your insurance claim has been approved."
        decision_color = "#28a745"
    elif decision == "REJECTED":
        subject_status = "Rejected"
        opening = "We regret to inform you that your insurance claim has been rejected."
        decision_color = "#dc3545"
    else:
        subject_status = "Under Review"
        opening = "Your insurance claim requires additional review by our team."
        decision_color = "#ffc107"
    
    # Build HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #003366; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .decision-box {{ background-color: {decision_color}; color: white; padding: 15px; text-align: center; margin: 20px 0; border-radius: 5px; }}
            .section {{ margin: 20px 0; padding: 15px; background-color: white; border-radius: 5px; border-left: 4px solid #003366; }}
            .section h3 {{ color: #003366; margin-top: 0; }}
            .status-pass {{ color: #28a745; font-weight: bold; }}
            .status-fail {{ color: #dc3545; font-weight: bold; }}
            .status-info {{ color: #17a2b8; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            td:first-child {{ font-weight: bold; width: 40%; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Allianz Insurance</h1>
                <p>Claim Status Notification</p>
            </div>
            
            <div class="content">
                <p>Dear Valued Customer,</p>
                <p>{opening}</p>
                
                <div class="decision-box">
                    <h2>Claim {subject_status}</h2>
                    <p>Claim ID: {claim_id}</p>
                    <p>Confidence Score: {confidence:.0%}</p>
                </div>
    """
    
    # Identity Verification Section
    identity = summary.get("identity")
    if identity:
        status_class = "status-pass" if identity["status"] == "PASS" else "status-fail"
        html_content += f"""
                <div class="section">
                    <h3>🪪 Identity Verification</h3>
                    <table>
                        <tr><td>Status:</td><td class="{status_class}">{identity['status']}</td></tr>
                        <tr><td>Confidence:</td><td>{identity['confidence']:.0%}</td></tr>
                        <tr><td>Name:</td><td>{identity.get('aadhaar_name') or 'N/A'}</td></tr>
                        <tr><td>Message:</td><td>{identity['message']}</td></tr>
                    </table>
                </div>
        """
    
    # Policy Verification Section
    policy = summary.get("policy")
    if policy:
        status_class = "status-pass" if policy["status"] == "PASS" else "status-fail"
        html_content += f"""
                <div class="section">
                    <h3>📋 Policy Verification</h3>
                    <table>
                        <tr><td>Status:</td><td class="{status_class}">{policy['status']}</td></tr>
                        <tr><td>Confidence:</td><td>{policy['confidence']:.0%}</td></tr>
                        <tr><td>Policy Plan:</td><td>{policy.get('plan') or 'N/A'}</td></tr>
                        <tr><td>Claim Event:</td><td>{policy.get('event') or 'N/A'}</td></tr>
                        <tr><td>Amount Claimed:</td><td>₹{policy.get('amount_claimed') or 'N/A'}</td></tr>
                        <tr><td>Message:</td><td>{policy['message']}</td></tr>
                    </table>
                </div>
        """
    
    # Document Verification Section
    document = summary.get("document")
    if document:
        status_class = "status-pass" if document["status"] == "PASS" else "status-info"
        doc_summary = document.get('summary') or 'N/A'
        if len(doc_summary) > 200:
            doc_summary = doc_summary[:200] + "..."
        html_content += f"""
                <div class="section">
                    <h3>📄 Document Analysis</h3>
                    <table>
                        <tr><td>Status:</td><td class="{status_class}">{document['status']}</td></tr>
                        <tr><td>Confidence:</td><td>{document['confidence']:.0%}</td></tr>
                        <tr><td>Extracted Name:</td><td>{document.get('extracted_name') or 'N/A'}</td></tr>
                        <tr><td>Summary:</td><td>{doc_summary}</td></tr>
                    </table>
                </div>
        """
    
    # Cross-Validation Section
    cross_val = summary.get("cross_validation")
    if cross_val:
        status_class = "status-pass" if cross_val["status"] == "VERIFIED" else "status-fail"
        html_content += f"""
                <div class="section">
                    <h3>🔍 Cross-Validation</h3>
                    <table>
                        <tr><td>Status:</td><td class="{status_class}">{cross_val['status']}</td></tr>
                        <tr><td>Name Match:</td><td>{'✓ Yes' if cross_val['name_match'] else '✗ No'}</td></tr>
                        <tr><td>Age Match:</td><td>{'✓ Yes' if cross_val['age_match'] else '✗ No'}</td></tr>
                        <tr><td>Message:</td><td>{cross_val['message']}</td></tr>
                    </table>
                </div>
        """
    
    # Fraud Detection Section
    fraud = summary.get("fraud")
    if fraud:
        status_class = "status-pass" if fraud["status"] == "PASS" else "status-fail"
        html_content += f"""
                <div class="section">
                    <h3>🛡️ Fraud Analysis</h3>
                    <table>
                        <tr><td>Status:</td><td class="{status_class}">{fraud['status']}</td></tr>
                        <tr><td>Confidence:</td><td>{fraud['confidence']:.0%}</td></tr>
                        <tr><td>Message:</td><td>{fraud['message']}</td></tr>
                    </table>
                </div>
        """
    
    # Closing section
    if decision == "APPROVED":
        next_steps = "Your claim amount will be processed within 5-7 business days. You will receive a separate notification once the payment has been initiated."
    elif decision == "REJECTED":
        next_steps = "If you believe this decision was made in error, please contact our support team with additional documentation. You may also file an appeal within 30 days."
    else:
        next_steps = "A claims officer will review your case and contact you within 2-3 business days. Please keep your documents ready for any additional verification."
    
    html_content += f"""
                <div class="section">
                    <h3>📌 Next Steps</h3>
                    <p>{next_steps}</p>
                </div>
                
                <p>If you have any questions, please don't hesitate to contact our customer support.</p>
                <p>Thank you for choosing Allianz Insurance.</p>
            </div>
            
            <div class="footer">
                <p>This is an automated message from Allianz Insurance Claim System.</p>
                <p>© 2026 Allianz Insurance. All rights reserved.</p>
                <p>Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content


def send_claim_email(
    recipient_email: str,
    summary: Dict[str, Any]
) -> Dict[str, Any]:
    """Send the claim status email via SMTP."""
    
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_password:
        return {
            "success": False,
            "error": "SMTP credentials not configured. Please set SMTP_EMAIL and SMTP_PASSWORD in .env"
        }
    
    decision = summary.get("final_decision", "PENDING")
    claim_id = summary.get("claim_id", "N/A")
    
    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Allianz Insurance - Claim {claim_id} Status: {decision}"
    msg["From"] = smtp_email
    msg["To"] = recipient_email
    
    # Generate HTML content
    html_content = draft_claim_email(recipient_email, summary)
    
    # Create plain text version
    plain_text = f"""
    Allianz Insurance - Claim Status Notification
    
    Claim ID: {claim_id}
    Decision: {decision}
    Confidence: {summary.get('final_confidence', 0.0):.0%}
    
    Please view this email in an HTML-compatible email client for the full report.
    
    Thank you for choosing Allianz Insurance.
    """
    
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, recipient_email, msg.as_string())
        
        return {
            "success": True,
            "message": f"Email sent successfully to {recipient_email}",
            "claim_id": claim_id,
            "decision": decision
        }
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "SMTP authentication failed. Please check your email credentials."
        }
    except smtplib.SMTPException as e:
        return {
            "success": False,
            "error": f"SMTP error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to send email: {str(e)}"
        }


def master_agent_send_report(
    user_email: str,
    state: ClaimState
) -> Dict[str, Any]:
    """
    Master agent function that:
    1. Combines input from all agents
    2. Makes final decision
    3. Drafts and sends customized email to user
    """
    # First, run the decision agent to finalize the claim
    if not state.get("final_decision"):
        state = master_decision_agent(state)
    
    # Get comprehensive summary from all agents
    summary = get_agent_summary(state)
    
    # Send the email
    result = send_claim_email(user_email, summary)
    
    # Update state
    state["email_sent"] = result.get("success", False)
    
    return {
        "state": state,
        "email_result": result,
        "summary": summary
    }
