/** Exact native minor amounts: never pass a large monetary integer through Number. */
export function formatPositionMoney(minor: string | null, currency: string | null): string {
  if (minor === null || !/^-?\d{1,19}$/.test(minor)) return "UNKNOWN";
  const amount = BigInt(minor);
  const raw = new Intl.NumberFormat("fr-FR", {
    maximumFractionDigits: 0
  }).format(amount);
  if (!currency) return `${raw} unités mineures · devise UNKNOWN`;
  try {
    const name = new Intl.DisplayNames(["fr"], {
      type: "currency",
      fallback: "none"
    }).of(currency);
    if (!name) return `${raw} unités mineures · ${currency}`;
    const digits = new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency
    }).resolvedOptions().maximumFractionDigits;
    if (digits === undefined) return `${raw} unités mineures · ${currency}`;
    const absolute = amount < 0n ? -amount : amount;
    const scale = 10n ** BigInt(digits);
    const whole = new Intl.NumberFormat("fr-FR", {
      maximumFractionDigits: 0
    }).format(absolute / scale);
    const fraction = digits ? `,${String(absolute % scale).padStart(digits, "0")}` : "";
    return `${amount < 0n ? "-" : ""}${whole}${fraction} ${currency}`;
  } catch {
    return `${raw} unités mineures · ${currency}`;
  }
}
