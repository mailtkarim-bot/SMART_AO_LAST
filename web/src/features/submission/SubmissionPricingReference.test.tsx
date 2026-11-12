import { render, screen } from "@testing-library/react";
import { expect, it } from "vitest";
import { SubmissionFinalControl } from "./SubmissionFinalControl";
import { controlFixture } from "./finalControl.testdata";

it("shows the old and latest published reference without inheriting the old agreement", () => {
  render(<SubmissionFinalControl report={{...controlFixture(), pricing_reference: {
    state: "REVIEW_REQUIRED", reason_code: "NEWER_PUBLISHED_REPORT",
    referenced: {report_id: "report-v1", revision: 4},
    latest_published: {report_id: "report-v2", revision: 2},
  }}}/>);
  expect(screen.getByText(/Chiffrage révisé : cette référence est à relire/)).toBeInTheDocument();
  expect(screen.getByText(/report-v1/)).toBeInTheDocument();
  expect(screen.getByText(/report-v2/)).toBeInTheDocument();
  expect(screen.getByText(/Aucun accord sur le nouveau chiffrage n’est déduit/)).toBeInTheDocument();
});

it("keeps a legacy control without a price reference UNKNOWN", () => {
  render(<SubmissionFinalControl report={controlFixture()}/>);
  expect(screen.getByText(/Référence de chiffrage UNKNOWN/)).toBeInTheDocument();
});


it.each([
  ["CURRENT", "Référence du dernier chiffrage publié"],
  ["NOT_APPLICABLE", "Candidature seule : aucune référence de chiffrage attendue"],
] as const)("keeps %s separate from conformity and P5", (state, message) => {
  render(<SubmissionFinalControl report={{...controlFixture(), pricing_reference: {
    state, referenced: state === "CURRENT" ? {report_id: "report-v1", revision: 0} : null,
    latest_published: state === "CURRENT" ? {report_id: "report-v1", revision: 0} : null,
    reason_code: state === "CURRENT" ? "LATEST_PUBLISHED_REFERENCE" : "CANDIDATURE_ONLY",
  }}}/>);
  expect(screen.getByText(new RegExp(message))).toBeInTheDocument();
  expect(screen.getByText(/P5 non enregistrée/)).toBeInTheDocument();
});

it("explains a fresh response review and exact package without transferring private cash flows",()=>{
 render(<SubmissionFinalControl report={{...controlFixture(),pricing_reference:{state:"REVIEW_REQUIRED",reason_code:"NEWER_PUBLISHED_REPORT",referenced:{report_id:"old",revision:2},latest_published:{report_id:"new",revision:3}}}}/>);
 expect(screen.getByText(/Pour reprendre : nouveau brouillon sourcé, nouvelle revue Patron/)).toBeInTheDocument();
 expect(screen.getByText(/Les flux et hypothèses de trésorerie privés ne sont pas repris automatiquement/)).toBeInTheDocument();
 expect(screen.getByText(/P5 non enregistrée/)).toBeInTheDocument();
});
