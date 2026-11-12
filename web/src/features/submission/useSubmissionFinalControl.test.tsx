import { act, renderHook } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import type { ApiClient } from '../../infrastructure/api';
import { useSubmissionActions } from './useSubmissionActions';

import { controlFixture } from "./finalControl.testdata";

describe('exact final control', () => {
  it('requires human confirmation before requesting a signature', async () => {
    const api = { requestSubmissionSignature: vi.fn().mockResolvedValue({ aggregate_refs: [] }) };
    const { result } = renderHook(() => useSubmissionActions(api as unknown as ApiClient, vi.fn()));
    act(() => result.current.setSubmissionPackageId('package-1'));
    await act(async () => result.current.requestSignature());
    expect(api.requestSubmissionSignature).not.toHaveBeenCalled();
  });

  it('discards a late control after another package is selected', async () => {
    let resolve!: (value: ReturnType<typeof controlFixture>) => void;
    const api = { getSubmissionFinalControl: vi.fn().mockImplementation(() => new Promise(r => { resolve = r; })) };
    const { result } = renderHook(() => useSubmissionActions(api as unknown as ApiClient, vi.fn()));
    act(() => result.current.setSubmissionPackageId('package-1'));
    let pending!: Promise<void>;
    act(() => { pending = result.current.loadFinalControl(); });
    act(() => result.current.setSubmissionPackageId('package-2'));
    await act(async () => { resolve(controlFixture()); await pending; });
    expect(result.current.finalControl).toBeNull();
  });
});

it('retries exactly one frozen signature intent after UNKNOWN and masks changed selection', async () => {
  const request = vi.fn().mockRejectedValueOnce(new Error('network timeout'))
    .mockImplementationOnce((_id, _version, metadata) => Promise.resolve({ aggregate_refs: [{ aggregate_id: metadata.signature_id }] }));
  const api = { getSubmissionFinalControl: vi.fn().mockResolvedValue(controlFixture()),
    requestSubmissionSignature: request, getSubmissionSignature: vi.fn() };
  const { result } = renderHook(() => useSubmissionActions(api as unknown as ApiClient, vi.fn()));
  act(() => result.current.setSubmissionPackageId('package-1'));
  await act(async () => result.current.loadFinalControl());
  act(() => result.current.setSignatureRationale('Les seuls octets synthétiques relus.'));
  act(() => result.current.setSignatureConfirmed(true));
  await act(async () => result.current.requestSignature());
  expect(result.current.signatureIntent).not.toBeNull();
  expect(api.getSubmissionSignature).not.toHaveBeenCalled();
  act(() => result.current.setSubmissionPackageId('package-2'));
  act(() => result.current.setSignatureRationale('Motif différent non transférable.'));
  await act(async () => result.current.loadFinalControl());
  expect(api.getSubmissionFinalControl).toHaveBeenCalledTimes(1);
  await act(async () => result.current.requestSignature());
  expect(request).toHaveBeenCalledTimes(2);
  expect(request.mock.calls[1]).toEqual(request.mock.calls[0]);
  expect(result.current.signatureStatus).toBeNull();
  expect(result.current.signatureIntent).toBeNull();
});

it('prevents double-click effects and masks a late receipt after selection changes', async () => {
  let finish!: (receipt: { aggregate_refs: Array<{ aggregate_id: string }> }) => void;
  const request = vi.fn().mockImplementation(() => new Promise(r => { finish = r; }));
  const api = { getSubmissionFinalControl: vi.fn().mockResolvedValue(controlFixture()), requestSubmissionSignature: request };
  const { result } = renderHook(() => useSubmissionActions(api as unknown as ApiClient, vi.fn()));
  act(() => result.current.setSubmissionPackageId('package-1'));
  await act(async () => result.current.loadFinalControl());
  act(() => result.current.setSignatureRationale('Qualification uniquement.'));
  act(() => result.current.setSignatureConfirmed(true));
  let pending!: Promise<void>;
  act(() => { pending = result.current.requestSignature(); });
  await act(async () => result.current.requestSignature());
  expect(request).toHaveBeenCalledTimes(1);
  act(() => result.current.setSubmissionPackageId('package-2'));
  await act(async () => { finish({ aggregate_refs: [{ aggregate_id: request.mock.calls[0][2].signature_id }] }); await pending; });
  expect(result.current.signatureStatus).toBeNull();
});

it('never projects a SIGNED result from another package', async () => {
  const api = { getSubmissionFinalControl: vi.fn().mockResolvedValue(controlFixture()),
    getSubmissionSignature: vi.fn().mockResolvedValue({ signature_id: 'signature-1', submission_package_id: 'other-package',
      expected_package_version: 3, manifest_sha256: 'c'.repeat(64), status: 'SIGNED', provider: 'TEST_PROVIDER', revision: 2 }) };
  const publish = vi.fn();
  const { result } = renderHook(() => useSubmissionActions(api as unknown as ApiClient, publish));
  act(() => result.current.setSubmissionPackageId('package-1'));
  await act(async () => result.current.loadFinalControl());
  act(() => result.current.setSignatureId('signature-1'));
  await act(async () => result.current.loadSignature());
  expect(result.current.signatureStatus).toBeNull();
  expect(publish).toHaveBeenLastCalledWith(expect.objectContaining({ tone: 'error' }));
});

it('invalidates a signature read and clears its status when its identifier changes', async () => {
  let finish!: (record: object) => void;
  const api = { getSubmissionFinalControl: vi.fn().mockResolvedValue(controlFixture()),
    getSubmissionSignature: vi.fn().mockImplementation(() => new Promise(r => { finish = r; })) };
  const { result } = renderHook(() => useSubmissionActions(api as unknown as ApiClient, vi.fn()));
  act(() => result.current.setSubmissionPackageId('package-1'));
  await act(async () => result.current.loadFinalControl());
  act(() => result.current.setSignatureId('signature-A'));
  let pending!: Promise<void>;
  act(() => { pending = result.current.loadSignature(); });
  act(() => result.current.setSignatureId('signature-B'));
  await act(async () => {
    finish({ signature_id: 'signature-A', submission_package_id: 'package-1', expected_package_version: 3,
      manifest_sha256: 'c'.repeat(64), status: 'SIGNED', provider: 'TEST_PROVIDER', revision: 2 });
    await pending;
  });
  expect(result.current.signatureId).toBe('signature-B');
  expect(result.current.signatureStatus).toBeNull();
});

it('masks a cached P5 and manifest when another package is selected', async () => {
  const api = { getSubmissionPackageManifest: vi.fn().mockResolvedValue({ submission_package_id: 'package-1',
    package_version: 3, manifest_sha256: 'a'.repeat(64), manifest: {}, authorization_status: 'AUTHORIZED' }) };
  const { result } = renderHook(() => useSubmissionActions(api as unknown as ApiClient, vi.fn()));
  act(() => result.current.setSubmissionPackageId('package-1'));
  await act(async () => result.current.loadSubmissionPackageManifest());
  expect(result.current.submissionAuthorized).toBe(true);
  act(() => result.current.setSubmissionPackageId('package-2'));
  expect(result.current.submissionManifest).toBeNull();
  expect(result.current.submissionAuthorized).toBe(false);
});
