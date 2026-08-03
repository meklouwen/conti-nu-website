// Vercel serverless function: verstuurt de quickscan-uitslag per e-mail via Flowmailer
// en een lead-notificatie naar Conti-nu. Credentials via Vercel-omgevingsvariabelen:
//   FLOWMAILER_CLIENT_ID, FLOWMAILER_CLIENT_SECRET, FLOWMAILER_ACCOUNT_ID
//   FLOWMAILER_SENDER        (bijv. noreply@conti-nu.nl — moet geldig afzenderdomein zijn in Flowmailer)
//   FLOWMAILER_SENDER_NAME   (optioneel, standaard "Conti-nu Bedrijfsondersteuning")
//   QUICKSCAN_NOTIFY         (optioneel, standaard info@conti-nu.nl)

const FM_TOKEN_URL = "https://login.flowmailer.net/oauth/token";
const FM_API_BASE = "https://api.flowmailer.net";
const FM_CONTENT_TYPE = "application/vnd.flowmailer.v1.12+json";

const TYPE_LABELS = { ggz: "GGZ", jeugd: "Jeugdhulp", both: "GGZ én jeugdhulp" };

function esc(s) {
  return String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

function validate(body) {
  if (!body || typeof body !== "object") return null;
  if (body.website) return null; // honeypot: bots vullen dit verborgen veld in
  const email = String(body.email || "").trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 254) return null;
  const name = String(body.name || "").trim().slice(0, 120);
  const practiceType = TYPE_LABELS[body.practiceType] ? String(body.practiceType) : null;
  const verdictTitle = String(body.verdictTitle || "").trim().slice(0, 200);
  if (!Array.isArray(body.categories) || body.categories.length < 1 || body.categories.length > 6) return null;
  const categories = body.categories.map(function (c) {
    return {
      name: String((c && c.name) || "").trim().slice(0, 80),
      pct: Math.max(0, Math.min(100, parseInt((c && c.pct) || 0, 10) || 0)),
      label: String((c && c.label) || "").trim().slice(0, 40),
    };
  });
  if (categories.some(function (c) { return !c.name; })) return null;
  return { email: email, name: name, practiceType: practiceType, verdictTitle: verdictTitle, categories: categories };
}

async function getToken(clientId, clientSecret) {
  const res = await fetch(FM_TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      grant_type: "client_credentials",
      scope: "api",
    }),
  });
  if (!res.ok) throw new Error("Flowmailer-token mislukt: " + res.status);
  const data = await res.json();
  if (!data.access_token) throw new Error("Flowmailer-token zonder access_token");
  return data.access_token;
}

async function submitMessage(token, accountId, message) {
  const res = await fetch(FM_API_BASE + "/" + accountId + "/messages/submit", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": FM_CONTENT_TYPE,
      Accept: FM_CONTENT_TYPE,
    },
    body: JSON.stringify(Object.assign({ messageType: "EMAIL" }, message)),
  });
  if (res.status !== 201) {
    const text = await res.text().catch(function () { return ""; });
    throw new Error("Flowmailer-submit mislukt: " + res.status + " " + text.slice(0, 300));
  }
}

function scoreRows(categories) {
  return categories.map(function (c) {
    return (
      '<tr><td style="padding:6px 14px 6px 0;color:#3D1A00;font-weight:600;">' + esc(c.name) + "</td>" +
      '<td style="padding:6px 14px 6px 0;color:#6E4A2E;">' + esc(c.label) + "</td>" +
      '<td style="padding:6px 0;color:#6E4A2E;text-align:right;">' + c.pct + "%</td></tr>"
    );
  }).join("");
}

