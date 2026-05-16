import fitz

POLICIES = {
    "sample_access_control_policy.pdf": """\
ACME CORPORATION - ACCESS CONTROL POLICY
Version 3.0 | Effective Date: March 1, 2025

SECTION 1: PURPOSE AND SCOPE
This policy defines requirements for controlling access to ACME Corporation systems,
applications, and data. It applies to all employees, contractors, and third parties
who access corporate resources.

SECTION 2: PRINCIPLE OF LEAST PRIVILEGE
All access rights must be granted on a need-to-know and least-privilege basis.
Users must only be granted the minimum access necessary to perform their job duties.
Privileged access (admin rights) must be approved by the employee's manager and the
IT Security team before being provisioned.

SECTION 3: ACCESS REQUEST AND PROVISIONING
Access to systems must be requested via the IT Service Portal using the Access Request
Form (ARF-001). Requests must be approved by the data owner and the employee's direct
manager. Access must be provisioned within 3 business days of approval. All access
grants must be documented in the Identity and Access Management (IAM) system.

SECTION 4: MULTI-FACTOR AUTHENTICATION
Multi-factor authentication (MFA) is mandatory for all remote access to corporate
systems, all cloud-based applications, and all privileged accounts. Acceptable MFA
methods include TOTP authenticator apps (Google Authenticator, Microsoft Authenticator)
and hardware security keys (FIDO2/WebAuthn). SMS-based MFA is not permitted for
privileged accounts due to SIM-swapping risks.

SECTION 5: ACCESS REVIEWS
Access rights for all users must be reviewed every 90 days by the relevant data owner.
Privileged access must be reviewed every 30 days. Any access that is no longer required
must be revoked within 5 business days of the review decision. Results of access reviews
must be logged and retained for 3 years.

SECTION 6: ACCOUNT TERMINATION
Upon employee termination, all system access must be revoked within 4 hours of HR
notification. For involuntary terminations, access must be revoked immediately at the
time of the termination meeting. Shared credentials known to the terminated employee
must be rotated within 24 hours. IT must confirm revocation in writing to HR and
the employee's manager.

SECTION 7: THIRD-PARTY ACCESS
Third-party vendors requiring access to corporate systems must sign a Data Processing
Agreement (DPA) before access is granted. Third-party access must be time-limited,
not exceeding 90 days, and must be renewed explicitly. All third-party sessions must
be logged and monitored in real time via the Privileged Access Management (PAM) tool.

SECTION 8: COMPLIANCE AND ENFORCEMENT
Violations of this policy may result in disciplinary action up to and including
termination of employment or contract. Access control compliance is audited monthly
by the Information Security team and reported to the CISO quarterly.
""",
    "sample_incident_response_policy.pdf": """\
ACME CORPORATION - INCIDENT RESPONSE POLICY
Version 1.4 | Effective Date: February 15, 2025

SECTION 1: PURPOSE AND SCOPE
This policy establishes the framework for detecting, reporting, and responding to
security incidents at ACME Corporation. It applies to all employees, contractors,
and managed service providers operating on behalf of ACME.

SECTION 2: INCIDENT CLASSIFICATION
Incidents are classified into four severity levels:
- P1 (Critical): Active breach, ransomware, or data exfiltration in progress.
  Response required within 15 minutes. CISO and executive team must be notified.
- P2 (High): Confirmed compromise of a system or account with potential data exposure.
  Response required within 1 hour. IT Security manager must be notified.
- P3 (Medium): Suspicious activity detected but not yet confirmed as a breach.
  Response required within 4 hours. Security analyst on call must be notified.
- P4 (Low): Policy violation or anomalous activity with no immediate threat.
  Response required within 24 hours. Standard ticket workflow applies.

SECTION 3: REPORTING REQUIREMENTS
All suspected security incidents must be reported immediately to the Security Operations
Center (SOC) by emailing security@acme.com or calling the 24/7 hotline at ext. 9911.
Employees must not attempt to investigate or remediate incidents themselves. Delaying
the reporting of a known incident is a policy violation and may result in disciplinary
action.

SECTION 4: INCIDENT RESPONSE PHASES
Phase 1 - Identification: Confirm and classify the incident. Assign an Incident Commander.
Phase 2 - Containment: Isolate affected systems to prevent further spread. Preserve
  forensic evidence before any remediation. Short-term containment must begin within
  30 minutes of P1 confirmation.
Phase 3 - Eradication: Remove the root cause (malware, compromised credentials, etc.).
  All affected systems must be rebuilt from known-good images, not patched in place.
Phase 4 - Recovery: Restore services from clean backups. Monitor restored systems
  intensively for 72 hours post-recovery.
Phase 5 - Post-Incident Review: A written post-mortem must be completed within 5 business
  days of incident closure. Root cause, timeline, and corrective actions must be documented.

SECTION 5: EVIDENCE PRESERVATION
Forensic images of affected systems must be taken before any remediation activity.
Logs must be exported and preserved in write-once storage (AWS S3 with Object Lock).
Chain of custody documentation must be maintained for all evidence. Evidence must be
retained for a minimum of 3 years or the duration of any legal proceedings, whichever
is longer.

SECTION 6: REGULATORY NOTIFICATION
If a data breach involves personal data of EU residents, the relevant supervisory authority
must be notified within 72 hours of discovery under GDPR Article 33. If a breach affects
customers, affected individuals must be notified within 30 days in accordance with
applicable state breach notification laws. The Legal and Compliance team must be engaged
immediately for any P1 or P2 incident.

SECTION 7: TESTING AND TRAINING
The incident response plan must be tested at least annually via a tabletop exercise.
A full red team simulation must be conducted every 2 years. All employees must complete
incident response awareness training annually. The SOC team must complete hands-on
incident response training every 6 months.

SECTION 8: POLICY MAINTENANCE
This policy must be reviewed and updated at least annually or following any major incident.
The CISO is responsible for approving all updates to this policy.
""",
}


def create_pdf(filename: str, content: str) -> None:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4

    x, y = 50, 50
    line_height = 14
    max_width = 495

    for line in content.splitlines():
        words = line.split()
        if not words:
            y += line_height
            if y > 800:
                page = doc.new_page(width=595, height=842)
                y = 50
            continue

        current_line = ""
        for word in words:
            test = (current_line + " " + word).strip()
            if fitz.get_text_length(test, fontsize=10) <= max_width:
                current_line = test
            else:
                page.insert_text((x, y), current_line, fontsize=10)
                y += line_height
                if y > 800:
                    page = doc.new_page(width=595, height=842)
                    y = 50
                current_line = word

        if current_line:
            page.insert_text((x, y), current_line, fontsize=10)
            y += line_height
            if y > 800:
                page = doc.new_page(width=595, height=842)
                y = 50

    doc.save(filename)
    print(f"Created {filename} ({doc.page_count} page(s))")
    doc.close()


for fname, content in POLICIES.items():
    create_pdf(fname, content)
