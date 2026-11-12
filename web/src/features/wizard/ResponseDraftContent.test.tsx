import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ResponseDraftContent } from "./ResponseDraftContent";

const prefix = "- Sources résolues côté serveur : ";
describe("ResponseDraftContent", () => {
  it("separates readable wording from exact native provenance without changing the bytes", () => {
    const native = "# Brouillon\n" + prefix + JSON.stringify({buyer:{document_family:"RC",locator:"RC · ligne 1",buyer_excerpt:"Le DC1 est obligatoire.",lot:"UNKNOWN",anchor:{source_sha256:"a".repeat(64)}},enterprise:{proofs:[{document_id:"proof-1",sha256:"b".repeat(64)}]}}) + "\n> Aucun accès ne sera fermé.\n- Manques déclarés : signature attendue.";
    render(<ResponseDraftContent content={native}/>);
    expect(screen.getByLabelText("Rédaction et manques")).toHaveTextContent("Aucun accès ne sera fermé.");
    expect(screen.getByLabelText("Rédaction et manques")).not.toHaveTextContent("source_sha256");
    expect(screen.getByText("Le DC1 est obligatoire.")).toBeInTheDocument();
    expect(screen.getByLabelText("Contenu natif exact").textContent).toBe(native);
  });
  it("keeps malformed provenance visible as UNKNOWN with the native text available", () => {
    render(<ResponseDraftContent content={prefix + "invalid"}/>);
    expect(screen.getByText(/Source non interprétable.*UNKNOWN/)).toBeInTheDocument();
    expect(screen.getByLabelText("Contenu natif exact")).toHaveTextContent("invalid");
  });
  it("keeps the historical plain draft readable", () => {
    render(<ResponseDraftContent content="Ancien brouillon sans manifeste local."/>);
    expect(screen.getByLabelText("Contenu natif exact")).toHaveTextContent("Ancien brouillon");
  });
});

it("keeps unavailable native content UNKNOWN", () => {
  render(<ResponseDraftContent content={null}/>);
  expect(screen.getByText("Contenu natif non relu · UNKNOWN")).toBeInTheDocument();
});

it('labels a DOCX text projection without presenting it as the binary bytes',()=>{
 render(<ResponseDraftContent content="Texte Word : UNKNOWN" format="DOCX" provenance={{schema_version:1}}/>);
 expect(screen.getByLabelText('Aperçu textuel DOCX')).toHaveTextContent('Texte Word');
 expect(screen.queryByLabelText('Contenu natif exact')).toBeNull();
 expect(screen.getByText(/empreinte porte sur le fichier DOCX/)).toBeInTheDocument();
});