function resultMailHtml(d) {
  const aanhef = d.name ? "Beste " + esc(d.name) : "Beste";
  return (
    '<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;margin:0 auto;color:#3D1A00;">' +
    '<h2 style="font-weight:600;">Uw quickscan-uitslag</h2>' +
    "<p>" + aanhef + ",</p>" +
    "<p>Bedankt voor het invullen van de quickscan zorgadministratie" +
    (d.practiceType ? " voor uw praktijk (" + esc(TYPE_LABELS[d.practiceType]) + ")" : "") + ". Dit is uw uitslag:</p>" +
    (d.verdictTitle ? '<p style="font-size:17px;font-weight:600;color:#C25A1A;">' + esc(d.verdictTitle) + "</p>" : "") +
    '<table style="border-collapse:collapse;width:100%;margin:12px 0 20px;">' + scoreRows(d.categories) + "</table>" +
    "<p>Wilt u weten hoe dit zich voor uw praktijk concreet vertaalt naar rust en tijd? " +
    "Wij denken graag vrijblijvend met u mee.</p>" +
    '<p><a href="mailto:info@conti-nu.nl?subject=' + encodeURIComponent("Vrijblijvend adviesgesprek naar aanleiding van quickscan") + '" ' +
    'style="display:inline-block;background:#E8722A;color:#FFFDF8;text-decoration:none;border-radius:8px;padding:12px 20px;font-weight:600;">Plan een vrijblijvend gesprek</a></p>' +
    '<p style="color:#6E4A2E;font-size:13px;margin-top:28px;">Conti-nu Bedrijfsondersteuning &middot; info@conti-nu.nl &middot; 06-488 70 577<br>' +
    "U ontvangt deze e-mail eenmalig omdat u de quickscan op conti-nu.nl heeft ingevuld.</p>" +
    "</div>"
  );
}

function resultMailText(d) {
  const lines = d.categories.map(function (c) { return "- " + c.name + ": " + c.label + " (" + c.pct + "%)"; });
  return (
    (d.name ? "Beste " + d.name : "Beste") + ",\n\n" +
    "Bedankt voor het invullen van de quickscan zorgadministratie. Dit is uw uitslag:\n\n" +
    (d.verdictTitle ? d.verdictTitle + "\n\n" : "") +
    lines.join("\n") + "\n\n" +
    "Wilt u weten hoe dit zich voor uw praktijk concreet vertaalt naar rust en tijd?\n" +
    "Mail ons via info@conti-nu.nl of bel 06-488 70 577.\n\n" +
    "Conti-nu Bedrijfsondersteuning\n"
  );
}

function notifyMailHtml(d) {
  return (
    '<div style="font-family:Arial,Helvetica,sans-serif;max-width:560px;color:#3D1A00;">' +
    "<h3>Nieuwe quickscan-invulling op conti-nu.nl</h3>" +
    "<p><strong>E-mail:</strong> " + esc(d.email) + "<br>" +
    (d.name ? "<strong>Naam:</strong> " + esc(d.name) + "<br>" : "") +
    (d.practiceType ? "<strong>Praktijktype:</strong> " + esc(TYPE_LABELS[d.practiceType]) + "<br>" : "") +
    (d.verdictTitle ? "<strong>Uitslag:</strong> " + esc(d.verdictTitle) : "") + "</p>" +
    '<table style="border-collapse:collapse;">' + scoreRows(d.categories) + "</table>" +
    "</div>"
  );
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, reason: "method_not_allowed" });
  }

  const clientId = process.env.FLOWMAILER_CLIENT_ID;
  const clientSecret = process.env.FLOWMAILER_CLIENT_SECRET;
  const accountId = process.env.FLOWMAILER_ACCOUNT_ID;
  const sender = process.env.FLOWMAILER_SENDER;
  if (!clientId || !clientSecret || !accountId || !sender) {
    return res.status(503).json({ ok: false, reason: "not_configured" });
  }
  const senderName = process.env.FLOWMAILER_SENDER_NAME || "Conti-nu Bedrijfsondersteuning";
  const notify = process.env.QUICKSCAN_NOTIFY || "info@conti-nu.nl";

  const data = validate(req.body);
  if (!data) return res.status(400).json({ ok: false, reason: "invalid_input" });

  try {
    const token = await getToken(clientId, clientSecret);

    // 1) Uitslag naar de invuller
    await submitMessage(token, accountId, {
      senderAddress: sender,
      headerFromAddress: sender,
      headerFromName: senderName,
      recipientAddress: data.email,
      headerToAddress: data.email,
      subject: "Uw quickscan-uitslag — Conti-nu",
      html: resultMailHtml(data),
      text: resultMailText(data),
    });

    // 2) Lead-notificatie naar Conti-nu (mag de invuller-mail niet blokkeren)
    try {
      await submitMessage(token, accountId, {
        senderAddress: sender,
        headerFromAddress: sender,
        headerFromName: "Quickscan conti-nu.nl",
        recipientAddress: notify,
        headerToAddress: notify,
        subject: "Nieuwe quickscan-invulling: " + data.email,
        html: notifyMailHtml(data),
      });
    } catch (e) {
      console.error("quickscan-notificatie mislukt:", e && e.message);
    }

    return res.status(200).json({ ok: true });
  } catch (e) {
    console.error("quickscan-mail fout:", e && e.message);
    return res.status(502).json({ ok: false, reason: "send_failed" });
  }
}
