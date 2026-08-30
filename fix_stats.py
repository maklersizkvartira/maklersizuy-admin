with open('admin-frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('fetch(`${API_BASE}/stats`', 'fetch(`${API_BASE}/admin/dashboard/stats`')
content = content.replace("fetch(`${API_BASE}/dashboard/stats`", "fetch(`${API_BASE}/admin/dashboard/stats`")

with open('admin-frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
