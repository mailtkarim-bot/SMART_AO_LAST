export const controlFixture = (id = 'package-1') => ({
  submission_package_id: id, package_version: 3, manifest_sha256: 'c'.repeat(64),
  dce_version_id: 'dce-1', state: 'PARTIAL' as const, source_state: 'CURRENT' as const,
  files: [], requirements: [], missing_cited_annexes: [], entries_without_exported_file: [],
  patron_review_ids: [], p5_authorization_status: 'NOT_RECORDED' as const, p5_authorization_id: null,
  signature_visibility: "RESTRICTED" as const, signature_records: [] as [], inventory: 'CURRENT_NON_FINANCIAL_SIGNALS_ONLY' as const,
  signature_requirement: 'UNKNOWN' as const, signature_verification: 'UNKNOWN' as const,
  signer_authority: 'UNKNOWN' as const, conformity: 'UNKNOWN' as const,
  external_submission: 'NOT_PERFORMED' as const,
});
