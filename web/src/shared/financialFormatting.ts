function hundredths(value: number) {
  const signed = BigInt(value);
  const absolute = signed < 0n ? -signed : signed;
  return { negative: signed < 0n, whole: absolute / 100n, fraction: (absolute % 100n).toString().padStart(2, "0") };
}

export function formatBasisPoints(value: number): string {
  if (!Number.isSafeInteger(value)) return "UNKNOWN";
  const { negative, whole, fraction } = hundredths(value);
  return `${negative ? "-" : ""}${whole}.${fraction}`;
}

export function formatMinorMoney(value: number, currency = "EUR"): string {
  if (!Number.isSafeInteger(value)) return "UNKNOWN";
  const { negative, whole, fraction } = hundredths(value);
  const formatter = new Intl.NumberFormat("fr-FR", { style: "currency", currency, minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const parts = formatter.formatToParts(negative ? -whole : whole);
  return (negative && whole === 0n ? "-" : "") + parts.map((part) => part.type === "fraction" ? fraction : part.value).join("");
}
