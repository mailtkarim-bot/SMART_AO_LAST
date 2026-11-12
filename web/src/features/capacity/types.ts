export type CapacitySource = {
  reference: string;
  revision: string;
  locator: string;
};
export type CapacityRow = {
  id: string;
  label: string;
  resource_type: string | null;
  units: number | null;
  start: string | null;
  end: string | null;
  source: CapacitySource | null;
  named_supply_id?: string | null;
};
export type CapacityInput = {
  command_id: string;
  idempotency_key: string;
  run_id: string;
  expected_revision: number;
  context_sha256: string;
  demands: CapacityRow[] | null;
  supplies: CapacityRow[] | null;
  justification: string;
  human_confirmed: true;
};
export type CapacityReceipt = {
  run_id: string;
  command_id: string;
  idempotency_key: string;
  revision: number;
  replayed: boolean;
};
export type CapacityRun = {
  run_id: string;
  revision: number;
  status: string;
  state: string;
  input_sha256: string;
  created_at: string;
  inputs: {
    demands: CapacityRow[] | null;
    supplies: CapacityRow[] | null;
    justification: string;
    source_kind: string;
  };
  result: {
    assignments: {
      demand_id: string;
      supply_id: string;
    }[];
    unknown_ids: string[];
    unassigned_demand_ids: string[];
    conflicts: {
      period: {
        start: string;
        end: string;
      };
      resource_type: string;
      required_units: number;
      available_units: number;
      demand_ids: string[];
    }[];
  };
};
export type CapacityProjection = {
  case_id: string;
  context_sha256: string;
  revision: number;
  current: CapacityRun | null;
  history: CapacityRun[];
  history_has_more: boolean;
  state: string;
  coverage_state: string;
  reservation_state: string;
};
