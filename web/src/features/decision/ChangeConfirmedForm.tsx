import { useState, type ComponentProps, type SubmitEvent } from 'react';
export type ChangeConsent = {
  human_confirmed: true;
  justification: string;
  publish: boolean;
};
export function ChangeConfirmedForm({
  children,
  onSubmit,
  onApprove,
  canPublish = false,
  locked = false,
  ...props
}: ComponentProps<'form'> & {
  onApprove: (consent: ChangeConsent) => void;
  canPublish?: boolean;
  locked?: boolean;
}) {
  const [why, setWhy] = useState(''),
    [confirmed, setConfirmed] = useState(false),
    [publish, setPublish] = useState(false),
    [invalid, setInvalid] = useState(false);
  function submit(event: SubmitEvent<HTMLFormElement>) {
    if (locked || !why.trim() || !confirmed) {
      event.preventDefault();
      setInvalid(true);
      return;
    }
    onApprove({
      human_confirmed: true,
      justification: why.trim(),
      publish: canPublish && publish
    });
    onSubmit?.(event);
  }
  return <form {...props} onSubmit={submit} onChangeCapture={event => {
    if (!(event.target instanceof HTMLInputElement) || event.target.name !== 'change_human_confirmed') setConfirmed(false);
  }}>
  {children}
  <fieldset className="workflow-form" disabled={locked}><legend>Confirmation de cet acte précis</legend>
   <label>Justification de cet acte<textarea name="change_justification" required maxLength={2000} value={why} onChange={e => {
          setWhy(e.target.value);
          setInvalid(false);
        }} /></label>
   {canPublish && <label><input type="checkbox" checked={publish} onChange={e => setPublish(e.target.checked)} />Publier les seuls éléments opérationnels de cet acte au Responsable affecté. Les pièces et impacts financiers restent privés.</label>}
   <label><input name="change_human_confirmed" type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} />Je confirme cet acte et les sources, valeurs et inconnus de ce formulaire.</label>
   {invalid && <p role="alert">Justifiez et confirmez cet acte avant son enregistrement.</p>}
  </fieldset>
 </form>;
}
