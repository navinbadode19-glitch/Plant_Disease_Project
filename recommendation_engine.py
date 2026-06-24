
def generate_timeline(severity):

    if severity == "High":
        return [
            "Day 1 - Apply treatment immediately",
            "Day 7 - Repeat spray",
            "Day 14 - Inspect infected areas",
            "Day 21 - Monitor recovery"
        ]

    elif severity == "Medium":
        return [
            "Day 1 - Begin treatment",
            "Day 7 - Check disease spread",
            "Day 14 - Reinspect crop",
            "Day 21 - Expected recovery"
        ]

    else:
        return [
            "Day 1 - Preventive spray",
            "Day 14 - Monitor plant health",
            "Day 21 - Continue prevention"
        ]
def generate_recommendation(disease, severity, confidence):

    if severity == "High":
        urgency = "Immediate Action Required"
        action = (
            "Remove infected leaves immediately. "
            "Apply recommended fungicide within 24 hours."
        )

    elif severity == "Medium":
        urgency = "Monitor Closely"
        action = (
            "Start treatment and inspect plants daily."
        )

    else:
        urgency = "Preventive Action"
        action = (
            "Continue monitoring and maintain good crop hygiene."
        )

    # Confidence Analysis
    if confidence < 70:
        confidence_note = (
            "Prediction confidence is low. "
            "Please verify the disease manually or consult an expert."
        )

    elif confidence < 90:
        confidence_note = (
            "Prediction confidence is moderate. "
            "Monitor the crop carefully before taking major action."
        )

    else:
        confidence_note = (
            "Prediction confidence is high. "
            "The diagnosis is likely accurate."
        )

    crop_loss = {
    "Low": "0-10%",
    "Medium": "10-30%",
    "High": "30-70%"
    }
    timeline = generate_timeline(severity)
    return {
    "urgency": urgency,
    "action": action,
    "confidence_note": confidence_note,
    "crop_loss": crop_loss.get(severity, "Unknown"),
    "timeline": timeline
}