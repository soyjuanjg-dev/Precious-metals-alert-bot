def check_alert(metal_name: str, today: float, yesterday: float | None, threshold: float) -> str | None:
    """
    Devuelve un mensaje si el cambio porcentual supera el umbral.
    threshold = 6 (por ejemplo)
    """
    if yesterday is None or yesterday == 0:
        return None

    change_pct = ((today - yesterday) / yesterday) * 100

    if abs(change_pct) >= threshold:
        direction = "UP" if change_pct > 0 else "DOWN"
        return (
            f"🚨 ALERT: {metal_name}\n\n"
            f"Yesterday: ${yesterday:,.2f}\n"
            f"Today:     ${today:,.2f}\n"
            f"Change:    {change_pct:+.2f}% ({direction})\n\n"
            f"Threshold: ±{threshold:.2f}%"
        )

    return None
