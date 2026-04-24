# ==========================================
# ROLE 3: OBSERVABILITY & QA ENGINEER
# ==========================================
# Task: Implement quality gates to reject corrupt data or logic discrepancies.

def run_quality_gate(document_dict):
    # Reject documents with 'content' length < 20 characters
    if len(document_dict.get('content', '')) < 20:
        return False

    # Reject documents containing toxic/error strings
    toxic_strings = ['Null pointer exception', 'Error', 'Failure']
    if any(toxic_string in document_dict.get('content', '') for toxic_string in toxic_strings):
        return False

    # Flag discrepancies in tax calculation comments
    tax_comment = document_dict.get('tax_comment', '')
    tax_code = document_dict.get('tax_code', 0)
    if '8%' in tax_comment and tax_code != 0.08:
        return False
    if '10%' in tax_comment and tax_code != 0.10:
        return False

    # Return True if all checks pass
    return True
