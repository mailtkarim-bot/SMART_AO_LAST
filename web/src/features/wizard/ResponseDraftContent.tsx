const sourcePrefix = "- Sources résolues côté serveur : ";

type RecordValue = Record<string, unknown>;
function record(value: unknown): RecordValue {
  return value !== null && typeof value === "object" && !Array.isArray(value) ? value as RecordValue : {};
}
function text(value: unknown) { return typeof value === "string" ? value : "UNKNOWN"; }
function capturedSource(line: string): RecordValue {
  try { return record(JSON.parse(line.slice(sourcePrefix.length))); }
  catch { return {}; }
}

export function ResponseDraftContent({ content,format="MARKDOWN",provenance }: { content: string | null;format?:"MARKDOWN"|"DOCX";provenance?:Record<string,unknown>|null }) {
  if (content === null) return <p>Contenu natif non relu · UNKNOWN</p>;
  if(format==="DOCX")return <div><p>Aperçu textuel uniquement : l’empreinte porte sur le fichier DOCX binaire, à télécharger pour la revue de la pièce exacte.</p>
    <pre className="review-draft-content" aria-label="Aperçu textuel DOCX">{content}</pre>
    <details><summary>Provenance des régions, sources et champs UNKNOWN</summary><pre className="review-draft-content">{JSON.stringify(provenance??{state:"UNKNOWN"},null,2)}</pre></details></div>;
  const lines = content.split("\n");
  const sources = lines.filter((line) => line.startsWith(sourcePrefix));
  if (sources.length === 0) return <pre className="review-draft-content" aria-label="Contenu natif exact">{content}</pre>;
  const wording = lines.filter((line) => !line.startsWith(sourcePrefix)).join("\n");
  return <div>
    <pre className="review-draft-content" aria-label="Rédaction et manques">{wording}</pre>
    <h4>Sources figées du brouillon</h4>
    <p>Ces références sont celles du texte enregistré. Leur présence ne prouve ni la couverture, ni leur actualité.</p>
    {sources.slice(0, 64).map((line, index) => {
      const source = capturedSource(line);
      const buyer = record(source.buyer);
      const anchor = record(buyer.anchor);
      const enterprise = record(source.enterprise);
      if (Object.keys(buyer).length === 0) return <p key={index}>Source non interprétable · UNKNOWN</p>;
      return <section key={index} aria-label={`Source figée ${index + 1}`}>
        <strong>Acheteur : {text(buyer.document_family)} · {text(buyer.locator)}</strong>
        <blockquote>{text(buyer.buyer_excerpt)}</blockquote>
        <p>Portée lot enregistrée : {text(buyer.lot)} · Couverture : {text(source.coverage)}</p>
        <details><summary>Version, région et empreintes enregistrées</summary>
          <dl>
            <dt>Version DCE</dt><dd>{text(buyer.dce_version_id)}</dd>
            <dt>État source enregistré</dt><dd>{text(buyer.source_state)}</dd>
            <dt>Ancre</dt><dd>{text(anchor.source_anchor_id)}</dd>
            <dt>SHA-256 de la pièce acheteur</dt><dd>{text(anchor.source_sha256)}</dd>
            <dt>Capacité entreprise versionnée</dt><dd>{text(source.capability_version_id)}</dd>
          </dl>
          {Array.isArray(enterprise.proofs) && enterprise.proofs.slice(0, 64).map((proof, proofIndex) => <p key={proofIndex}>Pièce entreprise : {text(record(proof).document_id)} · SHA-256 {text(record(proof).sha256)}</p>)}
        </details>
      </section>;
    })}
    {sources.length > 64 && <p>Sources supplémentaires non projetées · UNKNOWN. Consultez le contenu natif.</p>}
    <details><summary>Contenu natif exact pour contrôle du SHA-256</summary><pre className="review-draft-content" aria-label="Contenu natif exact">{content}</pre></details>
  </div>;
}
