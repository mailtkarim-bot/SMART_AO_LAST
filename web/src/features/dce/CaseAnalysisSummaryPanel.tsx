import {AnalysisCapacity} from "./AnalysisCapacity";
import {AnalysisDossierHistory} from "./AnalysisDossierHistory";
import {AnalysisDossierForm} from "./AnalysisDossierForm";
import {AnalysisDossierPendingStore} from "./analysisDossierPending";
import {AnalysisTreatmentRead} from "./AnalysisTreatmentFields";
import { AnalysisCash } from "./AnalysisCash";
import { AnalysisPricing } from "./AnalysisPricing";
import {AnalysisAssessmentPendingStore} from "./analysisAssessmentPending";
import {useState,useSyncExternalStore} from "react";
import type {ApiClient} from "../../infrastructure/api";
import {AnalysisAssessmentForm} from "./AnalysisAssessmentForm";
import type { CaseAnalysisItem, CaseAnalysisSummary } from "../../shared/types";

type Props={sourceReadBlocked?:boolean;dossierPendingIntents?:AnalysisDossierPendingStore;pendingIntents?:AnalysisAssessmentPendingStore;intentScope?:string;api?:ApiClient;allowed:boolean;caseId:string;dceVersionId:string|null;summary:CaseAnalysisSummary|null;loading:boolean;error:string|null;onRefresh:()=>void};
const labels:Record<string,string>={CANDIDATURE_DOCUMENT:"Pièce de candidature",SITE_VISIT:"Visite",OFFER_DOCUMENT:"Pièce de l’offre",SUBMISSION_DEADLINE_SIGNAL:"Date de remise à vérifier",SUBMISSION_CHANNEL:"Canal de dépôt",FILE_CONSTRAINT:"Format de remise",AWARD_CRITERION_SIGNAL:"Critère de jugement",NEGOTIATION_SIGNAL:"Négociation",OFFER_VALIDITY_SIGNAL:"Validité de l’offre",CONTRACT_RISK_SIGNAL:"Signal de risque contractuel",TECHNICAL_PRESCRIPTION:"Prescription technique à revoir",LOGISTICS_CONSTRAINT:"Contrainte logistique à revoir",SCHEDULE_CONSTRAINT:"Contrainte de planning ou de ressources à revoir",HSE_CONSTRAINT:"Contrainte HSE à revoir",PAYMENT_TERM_SIGNAL:"Condition de paiement à revoir",ACCEPTANCE_TERM_SIGNAL:"Condition de réception à revoir"};
const nativeLabels:Record<string,string>={PENDING_HUMAN_CONFIRMATION:"Confirmation humaine attendue",CONFIRMED:"Confirmé par acte humain",REVIEW_REQUIRED:"À revoir",NOT_APPLICABLE:"Non applicable — acte humain enregistré",OPEN:"Ouvert",ACCEPTED:"Accepté — revue enregistrée",MITIGATED:"Mitigé — preuve enregistrée",UNKNOWN:"Inconnu (UNKNOWN)"};
function Source({item}:{item:CaseAnalysisItem}) {
 const source=item.source_state==="CURRENT_SOURCE"?item.source_anchor:null;
 if (!source) return <p>Source courante non prouvée · UNKNOWN</p>;
 const locator=source.locator_state==="RESOLVED"?source.locator:null;
 const coordinates=locator?.coordinates??{};
 const field=locator?.kind==="docx_paragraph"?"paragraph":locator?.kind==="text_line"||locator?.kind==="docling_markdown"?"line":["pdf_page","ocr_page","pymupdf_block"].includes(locator?.kind??"")?"page":null;
 const value=field?coordinates[field]:null;
 let location="localisation UNKNOWN";
 if(typeof value==="number"&&Number.isSafeInteger(value)&&value>0)location=`${field==="paragraph"?"paragraphe":field==="line"?"ligne":"page"} ${value}`;
 if(locator?.kind==="xlsx_cell"&&typeof coordinates.sheet==="string"&&coordinates.sheet.trim()&&typeof coordinates.cell==="string"&&coordinates.cell.trim())location=`feuille ${coordinates.sheet} · cellule ${coordinates.cell}`;
 if(locator?.kind==="docx_table_cell"&&[coordinates.table,coordinates.row,coordinates.column,coordinates.paragraph].every(v=>typeof v==="number"&&Number.isSafeInteger(v)&&v>0))location=`tableau ${coordinates.table} · ligne ${coordinates.row} · colonne ${coordinates.column} · paragraphe ${coordinates.paragraph} · contexte entre cellules UNKNOWN`;
 return <details><summary>Références de la source{` · ${location}`}</summary>
  <dl><dt>Document</dt><dd>{source.dce_document_id}</dd><dt>Version DCE</dt><dd>{source.dce_version_id}</dd><dt>Région de l’extrait</dt><dd>Octets {item.start_byte_offset}–{item.end_byte_offset}</dd><dt>Extraction</dt><dd>{source.extraction_id}</dd><dt>Empreinte du document</dt><dd>{source.source_sha256}</dd><dt>Empreinte du fragment</dt><dd>{source.fragment_sha256}</dd></dl>
 </details>;
}
function HumanAssessment({item}:{item:CaseAnalysisItem}) {
 const act=item.human_assessment;if(!act)return null;
 const current=act.state==="CURRENT"&&item.source_state==="CURRENT_SOURCE"&&Boolean(item.source_context_sha256)&&act.source_context_sha256===item.source_context_sha256;
 return <><p>Revue humaine · révision {act.revision} · {current?"déclaration source courante":"à revalider (REVIEW_REQUIRED)"}</p>
 {current&&<details><summary>Acte humain enregistré · révision {act.revision}</summary><dl><dt>Auteur</dt><dd>{act.actor_id}</dd><dt>Horodatage serveur</dt><dd><time dateTime={act.created_at}>{act.created_at}</time></dd><dt>Justification</dt><dd>{act.justification}</dd><dt>Raison des inconnus</dt><dd>{act.unknown_reason??"Sans objet — valeurs déclarées"}</dd><dt>Acte précédent</dt><dd>{act.previous_assessment_id??"Première révision"}</dd><dt>Empreinte du contexte source</dt><dd>{act.source_context_sha256}</dd></dl></details>}</>;
}
function TableContext({item}:{item:CaseAnalysisItem}) {
 const context=item.source_state==="CURRENT_SOURCE"?item.table_context:null;
 if(!context)return null;
 if(context.state!=="EXACT_SOURCE")return <p>Contexte du tableau : UNKNOWN · {context.unknown_reason==="READ_BUDGET_EXCEEDED"?"Budget de lecture dépassé. Consultez le document.":"Sources à revalider."}</p>;
 return <details><summary>Cellules du tableau · contexte à relire</summary>
  <p>Aucune portée ni condition héritée. En-têtes, conditions et négations sont conservés tels qu’extraits ; leur applicabilité reste UNKNOWN.</p>
  <ul>{context.cells.map(cell=><li key={cell.source_anchor.source_anchor_id}>
   <blockquote style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{cell.text}</blockquote>
   <Source item={{...item,source_anchor:cell.source_anchor,start_byte_offset:0,end_byte_offset:new TextEncoder().encode(cell.text).length}}/>
  </li>)}</ul>
 </details>;
}
function Anatomy({item}:{item:CaseAnalysisItem}) {
 const current=item.source_state==="CURRENT_SOURCE";
 const excerpt=current && item.source_excerpt_state==="EXACT_SOURCE" ? item.source_excerpt : null;
 const assessment=current&&item.source_context_sha256&&item.human_assessment?.state==="CURRENT"&&item.human_assessment.source_context_sha256===item.source_context_sha256?item.human_assessment:null;
 const expected=assessment?.expected_evidence_state==="DECLARED"?assessment.expected_evidence:"UNKNOWN";
 const residual=assessment?.residual_risk_state==="DECLARED"?assessment.residual_risk:"UNKNOWN";
 const severity=current?({LOW:"faible",MEDIUM:"modérée",HIGH:"élevée",CRITICAL:"critique",UNKNOWN:"UNKNOWN"}[item.severity??"UNKNOWN"]):"UNKNOWN";
 return <>
  {excerpt?<><p>Extrait exact de la source :</p><blockquote style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere"}}>{excerpt}</blockquote></>:<p>{current && item.source_excerpt_unknown_reason==="READ_BUDGET_EXCEEDED"?"Extrait au-delà du budget de lecture (UNKNOWN). Consultez la source.":"Extrait source : UNKNOWN"}</p>}
  <p>Criticité déclarée : {severity} · Preuve attendue : {expected} · Risque résiduel : {residual}</p>
 </>;
}
function FollowUps({item}:{item:CaseAnalysisItem}) {
 const entries=item.source_state==="CURRENT_SOURCE" && item.follow_up_state==="RECORDED" ? item.follow_ups??[] : [];
 if (!entries.length && item.human_assessment?.state==="CURRENT" && item.human_assessment.treatment) return <p>Relation native d’action non établie; traitement humain déclaré ci-dessous.</p>;
 if (!entries.length) return <p>Relations non établies · Conséquences : UNKNOWN · Responsable : UNKNOWN · Action attendue : UNKNOWN</p>;
 return <ul aria-label="Actions, conditions et conséquences enregistrées">{entries.map(entry=><li key={`${entry.kind}:${entry.record_id}:${entry.relation_id??"direct"}:${entry.risk_requirement_link_id??"direct"}`}>
  <strong>{entry.description}</strong>
  <p>{entry.kind==="ACTION"?"Action Patron":entry.kind==="CONDITION"?"Condition Patron":"Impact contractuel"} · {nativeLabels[entry.state]??({IN_PROGRESS:"En cours",WAITING:"En attente",COMPLETED:"Terminée — état enregistré",ABANDONED:"Abandonnée",SATISFIED:"Satisfaite — état enregistré",FAILED:"Échec enregistré",WAIVED:"Dérogation enregistrée",HUMAN_REVIEW_REQUIRED:"Revue humaine requise"}[entry.state]??"État à revalider")}</p>
  <p>Conséquence déclarée : {entry.consequence??"UNKNOWN"} · Responsable affecté : {entry.responsible_actor_id??"UNKNOWN"} · Échéance : {entry.due_at??"UNKNOWN"}</p>
  <details><summary>Relation enregistrée et révision</summary><p>Référence : {entry.record_id} · Révision : {entry.revision} · Lien : {entry.relation_id??"direct"} · Exigence : {entry.requirement_id??"UNKNOWN"} · Risque : {entry.risk_id??"UNKNOWN"}{entry.risk_requirement_link_id?` · Lien risque/exigence : ${entry.risk_requirement_link_id}`:""}{entry.contract_impact_id?` · Preuve d’impact : ${entry.contract_impact_id} @ ${entry.contract_impact_revision}`:""}{entry.decision_id?` · Décision : ${entry.decision_id} · Contexte : ${entry.context_id}`:""}</p></details>
 </li>)}</ul>;
}
export function CaseAnalysisSummaryPanel({sourceReadBlocked=false,dossierPendingIntents,api,pendingIntents,intentScope,allowed,caseId,dceVersionId,summary,loading,error,onRefresh}:Props) {
 const[fallbackDossier]=useState(()=>new AnalysisDossierPendingStore());const dossierRegistry=dossierPendingIntents??fallbackDossier;
 const dossierSnapshot=useSyncExternalStore(dossierRegistry.subscribe,dossierRegistry.getSnapshot);
 const[fallbackRegistry]=useState(()=>new AnalysisAssessmentPendingStore());
 const registry=pendingIntents??fallbackRegistry;
 const pendingSnapshot=useSyncExternalStore(registry.subscribe,registry.getSnapshot);const assessmentScope=intentScope??caseId;
 const pending=[...pendingSnapshot.entries()].filter(([key])=>JSON.parse(key)[0]===assessmentScope).map(([,payload])=>payload);
 const dossierPending=dossierSnapshot.get(assessmentScope);
 const[writeLocked,setWriteLocked]=useState(pending.length>0);const[notice,setNotice]=useState("");
 if (!allowed) return null;
 if (sourceReadBlocked) return <section id="case-analysis-summary-section" className="section-block" aria-label="Synthèse métier du DCE"><h2>Synthèse métier du DCE</h2><p role="status">Admission DCE en cours ou UNKNOWN : synthèse, traitements et revue suspendus. Les actes antérieurs restent conservés ; résolvez le même acte DCE avant toute relecture.</p></section>;
 const value=summary?.case_id===caseId && summary?.dce_version_id===dceVersionId ? summary:null;
 const orphaned=pending.filter(payload=>!value?.axes.some(axis=>axis.items.some(item=>item.kind===payload.point_kind&&item.item_id===payload.point_id&&item.source_state==="CURRENT_SOURCE"&&item.source_context_sha256===payload.source_context_sha256)));
 return <section id="case-analysis-summary-section" className="section-block" aria-label="Synthèse métier du DCE" style={{overflowWrap:"anywhere"}}>
  <div className="section-heading"><h2>Synthèse métier du DCE</h2><button className="secondary-button compact-button" type="button" onClick={onRefresh} disabled={writeLocked||pending.length>0||Boolean(dossierPending)||loading||!caseId||!dceVersionId}>{loading?"Chargement…":"Charger la synthèse"}</button></div>
  <p>Cette lecture ne vaut pas analyse complète. Les champs non prouvés restent UNKNOWN.</p>
  {!dceVersionId && <p>Chargez d’abord la lecture DCE courante de l’Affaire.</p>}
  {notice&&<p role="status">{notice}</p>}
  {error && <p role="alert">{error}</p>}
  {api&&orphaned.length>0&&<><p>Acte antérieur au résultat inconnu : aucune nouvelle déclaration ou relecture avant un reçu ou un conflit.</p>{orphaned.map(payload=><AnalysisAssessmentForm historical key={payload.assessment_id} item={{item_id:payload.point_id,kind:payload.point_kind,source_context_sha256:payload.source_context_sha256,human_assessment:null}} pendingIntents={registry} intentScope={assessmentScope} disabled save={input=>api.recordCaseAnalysisAssessment(caseId,input)} onLock={setWriteLocked} onNotice={setNotice} onRefresh={onRefresh}/>)}</>}
  {!value&&api&&dossierPending&&<AnalysisDossierForm summary={null} scope={assessmentScope} store={dossierRegistry} disabled={false} save={input=>api.recordCaseAnalysisDossier(caseId,input)} onLock={setWriteLocked} onNotice={setNotice} onRefresh={onRefresh}/>}
  {value && <>
   {value.source_context_state !== "CURRENT" && <p role="status">Sources à revalider : le DCE est incomplet, non vérifié ou à revoir.</p>}
   {value.truncated && <p role="status">Vue limitée : des éléments supplémentaires restent à examiner.</p>}
   {value.coverage && <p>{value.coverage.unread_documents} pièce(s) non lue(s) dans l’inventaire admis. Complétude de l’inventaire : UNKNOWN. Consultez les pièces annoncées manquantes et les exclusions dans la lecture DCE.</p>}
   <p>Le tableau peut défiler horizontalement.</p><div className="line-table-wrap" role="region" aria-label="Axes métier — tableau défilant" tabIndex={0}><table><caption>Douze axes métier · classement des signaux existants uniquement</caption><thead><tr><th scope="col">Axe</th><th scope="col">Évaluation</th><th scope="col">Éléments et sources</th></tr></thead><tbody>
    {value.axes.map(axis=><tr key={axis.code}><th scope="row">{axis.label}</th><td>{axis.status==="NON_EVALUATED"?"Non évalué":"À revoir"}</td><td>{axis.code==="CASH"&&<AnalysisCash reports={axis.cash_reports??[]} scenarios={axis.pricing_scenarios??[]} caseId={caseId} current={value.source_context_state==="CURRENT"}/>}
     {axis.code==="CAPACITY"&&<AnalysisCapacity plans={axis.capacity_plans??[]} caseId={caseId} current={value.source_context_state==="CURRENT"}/>}
     {axis.code==="PRICE"&&<AnalysisPricing scenarios={axis.pricing_scenarios??[]} caseId={caseId} current={value.source_context_state==="CURRENT"}/>}
     {axis.items.length===0?"Couverture non établie":<ul>{axis.items.map(item=><li key={`${item.kind}:${item.item_id}`}>
      <strong>{item.source_state==="CURRENT_SOURCE" && item.title ? item.title : labels[item.native_type]??"Risque à relire"}</strong>
      <p>État enregistré : {nativeLabels[item.native_state]??"État à revalider"}. Applicabilité au lot : UNKNOWN.{item.lot_state==="CANDIDATE"?` Lots candidats : ${item.lot_numbers.join(", ")}.`:""}</p>
      <Anatomy item={item}/><Source item={item}/><TableContext item={item}/><FollowUps item={item}/>
      <HumanAssessment item={item}/>{item.human_assessment?.state==="CURRENT"&&item.human_assessment.treatment&&item.human_assessment.source_context_sha256===item.source_context_sha256&&<AnalysisTreatmentRead value={item.human_assessment.treatment} actorId={item.human_assessment.actor_id}/>}
      {api&&item.source_state==="CURRENT_SOURCE"&&item.source_context_sha256&&!orphaned.some(payload=>payload.point_kind===item.kind&&payload.point_id===item.item_id)&&<AnalysisAssessmentForm key={item.source_context_sha256} pendingIntents={registry} intentScope={assessmentScope} axisCode={axis.code} item={item} disabled={writeLocked||Boolean(dossierPending)} save={input=>api.recordCaseAnalysisAssessment(caseId,input)} onLock={setWriteLocked} onNotice={setNotice} onRefresh={onRefresh}/>}
    </li>)}</ul>}</td></tr>)}
   </tbody></table></div>
   {api&&<AnalysisDossierForm key={`${value.dossier_sha256??"legacy"}:${value.dossier_review?.revision??0}`} summary={value} scope={assessmentScope} store={dossierRegistry} disabled={pending.length>0||writeLocked} save={input=>api.recordCaseAnalysisDossier(caseId,input)} onLock={setWriteLocked} onNotice={setNotice} onRefresh={onRefresh}/>}
  </>}
  {api&&<AnalysisDossierHistory key={assessmentScope} api={api} caseId={caseId} disabled={writeLocked||pending.length>0||Boolean(dossierPending)}/>}
 </section>;
}
