export function formatCurrency(
  amount: string | number,
  currency: string | null | undefined,
): string {
  if (!currency) return "—"

  try {
    const formatter = new Intl.NumberFormat(undefined, { style: "currency", currency })
    if (typeof amount === "number") {
      return Number.isFinite(amount) ? formatter.format(amount) : `${currency} --`
    }

    const match = /^(-?)(\d+)(?:\.(\d+))?$/.exec(amount)
    if (!match) return `${currency} --`
    const fractionDigits = formatter.resolvedOptions().maximumFractionDigits ?? 2
    const sourceFraction = match[3] ?? ""
    const keptFraction = sourceFraction
      .slice(0, fractionDigits)
      .padEnd(fractionDigits, "0")
    const scale = 10n ** BigInt(fractionDigits)
    let minorUnits = BigInt(match[2]) * scale
      + BigInt(keptFraction || "0")
    if (sourceFraction.length > fractionDigits && sourceFraction[fractionDigits] >= "5") {
      minorUnits += 1n
    }

    const whole = minorUnits / scale
    const fraction = String(minorUnits % scale).padStart(fractionDigits, "0")
    const negative = match[1] === "-"
    const signedWhole = negative ? -whole : whole
    const parts = negative && whole === 0n
      ? formatter.formatToParts(-1n).map((part) =>
          part.type === "integer" ? { ...part, value: "0" } : part,
        )
      : formatter.formatToParts(signedWhole)
    return parts
      .map((part) => part.type === "fraction" ? { ...part, value: fraction } : part)
      .map((part) => part.value)
      .join("")
  } catch {
    return `${currency} ${amount}`
  }
}

function toMinorUnits(amount: string): bigint {
  const match = /^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(amount)
  if (!match) throw new Error(`Invalid decimal amount: ${amount}`)
  const sign = match[1] === "-" ? -1n : 1n
  const whole = BigInt(match[2])
  const fraction = BigInt((match[3] ?? "").padEnd(2, "0"))
  return sign * (whole * 100n + fraction)
}

export function sumAmounts(amounts: Array<string | null>): string {
  const total = amounts.reduce(
    (sum, amount) => sum + (amount === null ? 0n : toMinorUnits(amount)),
    0n,
  )
  return fromMinorUnits(total)
}

export function subtractAmounts(left: string, right: string): string {
  return fromMinorUnits(toMinorUnits(left) - toMinorUnits(right))
}

export function isGreaterAmount(left: string, right: string): boolean {
  return toMinorUnits(left) > toMinorUnits(right)
}

export function getProgressPercent(spent: string, budget: string): number {
  const budgetUnits = toMinorUnits(budget)
  if (budgetUnits <= 0n) throw new Error("Budget must be a positive amount.")
  const percentHundredths = toMinorUnits(spent) * 10_000n / budgetUnits
  return Math.min(Number(percentHundredths) / 100, 100)
}

function fromMinorUnits(amount: bigint): string {
  const sign = amount < 0n ? "-" : ""
  const absolute = amount < 0n ? -amount : amount
  return `${sign}${absolute / 100n}.${String(absolute % 100n).padStart(2, "0")}`
}
