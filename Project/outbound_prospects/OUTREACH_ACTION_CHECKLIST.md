# Parla Outbound Outreach Action Checklist

Your local email dispatcher engine [`Scripts/send_email_outreach.py`](file:///c:/Users/james/VuZiNat/iot_agent/Scripts/send_email_outreach.py) is completely built and ready to send.

---

### To trigger immediate email dispatch right now:

1. Open a **Free Resend Account** at [https://resend.com](https://resend.com) (takes 30 seconds via GitHub/email login).
2. Copy your API key (looks like `re_123456789...`).
3. In your terminal, run:

```powershell
$env:RESEND_API_KEY = "re_your_api_key_here"
.\.venv\Scripts\python.exe Scripts/send_email_outreach.py
```

---

### Alternative: Instant Manual Pitch Dispatch (< 2 Minutes)
If you prefer not to sign up for an API key right now, simply copy any of the prepared pitch files below and paste them into your email client or LinkedIn:

- [`pitch_01_singamas_petroleum.txt`](file:///c:/Users/james/VuZiNat/iot_agent/Project/outbound_prospects/singapore_pitches/pitch_01_singamas_petroleum.txt)
- [`pitch_02_chemoil_international.txt`](file:///c:/Users/james/VuZiNat/iot_agent/Project/outbound_prospects/singapore_pitches/pitch_02_chemoil_international.txt)
- [`pitch_03_fratelli_cosulich.txt`](file:///c:/Users/james/VuZiNat/iot_agent/Project/outbound_prospects/singapore_pitches/pitch_03_fratelli_cosulich.txt)
- [`pitch_04_equatorial_marine.txt`](file:///c:/Users/james/VuZiNat/iot_agent/Project/outbound_prospects/singapore_pitches/pitch_04_equatorial_marine.txt)
- [`pitch_05_bmt_asia_pacific.txt`](file:///c:/Users/james/VuZiNat/iot_agent/Project/outbound_prospects/singapore_pitches/pitch_05_bmt_asia_pacific.txt)
