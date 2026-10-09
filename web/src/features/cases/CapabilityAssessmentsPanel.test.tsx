import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { CapabilityAssessmentsPanel } from "./CapabilityAssessmentsPanel";

const props = {caseId:'case-a', projection:null, loading:false, error:null, onRefresh:vi.fn()};
describe('documentary eligibility panel',()=>{
  it('shows only documentary states and exact evaluation dates',()=>{
    const {container}=render(<CapabilityAssessmentsPanel {...props} projection={[{state:'CURRENT',evaluatedAt:'2026-10-08T09:00:00.123456Z'},{state:'EXPIRED',evaluatedAt:'2026-10-08T09:00:00Z'},{state:'UNKNOWN',evaluatedAt:null}]} />);
    expect(screen.getByText('CURRENT')).toBeVisible();expect(screen.getByText('EXPIRED')).toBeVisible();expect(screen.getByText('UNKNOWN')).toBeVisible();
    expect(screen.getByText('2026-10-08T09:00:00.123456Z')).toBeVisible();
    expect(screen.getByText('Date inconnue')).toBeVisible();
    expect(screen.getAllByRole('button')).toHaveLength(1);
    expect(container.textContent).not.toMatch(/case-a|proposal_id|source_locator|storage_key|sha256/);
  });
  it('separates selection/loading/error/empty and hides old rows',()=>{
    const {rerender}=render(<CapabilityAssessmentsPanel {...props} caseId=''/>);
    expect(screen.getByText(/Sélectionnez une affaire/)).toBeVisible();
    rerender(<CapabilityAssessmentsPanel {...props} loading projection={[{state:'CURRENT',evaluatedAt:null}]}/>);
    expect(screen.getByRole('status')).toBeVisible();expect(screen.queryByText('CURRENT')).toBeNull();
    rerender(<CapabilityAssessmentsPanel {...props} error='Lecture indisponible' projection={[{state:'CURRENT',evaluatedAt:null}]}/>);
    expect(screen.getByRole('alert')).toHaveTextContent('Lecture indisponible');expect(screen.queryByText('CURRENT')).toBeNull();
    rerender(<CapabilityAssessmentsPanel {...props} projection={[]}/>);
    expect(screen.getByText(/Aucune évaluation retournée/)).toBeVisible();
  });
});
