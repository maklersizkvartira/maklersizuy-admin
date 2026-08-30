import re

with open('admin-frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update API_BASE and remove API_BASE_URL
content = re.sub(
    r"const API_BASE_URL = '[^']+';",
    "",
    content
)
content = re.sub(
    r"const API_BASE = [^;]+;",
    "const API_BASE = '/api/v1';",
    content
)

# 2. Simplify URLs
content = content.replace('${API_BASE_URL}/', '${API_BASE}/')
content = content.replace('${API_BASE}/api/v1/', '${API_BASE}/')
content = content.replace('${API_BASE}/api/auth/', '${API_BASE}/auth/')
content = content.replace('${API_BASE}/api/listings', '${API_BASE}/listings')
content = content.replace('${API_BASE}/api/users', '${API_BASE}/users')

# Let's fix potential double slashes like `${API_BASE}//` -> `${API_BASE}/` just in case
content = content.replace('${API_BASE}//', '${API_BASE}/')

with open('admin-frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html successfully")
