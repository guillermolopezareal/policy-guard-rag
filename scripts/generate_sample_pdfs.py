import fitz
import os

OUTPUT_DIR = "samples"
os.makedirs(OUTPUT_DIR, exist_ok=True)

POLICIES = {
    "sample_business_continuity_policy.pdf": """\
ACME CORPORATION - BUSINESS CONTINUITY AND DISASTER RECOVERY POLICY
Version 2.0 | Effective Date: January 1, 2026 | Owner: Chief Technology Officer

SECTION 1: PURPOSE AND SCOPE
This policy establishes the requirements for ensuring that ACME Corporation can
maintain or rapidly resume critical business operations following a disruptive event.
It applies to all business units, IT systems, and third-party service providers that
support critical ACME operations. Disruptive events covered include natural disasters,
cyberattacks, infrastructure failures, pandemics, and supply chain disruptions.

SECTION 2: RECOVERY OBJECTIVES
Each critical system and business process must have a defined Recovery Time Objective
(RTO) and Recovery Point Objective (RPO) approved by the system owner and the CTO.

Tier 1 systems (mission-critical: payment processing, authentication, core APIs):
RTO must not exceed 1 hour. RPO must not exceed 15 minutes. Tier 1 systems must
use active-active or active-passive redundancy with automated failover.

Tier 2 systems (business-critical: CRM, HR systems, internal communication tools):
RTO must not exceed 4 hours. RPO must not exceed 1 hour. Tier 2 systems must
replicate to a secondary region with a tested failover procedure.

Tier 3 systems (important but non-critical: reporting dashboards, development tools):
RTO must not exceed 24 hours. RPO must not exceed 4 hours. Tier 3 systems may
use daily backups with manual restoration procedures.

SECTION 3: BACKUP REQUIREMENTS
All production data must be backed up daily at minimum. Tier 1 system data must be
replicated continuously to a geographically separate data center or cloud region.
Backups must be encrypted at rest using AES-256 and in transit using TLS 1.2 or
higher. Backup encryption keys must be stored separately from the backup data and
must not be accessible from the primary environment in the event of a ransomware attack.

Backup restoration must be tested at least quarterly for Tier 1 systems, semi-annually
for Tier 2 systems, and annually for Tier 3 systems. Restoration test results, including
the time taken to restore and any errors encountered, must be documented and retained
for 3 years. Failed restoration tests must be escalated to the CTO within 24 hours
and remediated before the next scheduled production backup cycle.

All backups must be retained according to the following schedule: daily backups for
30 days, weekly backups for 12 months, monthly backups for 7 years. Backups subject
to a legal hold must not be deleted regardless of retention schedule.

SECTION 4: BUSINESS CONTINUITY PLANS
Each department head is responsible for maintaining a Business Continuity Plan (BCP)
for their department. BCPs must be reviewed and updated annually or following any
significant change to business operations or critical systems. BCPs must identify:
critical processes that must be maintained during a disruption; manual workarounds
for automated processes; key personnel and alternates for each critical role; contact
information for critical vendors and customers; and escalation procedures.

The minimum staffing required to maintain critical operations during a disruption is
defined as the Minimum Business Continuity Objective (MBCO). Department heads must
identify which roles constitute the MBCO and ensure cross-training so that no single
person is the sole owner of a critical process.

SECTION 5: DISASTER RECOVERY PROCEDURES
Upon declaration of a disaster or major business disruption, the Crisis Management Team
(CMT) is activated. The CMT is chaired by the CEO and includes the CTO, CISO, CFO,
Head of Legal, and Head of Communications. The CMT has authority to invoke the Disaster
Recovery Plan, authorize emergency expenditure, and communicate with regulators.

The Incident Commander (appointed by the CISO for cyber incidents, or the CTO for
infrastructure incidents) coordinates technical recovery activities and provides status
updates to the CMT every 30 minutes during an active disaster.

Failover to the disaster recovery environment must be authorized by the CTO or a
designated alternate. Failback to the primary environment requires a stability period
of at least 4 hours after the root cause has been resolved and a sign-off from both
the CTO and the system owner.

SECTION 6: TESTING AND EXERCISES
A full Business Continuity and Disaster Recovery tabletop exercise must be conducted
annually, involving the CMT and all department heads. At least one live failover test
for all Tier 1 systems must be conducted annually in a pre-announced maintenance window.
A surprise or unannounced DR test must be conducted for at least one critical system
each year. All tests must produce a written after-action report with findings and
remediation timelines. Critical findings must be remediated within 30 days.

SECTION 7: VENDOR AND THIRD-PARTY DEPENDENCIES
All third-party vendors classified as critical (those whose unavailability would trigger
an RTO breach for any Tier 1 or Tier 2 system) must provide evidence of their own
business continuity and disaster recovery capabilities annually. Evidence may include
SOC 2 Type II reports, independent audit results, or the vendor's own BCP documentation.
Contracts with critical vendors must include SLAs aligned with ACME's RTO and RPO
requirements and must specify the vendor's notification obligations in the event of
a service disruption.

SECTION 8: COMPLIANCE AND ENFORCEMENT
Failure to maintain an up-to-date BCP, failure to test backups within the required
schedule, or failure to remediate critical DR test findings within 30 days will be
escalated to the relevant department head's manager and reported to the CTO and Board
Audit Committee. Business continuity compliance is audited annually by the internal
audit team.
""",
    "sample_vendor_risk_policy.pdf": """\
ACME CORPORATION - VENDOR AND THIRD-PARTY RISK MANAGEMENT POLICY
Version 1.2 | Effective Date: February 1, 2026 | Owner: Chief Information Security Officer

SECTION 1: PURPOSE AND SCOPE
This policy establishes the requirements for identifying, assessing, and managing risks
associated with third-party vendors, suppliers, contractors, and service providers that
have access to ACME Corporation systems, data, or facilities, or whose products or
services are incorporated into ACME's operations. All business units that engage
third parties are subject to this policy.

SECTION 2: VENDOR CLASSIFICATION
Vendors must be classified into one of three risk tiers based on the sensitivity of
data they access and the criticality of the services they provide.

Tier 1 (Critical Vendors): Vendors that process Restricted data, provide critical
infrastructure services, or have administrative access to ACME systems. Examples include
cloud infrastructure providers, payroll processors, and managed security service providers.
Tier 1 vendors require the most rigorous due diligence and are reviewed annually.

Tier 2 (High-Risk Vendors): Vendors that process Confidential data or provide services
that, if disrupted, would materially impact ACME operations. Examples include CRM
platforms, HR software providers, and marketing analytics tools. Tier 2 vendors
are reviewed every 18 months.

Tier 3 (Standard Vendors): Vendors that access only Internal or Public data and provide
non-critical services. Examples include office supply vendors, event management firms,
and business travel agencies. Tier 3 vendors complete a self-assessment questionnaire
and are reviewed every 3 years.

SECTION 3: VENDOR ONBOARDING AND DUE DILIGENCE
No vendor may be onboarded or granted access to ACME systems or data until the
applicable due diligence process has been completed and approved. The Procurement team
is responsible for initiating the vendor onboarding workflow via the Vendor Portal.

Tier 1 vendor due diligence must include: a completed Third-Party Risk Assessment
questionnaire; review of SOC 2 Type II report (not older than 12 months) or
equivalent; review of the vendor's information security policy and incident response
plan; a penetration testing summary from the past 12 months; financial stability check;
sanctions screening against OFAC and applicable international sanctions lists;
a signed Data Processing Agreement (DPA) and Master Service Agreement (MSA);
and CISO approval before access is granted.

Tier 2 vendor due diligence must include: a completed Third-Party Risk Assessment
questionnaire; review of SOC 2 Type I or II report or equivalent; a signed DPA;
and IT Security team approval.

Tier 3 vendor due diligence must include: completion of the ACME Vendor Self-Assessment
form and a signed vendor agreement with standard security and confidentiality clauses.

SECTION 4: CONTRACTUAL REQUIREMENTS
All contracts with Tier 1 and Tier 2 vendors must include the following provisions:
compliance with ACME's security requirements; the right to audit the vendor's security
controls with reasonable notice; mandatory incident notification to ACME within 24 hours
of any security incident that may affect ACME data; data breach notification timelines
consistent with applicable law; data deletion or return upon contract termination;
restriction on subcontracting to fourth parties without ACME's prior written consent;
and compliance with applicable data protection laws (GDPR, CCPA, etc.).

Contracts must not be executed, renewed, or modified without review and sign-off from
Legal and, for Tier 1 vendors, the CISO.

SECTION 5: ONGOING MONITORING
Tier 1 vendors must undergo a formal annual review that reassesses their risk profile,
reviews updated SOC 2 reports, and evaluates any security incidents that occurred
during the year. Significant changes to a Tier 1 vendor's ownership, infrastructure,
or security posture must be reported to ACME immediately and trigger an out-of-cycle
review.

Continuous monitoring of Tier 1 vendors must be performed using an approved vendor
risk intelligence platform (e.g., BitSight, SecurityScorecard). Significant score
drops or newly identified vulnerabilities in the vendor's publicly observable
infrastructure must be escalated to the IT Security team within 48 hours for review.

All vendors must be re-screened against sanctions lists at contract renewal and
whenever the IT Security team issues a mandatory re-screen notice.

SECTION 6: VENDOR OFFBOARDING
When a vendor relationship ends, the following must be completed within 10 business days:
revocation of all access credentials and API keys; confirmation that all ACME data
held by the vendor has been deleted or returned (with written certification from the vendor);
retrieval or verified destruction of any ACME-owned hardware in the vendor's possession;
closure of the vendor record in the Vendor Portal; and retention of contract and
due-diligence records for 7 years after the end of the relationship.

If a vendor terminates the relationship unexpectedly or becomes insolvent, the IT Security
team must be notified immediately to initiate emergency access revocation.

SECTION 7: FOURTH-PARTY RISK
Tier 1 vendors must disclose all subcontractors (fourth parties) that have access to
ACME data. Fourth parties are subject to the same minimum security requirements as the
vendor itself. Vendors must obtain ACME's written approval before adding new fourth
parties with access to ACME data. ACME reserves the right to require replacement of
any fourth party that fails to meet the applicable security standards.

SECTION 8: COMPLIANCE AND ENFORCEMENT
Non-compliance with this policy, including engaging a vendor without completing the
required due diligence, is a policy violation that must be reported to the CISO.
Violations may result in disciplinary action, contract suspension, or contract
termination. Vendor risk management compliance is audited semi-annually by the
Information Security team and reported to the Board Audit Committee annually.
""",
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


def create_pdf(filepath: str, content: str) -> None:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

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

    doc.save(filepath)
    print(f"Created {filepath} ({doc.page_count} page(s))")
    doc.close()


for fname, content in POLICIES.items():
    create_pdf(os.path.join(OUTPUT_DIR, fname), content)
