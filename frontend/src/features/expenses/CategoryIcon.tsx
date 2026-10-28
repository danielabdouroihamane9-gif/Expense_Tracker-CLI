import {
  Building2,
  Bus,
  Film,
  HeartPulse,
  Lightbulb,
  MoreHorizontal,
  ShoppingBag,
  Utensils,
  type LucideIcon,
} from "lucide-react"
import type { ExpenseCategory } from "../../types/api"

const categoryIcons: Record<ExpenseCategory, LucideIcon> = {
  food: Utensils,
  transport: Bus,
  rent: Building2,
  utilities: Lightbulb,
  entertainment: Film,
  healthcare: HeartPulse,
  shopping: ShoppingBag,
  other: MoreHorizontal,
}

export function CategoryIcon({
  category,
  size = 16,
}: {
  category: ExpenseCategory
  size?: number
}) {
  const Icon = categoryIcons[category]
  return <Icon size={size} aria-hidden="true" />
}
