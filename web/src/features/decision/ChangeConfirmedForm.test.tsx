import { fireEvent, render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { ChangeConfirmedForm } from './ChangeConfirmedForm';
test('requires a reason and confirmation; editing resets confirmation, publication stays explicit', () => {
  const approve = vi.fn(),
    submit = vi.fn(e => e.preventDefault());
  render(<ChangeConfirmedForm canPublish onApprove={approve} onSubmit={submit}><label>Instruction<input name="instruction" /></label><button type="submit">Enregistrer</button></ChangeConfirmedForm>);
  fireEvent.click(screen.getByText('Enregistrer'));
  expect(submit).not.toHaveBeenCalled();
  fireEvent.change(screen.getByLabelText('Justification de cet acte'), {
    target: {
      value: 'Instruction relue sur les sources exactes.'
    }
  });
  fireEvent.click(screen.getByLabelText(/Je confirme cet acte/));
  fireEvent.change(screen.getByLabelText('Instruction'), {
    target: {
      value: 'Accès secondaire'
    }
  });
  fireEvent.click(screen.getByText('Enregistrer'));
  expect(submit).not.toHaveBeenCalled();
  fireEvent.click(screen.getByLabelText(/Je confirme cet acte/));
  fireEvent.click(screen.getByText('Enregistrer'));
  expect(approve).toHaveBeenCalledWith(expect.objectContaining({
    publish: false,
    human_confirmed: true
  }));
  expect(submit).toHaveBeenCalledOnce();
});
