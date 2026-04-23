OPERATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>ForensiWipe Report</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f172a; color:#e2e8f0; padding:20px; }
    .card { background:#1e293b; border-radius:8px; padding:16px; margin-bottom:14px; }
    .warn { color:#facc15; }
    .err { color:#f87171; }
  </style>
</head>
<body>
  <h1>ForensiWipe Operation Report</h1>
  <div class="card">
    <p><b>Operation ID:</b> {{ operation_id }}</p>
    <p><b>Case ID:</b> {{ case_id }}</p>
    <p><b>Operator:</b> {{ operator }}</p>
    <p><b>Target:</b> {{ target }}</p>
    <p><b>Target Type:</b> {{ target_type }}</p>
    <p><b>File System:</b> {{ filesystem }}</p>
    <p><b>Method:</b> {{ method }} (passes={{ passes }})</p>
    <p><b>Metadata Handling Mode:</b> {{ metadata_mode }}</p>
    <p><b>Metadata Summary:</b> {{ metadata_summary }}</p>
    <p><b>Metadata Actions:</b>
      rename_rounds={{ metadata_actions.rename_rounds }},
      truncate={{ metadata_actions.truncate }},
      sha256_pre_wipe={{ metadata_actions.sha256_pre_wipe }}
    </p>
    <p><b>Status:</b> {{ status }} | <b>Verification:</b> {{ verification }}</p>
    <p><b>Bytes Processed:</b> {{ bytes_processed }}</p>
    <p><b>Start:</b> {{ started_at }} | <b>End:</b> {{ ended_at }}</p>
  </div>
  <div class="card">
    <h3>Warnings</h3>
    <ul>{% for w in warnings %}<li class="warn">{{ w }}</li>{% endfor %}</ul>
  </div>
  <div class="card">
    <h3>Forensic Notes</h3>
    <ul>{% for n in forensic_notes %}<li>{{ n }}</li>{% endfor %}</ul>
  </div>
  <div class="card">
    <h3>Errors</h3>
    <ul>{% for e in errors %}<li class="err">{{ e }}</li>{% endfor %}</ul>
  </div>
</body>
</html>
"""