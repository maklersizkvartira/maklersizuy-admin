with open('admin-frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix unblock
content = content.replace("""const res = await fetch(`${API_BASE}/admin/listings/${id}/unblock`, {
                        method: 'POST',
                        headers: getAuthHeaders({ 'Content-Type': 'application/json' })
                    });""", """const res = await fetch(`${API_BASE}/listings/${id}/status`, {
                        method: 'PATCH',
                        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
                        body: JSON.stringify({ status: 'APPROVED' })
                    });""")

content = content.replace("""const resLocal = await fetch(`${API_BASE}/admin/listings/${id}/unblock`, {
                        method: 'POST',
                        headers: getAuthHeaders({ 'Content-Type': 'application/json' })
                    });""", """const resLocal = await fetch(`${API_BASE}/listings/${id}/status`, {
                        method: 'PATCH',
                        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
                        body: JSON.stringify({ status: 'APPROVED' })
                    });""")

# Fix reject
content = content.replace("""const res = await fetch(`${API_BASE}/admin/listings/${id}/reject`, {
                        method: 'POST',
                        headers: getAuthHeaders({ 'Content-Type': 'application/json' })
                    });""", """const res = await fetch(`${API_BASE}/listings/${id}/status`, {
                        method: 'PATCH',
                        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
                        body: JSON.stringify({ status: 'REJECTED' })
                    });""")

content = content.replace("""const resLocal = await fetch(`${API_BASE}/admin/listings/${id}/reject`, {
                        method: 'POST',
                        headers: getAuthHeaders({ 'Content-Type': 'application/json' })
                    });""", """const resLocal = await fetch(`${API_BASE}/listings/${id}/status`, {
                        method: 'PATCH',
                        headers: getAuthHeaders({ 'Content-Type': 'application/json' }),
                        body: JSON.stringify({ status: 'REJECTED' })
                    });""")

# Fix delete
content = content.replace("fetch(`${API_BASE}/admin/listings/${id}`", "fetch(`${API_BASE}/listings/${id}`")

with open('admin-frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
